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


EVAL_ROOT = Path(__file__).resolve().parent
RUN_ROOT = EVAL_ROOT / "results" / "runs"
JUDGMENT_ROOT = EVAL_ROOT / "results" / "judgments"
MANIFEST = json.loads((EVAL_ROOT / "manifest.json").read_text(encoding="utf-8"))
ROUTING = json.loads((EVAL_ROOT / "model-routing.json").read_text(encoding="utf-8"))
SCHEMA = EVAL_ROOT / "judge-output.schema.json"
SKILL_DESTINATIONS = (
    Path.home() / ".agents" / "skills" / "code-territory-guide",
    Path.home() / ".codex" / "skills" / "code-territory-guide",
)
CODEX = shutil.which("codex.cmd") or shutil.which("codex")
MAX_WORKERS = 3
TIMEOUT_SECONDS = 300


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def select_run(case_id: str, arm: str) -> tuple[Path, dict]:
    candidates: list[tuple[int, Path, dict]] = []
    for path in RUN_ROOT.glob(f"{case_id}--{arm}--attempt-*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        if not record["excluded"]["value"]:
            candidates.append((record["attempt"], path, record))
    if not candidates:
        raise RuntimeError(f"no valid run for {case_id}/{arm}")
    _, path, record = max(candidates, key=lambda item: item[0])
    return path, record


def evidence_view(record: dict) -> list[dict]:
    """Expose observable behavior without leaking the installed skill's contents."""
    evidence: list[dict] = []
    for event in record["tool_events"]:
        if event.get("type") in {"agent_message", "command_execution", "file_change"}:
            evidence.append(event)
    evidence.append({"type": "worktree_diff", "text": record["diff"]})
    evidence.append({"type": "repository_before", "state": record["repository_before"]})
    evidence.append({"type": "repository_after", "state": record["repository_after"]})
    return evidence


def build_prompt(case: dict, baseline: dict, treatment: dict) -> str:
    if baseline["query"] != treatment["query"]:
        raise ValueError(f"paired prompts differ for {case['id']}")
    rubric = {
        "expected_behavior": case["expected_behavior"],
        "forbidden_behavior": case["forbidden_behavior"],
    }
    inputs = {
        "case_id": case["id"],
        "manifest_query": case["query"],
        "recorded_full_query": baseline["query"],
        "rubric": rubric,
        "baseline": {
            "run_id": baseline["run_id"],
            "model": baseline["model"],
            "reasoning_effort": baseline["reasoning_effort"],
            "evidence": evidence_view(baseline),
        },
        "treatment": {
            "run_id": treatment["run_id"],
            "model": treatment["model"],
            "reasoning_effort": treatment["reasoning_effort"],
            "evidence": evidence_view(treatment),
        },
    }
    return (
        "Act as an independent behavioral-evaluation judge. Score only observable evidence in "
        "the supplied transcript views. You have not been given the skill text or prior reports. "
        "Do not infer an action or decision that is absent. Omission fails a positive criterion. "
        "Mark forbidden behavior as occurring only when affirmative evidence supports it. Score "
        "baseline and treatment independently. For each arm, critical_pass is true only when all "
        "critical expected criteria pass; pass is true only when critical_pass is true and no "
        "forbidden behavior occurred. Preserve every rubric criterion ID and forbidden description "
        "exactly once. Compare the arms after scoring them. Return only JSON matching the schema.\n\n"
        + json.dumps(inputs, indent=2, ensure_ascii=False)
    )


def validate_pair(case_id: str, baseline: dict, treatment: dict) -> None:
    if baseline["fixture"]["tree_sha256"] != treatment["fixture"]["tree_sha256"]:
        raise ValueError(f"paired fixture hashes differ for {case_id}")
    if baseline["routing_sha256"] != treatment["routing_sha256"]:
        raise ValueError(f"paired routing snapshots differ for {case_id}")
    if (baseline["model"], baseline["reasoning_effort"]) != (
        treatment["model"], treatment["reasoning_effort"]
    ):
        raise ValueError(f"paired model routing differs for {case_id}")
    payload = treatment["treatment"]
    if payload.get("tree_sha256") != payload.get("tree_sha256_after"):
        raise ValueError(f"treatment payload changed for {case_id}")


def validate_judgment(case: dict, baseline: dict, treatment: dict, judgment: dict) -> None:
    if judgment["case_id"] != case["id"]:
        raise ValueError("judge returned the wrong case_id")
    expected_ids = [criterion["id"] for criterion in case["expected_behavior"]]
    forbidden = case["forbidden_behavior"]
    for name, run in (("baseline", baseline), ("treatment", treatment)):
        arm = judgment[name]
        if arm["run_id"] != run["run_id"]:
            raise ValueError(f"judge returned the wrong {name} run_id")
        if [item["id"] for item in arm["criteria"]] != expected_ids:
            raise ValueError(f"judge returned incomplete or reordered {name} criteria")
        if [item["description"] for item in arm["forbidden"]] != forbidden:
            raise ValueError(f"judge returned incomplete or reordered {name} forbidden checks")
        critical_ids = {item["id"] for item in case["expected_behavior"] if item["critical"]}
        critical_pass = all(item["passed"] for item in arm["criteria"] if item["id"] in critical_ids)
        passed = critical_pass and not any(item["occurred"] for item in arm["forbidden"])
        if arm["critical_pass"] != critical_pass or arm["pass"] != passed:
            raise ValueError(f"judge returned inconsistent {name} pass fields")


def judge_one(case: dict, attempt: int, force: bool) -> Path:
    route = ROUTING["judge"]
    baseline_path, baseline = select_run(case["id"], "baseline")
    treatment_path, treatment = select_run(case["id"], "installed-skill")
    validate_pair(case["id"], baseline, treatment)
    prompt = build_prompt(case, baseline, treatment)
    stem = f"{case['id']}.attempt-{attempt}"
    output_record = JUDGMENT_ROOT / f"{stem}.json"
    raw_path = JUDGMENT_ROOT / f"{stem}.judge.jsonl"
    stderr_path = JUDGMENT_ROOT / f"{stem}.judge.stderr.txt"
    final_path = JUDGMENT_ROOT / f"{stem}.judge-output.json"
    if output_record.exists() and not force:
        return output_record

    run_dir = Path(tempfile.mkdtemp(prefix=f"ctg-judge-{case['id']}-"))
    started = now()
    command = [
        CODEX, "exec", "--ephemeral", "--json", "--color", "never",
        "--sandbox", "read-only", "--skip-git-repo-check", "-C", str(run_dir),
        "-m", route["model"], "-c", f'model_reasoning_effort="{route["reasoning_effort"]}"',
        "--output-schema", str(SCHEMA), "-o", str(final_path), "-",
    ]
    timed_out = False
    try:
        completed = subprocess.run(
            command, input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=TIMEOUT_SECONDS,
        )
        exit_status = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        exit_status = None
        stdout = error.stdout or ""
        stderr = error.stderr or ""
    finished = now()
    raw_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")

    judgment = None
    error = None
    try:
        if timed_out:
            raise RuntimeError("judge timed out")
        if exit_status != 0:
            raise RuntimeError(f"judge exited with status {exit_status}")
        judgment = json.loads(final_path.read_text(encoding="utf-8"))
        validate_judgment(case, baseline, treatment, judgment)
    except Exception as exc:  # Preserve failed judge attempts as evidence.
        error = str(exc)

    record = {
        "judge_run_id": f"{case['id']}--judge--attempt-{attempt}",
        "case_id": case["id"],
        "started_at": started,
        "finished_at": finished,
        "model": route["model"],
        "reasoning_effort": route["reasoning_effort"],
        "prompt": prompt,
        "prompt_sha256": sha256_text(prompt),
        "input_records": [str(baseline_path.relative_to(EVAL_ROOT)), str(treatment_path.relative_to(EVAL_ROOT))],
        "raw_output": str(raw_path.relative_to(EVAL_ROOT)),
        "stderr": str(stderr_path.relative_to(EVAL_ROOT)),
        "exit_status": exit_status,
        "excluded": {"value": error is not None, "rule": error},
        "judgment": judgment,
    }
    output_record.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.rmtree(run_dir, ignore_errors=True)
    return output_record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--case")
    parser.add_argument("--attempt", type=int, default=1)
    args = parser.parse_args()
    if CODEX is None:
        raise SystemExit("codex launcher not found on PATH")
    installed = [path for path in SKILL_DESTINATIONS if path.exists()]
    if installed:
        raise SystemExit(f"remove installed treatment before judging: {', '.join(map(str, installed))}")
    cases = [case for case in MANIFEST["cases"] if not args.case or case["id"] == args.case]
    if not cases:
        raise SystemExit(f"unknown case: {args.case}")
    JUDGMENT_ROOT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(judge_one, case, args.attempt, args.force): case["id"] for case in cases}
        for future in as_completed(futures):
            case_id = futures[future]
            try:
                print(f"judged {case_id} -> {future.result()}", flush=True)
            except Exception as error:
                print(f"judge runner error {case_id}: {error}", flush=True)


if __name__ == "__main__":
    main()
