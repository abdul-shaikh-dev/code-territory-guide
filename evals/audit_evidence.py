from __future__ import annotations

import hashlib
import argparse
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from freeze_evaluation import lock_sha256, validate_lock


EVAL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EVAL_ROOT.parent
RESULT_ROOT = EVAL_ROOT / "results"
ROUTING = json.loads((EVAL_ROOT / "model-routing.json").read_text(encoding="utf-8"))
CODEX = shutil.which("codex.cmd") or shutil.which("codex")
AUTH_SOURCE = Path.home() / ".codex" / "auth.json"
REPORT = RESULT_ROOT / "synthetic-evidence.md"
GENERATED = RESULT_ROOT / "generated"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=int, default=1)
    args = parser.parse_args()
    stem = f"synthetic-evidence-audit-attempt-{args.attempt}"
    final = GENERATED / f"{stem}.md"
    raw = GENERATED / f"{stem}.jsonl"
    stderr_path = GENERATED / f"{stem}.stderr.txt"
    record_path = GENERATED / f"{stem}.record.json"
    if CODEX is None or not AUTH_SOURCE.is_file():
        raise SystemExit("Codex launcher or auth file unavailable")
    try:
        evaluation_lock = validate_lock(args.attempt)
    except ValueError as error:
        raise SystemExit(f"evaluation lock rejected before model execution: {error}") from error
    if record_path.exists():
        raise SystemExit(f"refusing to overwrite preserved audit: {record_path}")
    route = ROUTING["audit"]
    prompt = """Act as an independent adversarial auditor of a behavioral-evaluation evidence package.

Audit only these paths under evals/:
- manifest.json, model-routing.json, exclusion-policy.md, README.md
- run-record.schema.json, judge-output.schema.json
- run_matrix.py, judge_matrix.py, build_report.py
- results/runs/*.json
- results/judgments/*
- results/synthetic-evidence.md

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
    audit_home = run_dir / "home"
    audit_codex_home = audit_home / ".codex"
    audit_codex_home.mkdir(parents=True)
    shutil.copy2(AUTH_SOURCE, audit_codex_home / "auth.json")
    inherited = ("PATH", "SystemRoot", "WINDIR", "ComSpec", "PATHEXT")
    env = {key: os.environ[key] for key in inherited if key in os.environ}
    env.update({"CODEX_HOME": str(audit_codex_home), "HOME": str(audit_home), "USERPROFILE": str(audit_home)})
    command = [
        CODEX, "exec", "--ephemeral", "--json", "--color", "never",
        "--sandbox", "read-only", "--skip-git-repo-check", "-C", str(REPO_ROOT),
        "-m", route["model"], "-c", f'model_reasoning_effort="{route["reasoning_effort"]}"',
        "-o", str(final), "-",
    ]
    completed = subprocess.run(
        command, input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=600, env=env,
    )
    finished = now()
    raw.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    valid = completed.returncode == 0 and final.is_file() and final.stat().st_size > 0
    record = {
        "audit_run_id": f"synthetic-evidence-audit--attempt-{args.attempt}",
        "started_at": started,
        "finished_at": finished,
        "model": route["model"],
        "reasoning_effort": route["reasoning_effort"],
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "input_report": str(REPORT.relative_to(EVAL_ROOT)),
        "raw_output": str(raw.relative_to(EVAL_ROOT)),
        "stderr": str(stderr_path.relative_to(EVAL_ROOT)),
        "final_output": str(final.relative_to(EVAL_ROOT)) if final.exists() else None,
        "exit_status": completed.returncode,
        "excluded": {"value": not valid, "rule": None if valid else "audit did not produce a successful non-empty final output"},
        "evaluation_lock": {
            "release_id": evaluation_lock["release_id"],
            "sha256": lock_sha256(evaluation_lock),
            "preregistered": True,
        },
    }
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.rmtree(run_dir, ignore_errors=True)
    print(f"audit exit={completed.returncode} valid={valid} record={record_path}")


if __name__ == "__main__":
    main()
