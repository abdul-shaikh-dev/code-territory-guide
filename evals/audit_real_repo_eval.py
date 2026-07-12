from __future__ import annotations

import hashlib
import argparse
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parent
RESULT_ROOT = EVAL_ROOT / "results" / "generated" / "real-repos"
MANIFEST = json.loads((EVAL_ROOT / "real-repo-manifest.json").read_text(encoding="utf-8"))
CODEX = shutil.which("codex.cmd") or shutil.which("codex")


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
    started = now()
    command = [
        CODEX, "exec", "--ephemeral", "--json", "--color", "never", "--sandbox", "read-only",
        "--skip-git-repo-check", "-C", str(EVAL_ROOT.parent), "-m", route["model"],
        "-c", f'model_reasoning_effort="{route["reasoning_effort"]}"', "-o", str(final), "-",
    ]
    completed = subprocess.run(command, input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
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
    }
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    print(f"audit valid={valid} record={record_path}")


if __name__ == "__main__":
    main()
