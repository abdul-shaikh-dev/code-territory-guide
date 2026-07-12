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

from materialize_fixture import materialize


EVAL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EVAL_ROOT.parent
SKILL_SOURCE = REPO_ROOT / "skills" / "code-territory-guide"
RUN_ROOT = EVAL_ROOT / "results" / "runs-v2"
MANIFEST = json.loads((EVAL_ROOT / "manifest.json").read_text(encoding="utf-8"))
ROUTING_PATH = EVAL_ROOT / "model-routing.json"
ROUTING = json.loads(ROUTING_PATH.read_text(encoding="utf-8"))
AUTH_SOURCE = Path.home() / ".codex" / "auth.json"
CODEX = shutil.which("codex.cmd") or shutil.which("codex")
MAX_WORKERS = 2
TIMEOUT_SECONDS = 480
TEMP_ROOT = Path(os.environ.get("CTG_EVAL_TEMP_ROOT", r"G:\tmp\code-territory-guide-evals"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def snapshot(root: Path, include_content: bool = False) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file() and ".git" not in item.parts):
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        entry: dict[str, object] = {"sha256": sha256_bytes(data), "size": len(data)}
        if include_content and len(data) <= 100_000:
            try:
                entry["text"] = data.decode("utf-8")
            except UnicodeDecodeError:
                pass
        result[relative] = entry
    return result


def tree_hash(root: Path) -> tuple[str, dict[str, str]]:
    files = {path.relative_to(root).as_posix(): sha256_file(path) for path in sorted(root.rglob("*")) if path.is_file()}
    digest = hashlib.sha256()
    for relative, file_hash in files.items():
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest(), files


def git_output(repo: Path, *args: str) -> str:
    completed = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return completed.stdout + completed.stderr


def tool_events(raw_output: str) -> list[dict]:
    events: list[dict] = []
    for line in raw_output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item") or {}
        kind = item.get("type")
        if kind == "command_execution" and item.get("status") != "in_progress":
            command = item.get("command", "")
            output = item.get("aggregated_output", "")
            if "\\.agents\\skills\\code-territory-guide" in command.lower():
                output = "<skill contents omitted from derived evidence>"
            events.append({
                "type": kind, "command": command, "output": output,
                "exit_code": item.get("exit_code"), "status": item.get("status"),
            })
        elif kind == "file_change" and item.get("status") != "in_progress":
            events.append({"type": kind, "changes": item.get("changes", []), "status": item.get("status")})
        elif kind == "agent_message":
            events.append({"type": kind, "text": item.get("text", "")})
    return events


def changed_files(before: dict, after: dict) -> list[dict]:
    changes = []
    for relative in sorted(set(before) | set(after)):
        old = before.get(relative)
        new = after.get(relative)
        if old != new:
            changes.append({
                "path": relative,
                "kind": "add" if old is None else "delete" if new is None else "update",
                "before": old,
                "after": new,
            })
    return changes


def make_isolated_home(root: Path, arm: str) -> tuple[Path, dict]:
    home = root / "home"
    codex_home = home / ".codex"
    codex_home.mkdir(parents=True)
    shutil.copy2(AUTH_SOURCE, codex_home / "auth.json")
    treatment = {"installed": False, "path": None, "tree_sha256": None, "files": {}}
    if arm == "installed-skill":
        destination = codex_home / "skills" / "code-territory-guide"
        destination.parent.mkdir(parents=True)
        shutil.copytree(SKILL_SOURCE, destination)
        digest, files = tree_hash(destination)
        treatment = {"installed": True, "path": str(destination), "tree_sha256": digest, "files": files}
    return home, treatment


def run_one(case: dict, arm: str, attempt: int) -> Path:
    route = ROUTING["cases"].get(case["id"], ROUTING["default"])
    run_id = f"{case['id']}--{arm}--attempt-{attempt}"
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    run_parent = Path(tempfile.mkdtemp(prefix=f"ctg-v2-{run_id}-", dir=TEMP_ROOT))
    repo = run_parent / "repo"
    materialize(case["id"], repo)
    home, treatment = make_isolated_home(run_parent, arm)
    treatment_before = treatment["tree_sha256"]
    fixture_hash, fixture_files = tree_hash(repo)
    before = snapshot(repo, include_content=True)
    status_before = git_output(repo, "status", "--short", "--branch")
    prompt = (
        case["query"]
        + "\n\nWork only in the current repository. Do not search parent directories or user-profile directories. "
        "Preserve unrelated existing changes and use the repository's own validation instructions."
    )
    env = os.environ.copy()
    env.update({
        "CODEX_HOME": str(home / ".codex"),
        "HOME": str(home),
        "USERPROFILE": str(home),
        "TEMP": str(run_parent / "tmp"),
        "TMP": str(run_parent / "tmp"),
    })
    Path(env["TEMP"]).mkdir()
    command = [
        CODEX, "exec", "--ephemeral", "--json", "--color", "never",
        "--sandbox", "workspace-write", "--skip-git-repo-check", "-C", str(repo),
        "-m", route["model"], "-c", f'model_reasoning_effort="{route["reasoning_effort"]}"', "-",
    ]
    started = now()
    timed_out = False
    try:
        completed = subprocess.run(
            command, input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=TIMEOUT_SECONDS, env=env,
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
    after = snapshot(repo, include_content=True)
    status_after = git_output(repo, "status", "--short", "--branch")
    diff = git_output(repo, "diff", "--binary") + git_output(repo, "diff", "--cached", "--binary")
    events = tool_events(stdout)
    has_agent_message = any(event["type"] == "agent_message" for event in events)
    if treatment["installed"]:
        treatment_after, _ = tree_hash(Path(treatment["path"]))
    else:
        treatment_after = None
    contamination = treatment_before != treatment_after
    excluded = timed_out or not has_agent_message or contamination
    if contamination:
        exclusion_rule = "treatment payload changed during run"
    elif timed_out:
        exclusion_rule = "hard timeout before an evaluable agent response"
    elif not has_agent_message:
        exclusion_rule = "no evaluable agent response"
    else:
        exclusion_rule = None
    record = {
        "schema_version": 2,
        "run_id": run_id,
        "case_id": case["id"],
        "arm": arm,
        "attempt": attempt,
        "started_at": started,
        "finished_at": finished,
        "harness": "codex-cli-materialized-git-isolated-home-v2",
        "model": route["model"],
        "reasoning_effort": route["reasoning_effort"],
        "routing_sha256": sha256_file(ROUTING_PATH),
        "query": prompt,
        "fixture": {"tree_sha256": fixture_hash, "files": fixture_files},
        "treatment": {**treatment, "tree_sha256_after": treatment_after},
        "raw_output": stdout,
        "tool_log": stderr,
        "worktree_before": status_before,
        "worktree_after": status_after,
        "diff": diff,
        "files_before": before,
        "files_after": after,
        "changed_files": changed_files(before, after),
        "tool_events": events,
        "exit_status": exit_status,
        "excluded": {"value": excluded, "rule": exclusion_rule},
    }
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    output = RUN_ROOT / f"{run_id}.json"
    if output.exists():
        raise RuntimeError(f"refusing to overwrite {output}")
    output.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.rmtree(run_parent, ignore_errors=True)
    return output


def run_arm(cases: list[dict], arm: str, attempt: int) -> None:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(run_one, case, arm, attempt): case["id"] for case in cases}
        for future in as_completed(futures):
            case_id = futures[future]
            try:
                print(f"completed {arm}: {case_id} -> {future.result()}", flush=True)
            except Exception as error:
                print(f"runner error {arm}: {case_id}: {error}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--case")
    parser.add_argument("--arm", choices=["baseline", "installed-skill", "both"], default="both")
    args = parser.parse_args()
    if CODEX is None:
        raise SystemExit("codex launcher not found on PATH")
    if not AUTH_SOURCE.is_file():
        raise SystemExit("Codex auth.json not found")
    cases = [case for case in MANIFEST["cases"] if not args.case or case["id"] == args.case]
    if not cases:
        raise SystemExit(f"unknown case: {args.case}")
    if args.arm in ("baseline", "both"):
        run_arm(cases, "baseline", args.attempt)
    if args.arm in ("installed-skill", "both"):
        run_arm(cases, "installed-skill", args.attempt)


if __name__ == "__main__":
    main()
