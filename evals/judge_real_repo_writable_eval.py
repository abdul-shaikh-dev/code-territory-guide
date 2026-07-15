from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from freeze_evaluation import lock_sha256, validate_lock
from judge_matrix import build_prompt, normalize_judgment, validate_judgment


EVAL_ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads(
    (EVAL_ROOT / "real-repo-writable-manifest.json").read_text(encoding="utf-8")
)
RUN_ROOT = EVAL_ROOT / "results" / "real-repos-writable" / "runs"
RESULT_ROOT = EVAL_ROOT / "results" / "real-repos-writable" / "judgments"
SCHEMA = EVAL_ROOT / "judge-blind-output.schema.json"
ROUTING = json.loads(
    (EVAL_ROOT / "model-routing.json").read_text(encoding="utf-8")
)
AUTH_SOURCE = Path.home() / ".codex" / "auth.json"
CODEX = shutil.which("codex.cmd") or shutil.which("codex")
TIMEOUT_SECONDS = 480


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_run(case_id: str, arm: str, attempt: int, expected_lock: str) -> tuple[Path, dict]:
    path = RUN_ROOT / f"{case_id}--{arm}--attempt-{attempt}.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    if record["excluded"]["value"]:
        raise RuntimeError(f"excluded input run: {path}: {record['excluded']}")
    if record.get("evaluation_lock", {}).get("sha256") != expected_lock:
        raise RuntimeError(f"input run does not match the active lock: {path}")
    return path, record


def validate_pair(case: dict, baseline: dict, treatment: dict) -> None:
    if baseline["case_id"] != case["id"] or treatment["case_id"] != case["id"]:
        raise ValueError("case identity mismatch")
    if baseline["arm"] != "baseline" or treatment["arm"] != "installed-skill":
        raise ValueError("arm identity mismatch")
    if baseline["attempt"] != treatment["attempt"]:
        raise ValueError("attempt mismatch")
    if baseline["query"] != treatment["query"]:
        raise ValueError("paired prompts differ")
    if baseline["seed"]["head"] != treatment["seed"]["head"]:
        raise ValueError("seed commit mismatch")
    if baseline["seed"]["tree"] != treatment["seed"]["tree"]:
        raise ValueError("seed tree mismatch")
    if (baseline["model"], baseline["reasoning_effort"]) != (
        treatment["model"],
        treatment["reasoning_effort"],
    ):
        raise ValueError("paired model routing mismatch")
    if baseline["execution"]["sandbox"] != "workspace-write":
        raise ValueError("baseline did not use workspace-write")
    if treatment["execution"]["sandbox"] != "workspace-write":
        raise ValueError("treatment did not use workspace-write")
    if baseline["treatment"]["installed"]:
        raise ValueError("baseline contains treatment")
    payload = treatment["treatment"]
    if not payload["installed"]:
        raise ValueError("treatment missing")
    if payload["tree_sha256"] != payload["tree_sha256_after"]:
        raise ValueError("treatment payload changed")


def evidence_record(record: dict) -> dict:
    return {
        **record,
        "tool_events": record["events"],
        "repository_before": record["repository_before"],
        "repository_after": record["repository_after"],
    }


