from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from freeze_evaluation import lock_sha256, validate_current_lock
from judge_matrix import build_prompt, normalize_judgment, validate_judgment


EVAL_ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((EVAL_ROOT / "real-repo-manifest.json").read_text(encoding="utf-8"))
RUN_ROOT = EVAL_ROOT / "results" / "real-repos" / "runs"
RESULT_ROOT = EVAL_ROOT / "results" / "real-repos" / "judgments"
SCHEMA = EVAL_ROOT / "judge-blind-output.schema.json"
CODEX = shutil.which("codex.cmd") or shutil.which("codex")
AUTH_SOURCE = Path.home() / ".codex" / "auth.json"
ROUTING = json.loads((EVAL_ROOT / "model-routing.json").read_text(encoding="utf-8"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_run(case_id: str, arm: str, attempt: int, expected_lock: str) -> dict:
    path = RUN_ROOT / f"{case_id}--{arm}--attempt-{attempt}.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    if record["excluded"]["value"]:
        raise RuntimeError(f"excluded input run: {path}: {record['excluded']['rule']}")
    if record.get("evaluation_lock", {}).get("sha256") != expected_lock:
        raise RuntimeError(f"input run is not preregistered by the active lock: {path}")
    return record


def judge_pair(
    case: dict,
    baseline_attempt: int,
    treatment_attempt: int,
    judge_attempt: int,
    evaluation_lock: dict,
) -> Path:
    expected_lock = lock_sha256(evaluation_lock)
    baseline = load_run(case["id"], "baseline", baseline_attempt, expected_lock)
    treatment = load_run(case["id"], "installed-skill", treatment_attempt, expected_lock)
    route = ROUTING["judge_by_source_model"].get(treatment["model"])
    if route is None or route["model"] == treatment["model"]:
        raise ValueError(f"no independent judge model for {treatment['model']}")
    baseline_view = {**baseline, "tool_events": baseline["events"]}
    treatment_view = {**treatment, "tool_events": treatment["events"]}
    prompt, assignment = build_prompt(case, baseline_view, treatment_view)
    stem = f"{case['id']}--judge-attempt-{judge_attempt}"
    record_path = RESULT_ROOT / f"{stem}.json"
    raw_path = RESULT_ROOT / f"{stem}.jsonl"
    stderr_path = RESULT_ROOT / f"{stem}.stderr.txt"
    final_path = RESULT_ROOT / f"{stem}.output.json"
    if record_path.exists():
        raise RuntimeError(f"refusing to overwrite {record_path}")
    work = Path(tempfile.mkdtemp(prefix=f"ctg-real-judge-{case['id']}-"))
    judge_home = work / "home"
    judge_codex_home = judge_home / ".codex"
    judge_codex_home.mkdir(parents=True)
    shutil.copy2(AUTH_SOURCE, judge_codex_home / "auth.json")
    inherited = ("PATH", "SystemRoot", "WINDIR", "ComSpec", "PATHEXT")
    env = {key: os.environ[key] for key in inherited if key in os.environ}
    env.update({"CODEX_HOME": str(judge_codex_home), "HOME": str(judge_home), "USERPROFILE": str(judge_home)})
    command = [
        CODEX, "exec", "--ephemeral", "--json", "--color", "never", "--sandbox", "read-only",
        "--skip-git-repo-check", "-C", str(work), "-m", route["model"],
        "-c", f'model_reasoning_effort="{route["reasoning_effort"]}"',
        "--output-schema", str(SCHEMA), "-o", str(final_path), "-",
    ]
    started = now()
    completed = subprocess.run(
        command, input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=480, env=env,
    )
    finished = now()
    raw_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    judgment = None
    error = None
    try:
        if completed.returncode != 0:
            raise RuntimeError(f"judge exited {completed.returncode}")
        blind = json.loads(final_path.read_text(encoding="utf-8"))
        judgment = normalize_judgment(blind, assignment, baseline, treatment)
        validate_judgment(case, baseline, treatment, judgment)
    except Exception as exc:
        error = str(exc)
    record = {
        "judge_run_id": stem, "case_id": case["id"], "started_at": started, "finished_at": finished,
        "model": route["model"], "reasoning_effort": route["reasoning_effort"], "prompt": prompt,
        "blinding": {
            "enabled": True,
            "assignment": assignment,
            "source_model": treatment["model"],
            "judge_model_is_independent": route["model"] != treatment["model"],
        },
        "evaluation_lock": {
            "release_id": evaluation_lock["release_id"],
            "sha256": expected_lock,
            "preregistered": True,
        },
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "input_runs": [baseline["run_id"], treatment["run_id"]],
        "raw_output": str(raw_path.relative_to(EVAL_ROOT)), "stderr": str(stderr_path.relative_to(EVAL_ROOT)),
        "exit_status": completed.returncode, "excluded": {"value": error is not None, "rule": error},
        "judgment": judgment,
    }
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    return record_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-attempt", type=int, default=1)
    parser.add_argument("--treatment-attempt", type=int, default=1)
    parser.add_argument("--judge-attempt", type=int, default=1)
    parser.add_argument("--case")
    args = parser.parse_args()
    if CODEX is None or not AUTH_SOURCE.is_file():
        raise SystemExit("Codex launcher or auth file unavailable")
    try:
        evaluation_lock = validate_current_lock()
    except ValueError as error:
        raise SystemExit(f"evaluation lock rejected before model execution: {error}") from error
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    cases = [case for case in MANIFEST["cases"] if not args.case or case["id"] == args.case]
    if not cases:
        raise SystemExit(f"unknown case: {args.case}")
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(
                judge_pair,
                case,
                args.baseline_attempt,
                args.treatment_attempt,
                args.judge_attempt,
                evaluation_lock,
            ): case["id"]
            for case in cases
        }
        for future in as_completed(futures):
            print(f"judged {futures[future]} -> {future.result()}", flush=True)


if __name__ == "__main__":
    main()
