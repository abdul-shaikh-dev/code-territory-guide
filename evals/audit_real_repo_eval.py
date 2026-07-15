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

from freeze_evaluation import lock_sha256, validate_current_lock


EVAL_ROOT = Path(__file__).resolve().parent
RESULT_ROOT = EVAL_ROOT / "results" / "generated" / "real-repos"
MANIFEST = json.loads((EVAL_ROOT / "real-repo-manifest.json").read_text(encoding="utf-8"))
CODEX = shutil.which("codex.cmd") or shutil.which("codex")
AUTH_SOURCE = Path.home() / ".codex" / "auth.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=int, default=1)
    args = parser.parse_args()
    final = RESULT_ROOT / f"2026-07-12-audit-attempt-{args.attempt}.md"
    raw = RESULT_ROOT / f"2026-07-12-audit-attempt-{args.attempt}.jsonl"
    stderr_file = RESULT_ROOT / f"2026-07-12-audit-attempt-{args.attempt}.stderr.txt"
    record_path = RESULT_ROOT / f"2026-07-12-audit-attempt-{args.attempt}.record.json"
    if record_path.exists():
        raise SystemExit(f"refusing to overwrite {record_path}")
    if CODEX is None or not AUTH_SOURCE.is_file():
        raise SystemExit("Codex launcher or auth file unavailable")
    try:
        evaluation_lock = validate_current_lock()
    except ValueError as error:
        raise SystemExit(f"evaluation lock rejected before model execution: {error}") from error
    if MANIFEST["frozen_treatment_sha256"] != evaluation_lock["treatment_tree_sha256"]:
        raise SystemExit("historical real-repository manifest does not match the active evaluation lock")
    route = MANIFEST["audit"]
    prompt = """Independently audit the Code Territory Guide real-repository evaluation.

Inspect only:
- evals/real-repo-manifest.json
- evals/run_real_repo_eval.py
- evals/judge_real_repo_eval.py
- evals/build_real_repo_report.py
- evals/results/real-repos/runs/*.json
- evals/results/real-repos/judgments/simulator-capacity-zero-boundary--judge-attempt-4.json
- evals/results/real-repos/judgments/cogstash-stale-superpowers-plan--judge-attempt-5.json
- evals/results/generated/real-repository-readonly.md

Do not read the skill implementation or earlier synthetic reports. Verify run counts, exclusions, before/after repository state, disabled push URLs, treatment hashes, model metadata, rubric completeness, judge consistency, headline pass/outcome counts, and runtime/event/command metrics. Check for leaked expected answers, selection bias, unsupported claims, and whether preserved behavior is being overstated as improvement. Distinguish safety evidence from quality-uplift evidence.

Return a concise Markdown audit with a PASS, QUALIFIED, or FAIL verdict, severity-ordered findings, verified counts, supported claims, unsupported claims, and required next actions. Do not edit files or access the network."""
    work = Path(tempfile.mkdtemp(prefix="ctg-real-audit-"))
    audit_home = work / "home"
    audit_codex_home = audit_home / ".codex"
    audit_codex_home.mkdir(parents=True)
    shutil.copy2(AUTH_SOURCE, audit_codex_home / "auth.json")
    inherited = ("PATH", "SystemRoot", "WINDIR", "ComSpec", "PATHEXT")
    env = {key: os.environ[key] for key in inherited if key in os.environ}
    env.update({"CODEX_HOME": str(audit_codex_home), "HOME": str(audit_home), "USERPROFILE": str(audit_home)})
    started = now()
    command = [
        CODEX, "exec", "--ephemeral", "--json", "--color", "never", "--sandbox", "read-only",
        "--skip-git-repo-check", "-C", str(EVAL_ROOT.parent), "-m", route["model"],
        "-c", f'model_reasoning_effort="{route["reasoning_effort"]}"', "-o", str(final), "-",
    ]
    completed = subprocess.run(
        command, input=prompt, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=600, env=env,
    )
    finished = now()
    raw.write_text(completed.stdout, encoding="utf-8")
    stderr_file.write_text(completed.stderr, encoding="utf-8")
    valid = completed.returncode == 0 and final.is_file() and final.stat().st_size > 0
    record = {
        "audit_run_id": f"real-repository-audit--attempt-{args.attempt}", "started_at": started, "finished_at": finished,
        "model": route["model"], "reasoning_effort": route["reasoning_effort"], "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "raw_output": str(raw.relative_to(EVAL_ROOT)), "stderr": str(stderr_file.relative_to(EVAL_ROOT)),
        "final_output": str(final.relative_to(EVAL_ROOT)) if final.exists() else None,
        "exit_status": completed.returncode,
        "excluded": {"value": not valid, "rule": None if valid else "audit did not produce a successful final output"},
        "evaluation_lock": {
            "release_id": evaluation_lock["release_id"],
            "sha256": lock_sha256(evaluation_lock),
            "preregistered": True,
        },
    }
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    print(f"audit valid={valid} record={record_path}")


if __name__ == "__main__":
    main()