def judge_pair(case: dict, run_attempt: int, judge_attempt: int, lock: dict) -> Path:
    expected_lock = lock_sha256(lock)
    baseline_path, baseline = load_run(
        case["id"], "baseline", run_attempt, expected_lock
    )
    treatment_path, treatment = load_run(
        case["id"], "installed-skill", run_attempt, expected_lock
    )
    validate_pair(case, baseline, treatment)
    route = ROUTING["judge_by_source_model"].get(treatment["model"])
    if route is None or route["model"] == treatment["model"]:
        raise ValueError(f"no independent judge model for {treatment['model']}")
    prompt, assignment = build_prompt(
        case,
        evidence_record(baseline),
        evidence_record(treatment),
    )
    stem = f"{case['id']}--judge-attempt-{judge_attempt}"
    record_path = RESULT_ROOT / f"{stem}.json"
    raw_path = RESULT_ROOT / f"{stem}.jsonl"
    stderr_path = RESULT_ROOT / f"{stem}.stderr.txt"
    final_path = RESULT_ROOT / f"{stem}.output.json"
    if record_path.exists():
        raise RuntimeError(f"refusing to overwrite {record_path}")

    work = Path(tempfile.mkdtemp(prefix=f"ctg-writable-judge-{case['id']}-"))
    judge_home = work / "home"
    codex_home = judge_home / ".codex"
    codex_home.mkdir(parents=True)
    shutil.copy2(AUTH_SOURCE, codex_home / "auth.json")
    inherited = ("PATH", "SystemRoot", "WINDIR", "ComSpec", "PATHEXT")
    env = {key: os.environ[key] for key in inherited if key in os.environ}
    env.update(
        {
            "CODEX_HOME": str(codex_home),
            "HOME": str(judge_home),
            "USERPROFILE": str(judge_home),
        }
    )
    command = [
        CODEX,
        "exec",
        "--ephemeral",
        "--json",
        "--color",
        "never",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "-C",
        str(work),
        "-m",
        route["model"],
        "-c",
        f'model_reasoning_effort="{route["reasoning_effort"]}"',
        "--output-schema",
        str(SCHEMA),
        "-o",
        str(final_path),
        "-",
    ]
    started = now()
    completed = subprocess.run(
        command,
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=TIMEOUT_SECONDS,
        env=env,
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
        "schema_version": 1,
        "judge_run_id": stem,
        "case_id": case["id"],
        "started_at": started,
        "finished_at": finished,
        "model": route["model"],
        "reasoning_effort": route["reasoning_effort"],
        "blinding": {
            "enabled": True,
            "assignment": assignment,
            "source_model": treatment["model"],
            "judge_model_is_independent": route["model"] != treatment["model"],
        },
        "evaluation_lock": {
            "release_id": lock["release_id"],
            "sha256": expected_lock,
            "preregistered": True,
        },
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "input_records": [
            str(baseline_path.relative_to(EVAL_ROOT)),
            str(treatment_path.relative_to(EVAL_ROOT)),
        ],
        "raw_output": str(raw_path.relative_to(EVAL_ROOT)),
        "stderr": str(stderr_path.relative_to(EVAL_ROOT)),
        "exit_status": completed.returncode,
        "excluded": {"value": error is not None, "rule": error},
        "judgment": judgment,
    }
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    record_path.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    shutil.rmtree(work, ignore_errors=True)
    return record_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-attempt", type=int, required=True)
    parser.add_argument("--judge-attempt", type=int, required=True)
    parser.add_argument("--case")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if CODEX is None or not AUTH_SOURCE.is_file():
        raise SystemExit("Codex launcher or auth file unavailable")
    try:
        lock = validate_lock(args.judge_attempt)
    except ValueError as error:
        raise SystemExit(f"evaluation lock rejected before judging: {error}") from error
    cases = [
        case
        for case in MANIFEST["cases"]
        if not args.case or case["id"] == args.case
    ]
    if not cases:
        raise SystemExit(f"unknown case: {args.case}")
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    failures = []
    for case in cases:
        output = RESULT_ROOT / f"{case['id']}--judge-attempt-{args.judge_attempt}.json"
        if output.exists() and args.resume:
            print(f"resume: preserved {output}", flush=True)
            continue
        try:
            path = judge_pair(case, args.run_attempt, args.judge_attempt, lock)
            record = json.loads(path.read_text(encoding="utf-8"))
            print(
                f"judged {case['id']}: excluded={record['excluded']['value']} -> {path}",
                flush=True,
            )
            if record["excluded"]["value"]:
                failures.append((case["id"], record["excluded"]["rule"]))
                break
        except Exception as error:
            failures.append((case["id"], str(error)))
            break
    if failures:
        raise SystemExit(f"writable judging stopped: {failures}")


if __name__ == "__main__":
    main()
