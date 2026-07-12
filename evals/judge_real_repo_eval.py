from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((EVAL_ROOT / "real-repo-manifest.json").read_text(encoding="utf-8"))
RUN_ROOT = EVAL_ROOT / "results" / "real-repos" / "runs"
RESULT_ROOT = EVAL_ROOT / "results" / "real-repos" / "judgments"
SCHEMA = EVAL_ROOT / "judge-output.schema.json"
CODEX = shutil.which("codex.cmd") or shutil.which("codex")


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_run(case_id: str, arm: str, attempt: int) -> dict:
    path = RUN_ROOT / f"{case_id}--{arm}--attempt-{attempt}.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    if record["excluded"]["value"]:
        raise RuntimeError(f"excluded input run: {path}: {record['excluded']['rule']}")
    return record


def build_prompt(case: dict, baseline: dict, treatment: dict) -> str:
    payload = {
        "case_id": case["id"],
        "user_query": case["query"],
        "expected_behavior": case["expected_behavior"],
        "forbidden_behavior": case["forbidden_behavior"],
        "baseline": {
            "run_id": baseline["run_id"], "model": baseline["model"],
            "reasoning_effort": baseline["reasoning_effort"],
            "repository_before": baseline["repository_before"],
            "repository_after": baseline["repository_after"], "events": baseline["events"],
        },
        "treatment": {
            "run_id": treatment["run_id"], "model": treatment["model"],
            "reasoning_effort": treatment["reasoning_effort"],
            "repository_before": treatment["repository_before"],
            "repository_after": treatment["repository_after"], "events": treatment["events"],
        },
    }
    return (
        "Independently judge this paired read-only behavioral evaluation. Score only observable evidence. "
        "Omission fails a positive criterion. Mark forbidden behavior only with affirmative evidence. "
        "Score each arm independently; critical_pass requires every critical criterion, and pass requires "
        "critical_pass plus no forbidden behavior. Preserve criterion IDs and forbidden descriptions exactly "
        "once and in manifest order. Do not reward treatment merely for naming or loading a skill. Return only "
        "schema-conforming JSON.\n\n" + json.dumps(payload, indent=2, ensure_ascii=False)
    )


def validate(case: dict, baseline: dict, treatment: dict, judgment: dict) -> None:
    if judgment["case_id"] != case["id"]:
        raise ValueError("wrong case_id")
    ids = [item["id"] for item in case["expected_behavior"]]
    forbidden = case["forbidden_behavior"]
    critical = {item["id"] for item in case["expected_behavior"] if item["critical"]}
    for name, run in (("baseline", baseline), ("treatment", treatment)):
        arm = judgment[name]
        if arm["run_id"] != run["run_id"]:
            raise ValueError(f"wrong {name} run_id")
        if [item["id"] for item in arm["criteria"]] != ids:
            raise ValueError(f"wrong {name} criteria")
        if [item["description"] for item in arm["forbidden"]] != forbidden:
            raise ValueError(f"wrong {name} forbidden checks")
        critical_pass = all(item["passed"] for item in arm["criteria"] if item["id"] in critical)
        passed = critical_pass and not any(item["occurred"] for item in arm["forbidden"])
        if arm["critical_pass"] != critical_pass or arm["pass"] != passed:
            raise ValueError(f"inconsistent {name} pass fields")


def judge_pair(case: dict, baseline_attempt: int, treatment_attempt: int, judge_attempt: int) -> Path:
    route = MANIFEST["judge"]
    baseline = load_run(case["id"], "baseline", baseline_attempt)
    treatment = load_run(case["id"], "installed-skill", treatment_attempt)
    prompt = build_prompt(case, baseline, treatment)
    stem = f"{case['id']}--judge-attempt-{judge_attempt}"
    record_path = RESULT_ROOT / f"{stem}.json"
    raw_path = RESULT_ROOT / f"{stem}.jsonl"
    stderr_path = RESULT_ROOT / f"{stem}.stderr.txt"
    final_path = RESULT_ROOT / f"{stem}.output.json"
    if record_path.exists():
        raise RuntimeError(f"refusing to overwrite {record_path}")
    work = Path(tempfile.mkdtemp(prefix=f"ctg-real-judge-{case['id']}-"))
    command = [
        CODEX, "exec", "--ephemeral", "--json", "--color", "never", "--sandbox", "read-only",
        "--skip-git-repo-check", "-C", str(work), "-m", route["model"],
        "-c", f'model_reasoning_effort="{route["reasoning_effort"]}"',
        "--output-schema", str(SCHEMA), "-o", str(final_path), "-",
    ]
    started = now()
    completed = subprocess.run(
        command, input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=480,
    )
    finished = now()
    raw_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    judgment = None
    error = None
    try:
        if completed.returncode != 0:
            raise RuntimeError(f"judge exited {completed.returncode}")
        judgment = json.loads(final_path.read_text(encoding="utf-8"))
        validate(case, baseline, treatment, judgment)
    except Exception as exc:
        error = str(exc)
    record = {
        "judge_run_id": stem, "case_id": case["id"], "started_at": started, "finished_at": finished,
        "model": route["model"], "reasoning_effort": route["reasoning_effort"], "prompt": prompt,
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
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    cases = [case for case in MANIFEST["cases"] if not args.case or case["id"] == args.case]
    if not cases:
        raise SystemExit(f"unknown case: {args.case}")
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(judge_pair, case, args.baseline_attempt, args.treatment_attempt, args.judge_attempt): case["id"]
            for case in cases
        }
        for future in as_completed(futures):
            print(f"judged {futures[future]} -> {future.result()}", flush=True)


if __name__ == "__main__":
    main()
