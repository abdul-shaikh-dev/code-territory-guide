from __future__ import annotations

import hashlib
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EVAL_ROOT.parent
SKILL_SOURCE = REPO_ROOT / "skills" / "code-territory-guide"
SKILL_DEST = Path.home() / ".agents" / "skills" / "code-territory-guide"
RUN_ROOT = EVAL_ROOT / "results" / "runs"
MANIFEST = json.loads((EVAL_ROOT / "manifest.json").read_text(encoding="utf-8"))
ROUTING = json.loads((EVAL_ROOT / "model-routing.json").read_text(encoding="utf-8"))
MAX_WORKERS = 3
TIMEOUT_SECONDS = 240
CODEX = shutil.which("codex.cmd") or shutil.which("codex")


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def build_prompt(case: dict) -> tuple[str, list[dict]]:
    context_records: list[dict] = []
    context_blocks: list[str] = []
    for relative in case["context_files"]:
        path = EVAL_ROOT / relative
        context_records.append({"path": relative, "sha256": sha256(path)})
        context_blocks.append(f'<context path="{relative}">\n{path.read_text(encoding="utf-8")}\n</context>')

    parts = [case["query"]]
    if context_blocks:
        parts.append("Repository context supplied for this task:\n" + "\n\n".join(context_blocks))
    parts.append("Do not inspect files outside the supplied context. Do not modify files. Respond exactly as you would to the user, including decisions, validation expectations, and the completion claim you would make.")
    return "\n\n".join(parts), context_records


def run_one(case: dict, arm: str, seed: int) -> Path:
    route = ROUTING["cases"].get(case["id"], ROUTING["default"])
    run_id = f"{case['id']}--{arm}--seed-{seed}"
    run_dir = Path(tempfile.mkdtemp(prefix=f"ctg-{run_id}-", dir=os.environ.get("TEMP") or os.environ.get("TMP") or None))
    prompt, context_records = build_prompt(case)
    started = now()
    command = [
        CODEX, "exec", "--ephemeral", "--json", "--color", "never",
        "--sandbox", "read-only", "--skip-git-repo-check", "-C", str(run_dir),
        "-m", route["model"], "-c", f'model_reasoning_effort="{route["reasoning_effort"]}"',
        prompt,
    ]

    timed_out = False
    try:
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT_SECONDS)
        exit_status = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        exit_status = None
        stdout = error.stdout or ""
        stderr = error.stderr or ""

    finished = now()
    has_agent_message = '"type":"agent_message"' in stdout or '"type": "agent_message"' in stdout
    excluded = timed_out or (exit_status not in (0, None) and not has_agent_message) or not has_agent_message
    if timed_out:
        exclusion_rule = "hard timeout before an evaluable agent response"
    elif not has_agent_message:
        exclusion_rule = "no evaluable agent response"
    else:
        exclusion_rule = None

    record = {
        "run_id": run_id,
        "case_id": case["id"],
        "arm": arm,
        "seed": seed,
        "started_at": started,
        "finished_at": finished,
        "harness": "codex-cli-0.144.1-ephemeral-read-only",
        "model": route["model"],
        "reasoning_effort": route["reasoning_effort"],
        "query": prompt,
        "context": context_records,
        "treatment": {
            "skill_path": str(SKILL_DEST) if arm == "installed-skill" else None,
            "policy_payload": None
        },
        "raw_output": stdout,
        "tool_log": stderr,
        "worktree_before": "",
        "worktree_after": "",
        "diff": "",
        "validation_output": "",
        "exit_status": exit_status,
        "excluded": {"value": excluded, "rule": exclusion_rule},
        "criteria": [],
        "forbidden": [],
        "scorer": "unscored"
    }
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    output = RUN_ROOT / f"{run_id}.json"
    output.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.rmtree(run_dir, ignore_errors=True)
    return output


def run_arm(arm: str, seed: int, cases: list[dict] | None = None) -> None:
    cases = cases or MANIFEST["cases"]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(run_one, case, arm, seed): case["id"] for case in cases}
        for future in as_completed(futures):
            case_id = futures[future]
            try:
                print(f"completed {arm}: {case_id} -> {future.result()}", flush=True)
            except Exception as error:
                print(f"runner error {arm}: {case_id}: {error}", file=sys.stderr, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry-excluded", action="store_true")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    if CODEX is None:
        raise SystemExit("codex launcher not found on PATH")
    if SKILL_DEST.exists():
        raise SystemExit(f"refusing to overwrite existing skill installation: {SKILL_DEST}")

    if args.retry_excluded:
        selected: dict[str, list[dict]] = {}
        by_id = {case["id"]: case for case in MANIFEST["cases"]}
        for arm in ("baseline", "installed-skill"):
            selected[arm] = []
            for case_id, case in by_id.items():
                source = RUN_ROOT / f"{case_id}--{arm}--seed-1.json"
                if source.is_file() and json.loads(source.read_text(encoding="utf-8"))["excluded"]["value"]:
                    selected[arm].append(case)
    else:
        selected = {"baseline": MANIFEST["cases"], "installed-skill": MANIFEST["cases"]}

    run_arm("baseline", seed=args.seed, cases=selected["baseline"])
    SKILL_DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SKILL_SOURCE, SKILL_DEST)
    try:
        run_arm("installed-skill", seed=args.seed, cases=selected["installed-skill"])
    finally:
        shutil.rmtree(SKILL_DEST, ignore_errors=True)


if __name__ == "__main__":
    main()
