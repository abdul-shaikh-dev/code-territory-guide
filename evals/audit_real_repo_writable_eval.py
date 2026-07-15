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


EVAL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EVAL_ROOT.parent
RESULT_ROOT = EVAL_ROOT / "results" / "generated" / "real-repos-writable"
ROUTING = json.loads(
    (EVAL_ROOT / "model-routing.json").read_text(encoding="utf-8")
)
AUTH_SOURCE = Path.home() / ".codex" / "auth.json"
CODEX = shutil.which("codex.cmd") or shutil.which("codex")


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=int, required=True)
    args = parser.parse_args()
    if CODEX is None or not AUTH_SOURCE.is_file():
        raise SystemExit("Codex launcher or auth file unavailable")
    try:
        lock = validate_lock(args.attempt)
    except ValueError as error:
        raise SystemExit(f"evaluation lock rejected before audit: {error}") from error
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    stem = f"writable-real-repository-audit-attempt-{args.attempt}"
    final = RESULT_ROOT / f"{stem}.md"
    raw = RESULT_ROOT / f"{stem}.jsonl"
    stderr_path = RESULT_ROOT / f"{stem}.stderr.txt"
    record_path = RESULT_ROOT / f"{stem}.record.json"
    if record_path.exists():
        raise SystemExit(f"refusing to overwrite preserved audit: {record_path}")
    prompt = """Act as an independent adversarial auditor of the writable real-repository evaluation.

Inspect only:
- evals/real-repo-writable-manifest.json
- evals/real-repo-writable-run.schema.json
- evals/run_real_repo_writable_eval.py
- evals/judge_real_repo_writable_eval.py
- evals/build_real_repo_writable_report.py
- evals/results/real-repos-writable/runs/*.json
- evals/results/real-repos-writable/judgments/*.json
- evals/results/real-repository-writable-evidence.md

Do not inspect the skill implementation. Verify matched seed commits, separate workspaces, disabled remotes, treatment hashes, lock provenance, model routing, execution mode, local commit counts, clean final worktrees, changed files, validation-command evidence, exclusions, blinded judging, rubric consistency, report counts, and claim qualifications. Look for selection bias, network-capable commands, dependency mutation, read-only downgrade, leaked arm identity, unsupported completion claims, and overgeneralization.

Return concise Markdown with a PASS, QUALIFIED, or FAIL verdict, severity-ordered findings, verified counts, supported claims, unsupported claims, and required next actions. Do not edit files, access the network, or run model sessions."""
    work = Path(tempfile.mkdtemp(prefix="ctg-writable-audit-"))
    home = work / "home"
    codex_home = home / ".codex"
    codex_home.mkdir(parents=True)
    shutil.copy2(AUTH_SOURCE, codex_home / "auth.json")
    inherited = ("PATH", "SystemRoot", "WINDIR", "ComSpec", "PATHEXT")
    env = {key: os.environ[key] for key in inherited if key in os.environ}
    env.update(
        {
            "CODEX_HOME": str(codex_home),
            "HOME": str(home),
            "USERPROFILE": str(home),
        }
    )
    route = ROUTING["audit"]
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
        str(REPO_ROOT),
        "-m",
        route["model"],
        "-c",
        f'model_reasoning_effort="{route["reasoning_effort"]}"',
        "-o",
        str(final),
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
        timeout=600,
        env=env,
    )
    finished = now()
    raw.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    valid = (
        completed.returncode == 0
        and final.is_file()
        and final.stat().st_size > 0
    )
    record = {
        "audit_run_id": stem,
        "started_at": started,
        "finished_at": finished,
        "model": route["model"],
        "reasoning_effort": route["reasoning_effort"],
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "evaluation_lock": {
            "release_id": lock["release_id"],
            "sha256": lock_sha256(lock),
            "preregistered": True,
        },
        "raw_output": str(raw.relative_to(EVAL_ROOT)),
        "stderr": str(stderr_path.relative_to(EVAL_ROOT)),
        "final_output": (
            str(final.relative_to(EVAL_ROOT)) if final.exists() else None
        ),
        "exit_status": completed.returncode,
        "excluded": {
            "value": not valid,
            "rule": None if valid else "audit did not produce a successful result",
        },
    }
    record_path.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    shutil.rmtree(work, ignore_errors=True)
    print(f"audit valid={valid} record={record_path}")


if __name__ == "__main__":
    main()
