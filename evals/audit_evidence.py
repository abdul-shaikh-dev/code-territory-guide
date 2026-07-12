from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EVAL_ROOT.parent
RESULT_ROOT = EVAL_ROOT / "results"
ROUTING = json.loads((EVAL_ROOT / "model-routing.json").read_text(encoding="utf-8"))
CODEX = shutil.which("codex.cmd") or shutil.which("codex")
REPORT = RESULT_ROOT / "2026-07-12-recorded-matrix.md"
FINAL = RESULT_ROOT / "2026-07-12-recorded-matrix-audit.md"
RAW = RESULT_ROOT / "2026-07-12-recorded-matrix-audit.jsonl"
STDERR = RESULT_ROOT / "2026-07-12-recorded-matrix-audit.stderr.txt"
RECORD = RESULT_ROOT / "2026-07-12-recorded-matrix-audit.record.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    if CODEX is None:
        raise SystemExit("codex launcher not found on PATH")
    if RECORD.exists():
        raise SystemExit(f"refusing to overwrite preserved audit: {RECORD}")
    route = ROUTING["audit"]
    prompt = """Act as an independent adversarial auditor of a behavioral-evaluation evidence package.

Audit only these paths under evals/:
- manifest.json, model-routing.json, exclusion-policy.md, README.md
- run-record.schema.json, judge-output.schema.json
- run_matrix.py, judge_matrix.py, build_report.py
- results/runs/*.json
- results/judgments/*
- results/2026-07-12-recorded-matrix.md

Do not read the skill implementation or the older smoke/full/audit reports. Do not assume the new report is correct. Verify its counts and material claims against the raw records and structured judgments. Check provenance, exact prompts, fixture hashes, model/reasoning metadata, baseline/treatment separation, run selection, exclusions, judge independence, rubric completeness, pass-field consistency, raw-output preservation, retry preservation, contamination or skill-text leakage, and whether the harness actually exercises the behaviors claimed. Treat omitted evidence as absent. Distinguish a failure of the skill from a failure or limitation of the harness.

Write a concise Markdown audit containing:
1. Verdict: PASS, QUALIFIED, or FAIL for whether the report's stated claims are supported.
2. Findings ordered by severity, each citing concrete relative file paths and record IDs.
3. Verified counts.
4. Claims supported and claims not supported.
5. Required next actions.

Do not edit files or run model sessions. Your final response is the audit document only."""
    started = now()
    run_dir = Path(tempfile.mkdtemp(prefix="ctg-evidence-audit-"))
    command = [
        CODEX, "exec", "--ephemeral", "--json", "--color", "never",
        "--sandbox", "read-only", "--skip-git-repo-check", "-C", str(REPO_ROOT),
        "-m", route["model"], "-c", f'model_reasoning_effort="{route["reasoning_effort"]}"',
        "-o", str(FINAL), "-",
    ]
    completed = subprocess.run(
        command, input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=600,
    )
    finished = now()
    RAW.write_text(completed.stdout, encoding="utf-8")
    STDERR.write_text(completed.stderr, encoding="utf-8")
    valid = completed.returncode == 0 and FINAL.is_file() and FINAL.stat().st_size > 0
    record = {
        "audit_run_id": "recorded-matrix-audit--attempt-1",
        "started_at": started,
        "finished_at": finished,
        "model": route["model"],
        "reasoning_effort": route["reasoning_effort"],
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "input_report": str(REPORT.relative_to(EVAL_ROOT)),
        "raw_output": str(RAW.relative_to(EVAL_ROOT)),
        "stderr": str(STDERR.relative_to(EVAL_ROOT)),
        "final_output": str(FINAL.relative_to(EVAL_ROOT)) if FINAL.exists() else None,
        "exit_status": completed.returncode,
        "excluded": {"value": not valid, "rule": None if valid else "audit did not produce a successful non-empty final output"},
    }
    RECORD.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.rmtree(run_dir, ignore_errors=True)
    print(f"audit exit={completed.returncode} valid={valid} record={RECORD}")


if __name__ == "__main__":
    main()
