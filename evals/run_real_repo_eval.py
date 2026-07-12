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


EVAL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EVAL_ROOT.parent
SKILL_SOURCE = REPO_ROOT / "skills" / "code-territory-guide"
MANIFEST = json.loads((EVAL_ROOT / "real-repo-manifest.json").read_text(encoding="utf-8"))
CLONE_ROOT = Path(r"G:\tmp\code-territory-guide-real-repos")
TEMP_ROOT = Path(r"G:\tmp\code-territory-guide-real-sessions")
RESULT_ROOT = EVAL_ROOT / "results" / "real-repos" / "runs"
AUTH_SOURCE = Path.home() / ".codex" / "auth.json"
CODEX = shutil.which("codex.cmd") or shutil.which("codex")
TIMEOUT_SECONDS = 480


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hash(root: Path) -> tuple[str, dict[str, str]]:
    files = {path.relative_to(root).as_posix(): sha256_file(path) for path in sorted(root.rglob("*")) if path.is_file()}
    digest = hashlib.sha256()
    for relative, value in files.items():
        digest.update(f"{relative}\0{value}\n".encode("utf-8"))
    return digest.hexdigest(), files


def repository_tree_hash(root: Path) -> str:
    files = {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }
    digest = hashlib.sha256()
    for relative, value in files.items():
        digest.update(f"{relative}\0{value}\n".encode("utf-8"))
    return digest.hexdigest()


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()


def observable_events(raw: str) -> list[dict]:
    events = []
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item") or {}
        kind = item.get("type")
        if kind == "agent_message":
            events.append({"type": kind, "text": item.get("text", "")})
        elif kind == "command_execution" and item.get("status") != "in_progress":
            command = item.get("command", "")
            output = item.get("aggregated_output", "")
            if "code-territory-guide" in command.lower() and "get-content" in command.lower():
                output = "<skill contents omitted from derived evidence>"
            events.append({
                "type": kind, "command": command, "output": output,
                "exit_code": item.get("exit_code"), "status": item.get("status"),
            })
        elif kind == "file_change" and item.get("status") != "in_progress":
            events.append({"type": kind, "changes": item.get("changes", []), "status": item.get("status")})
    return events


def make_home(root: Path, arm: str) -> tuple[Path, dict]:
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


def run_case(case: dict, arm: str, attempt: int) -> Path:
    route = MANIFEST.get("retry_routing", {}).get(case["id"], case) if attempt > 1 else case
    repo = CLONE_ROOT / case["repo"]
    run_id = f"{case['id']}--{arm}--attempt-{attempt}"
    output = RESULT_ROOT / f"{run_id}.json"
    if output.exists():
        raise RuntimeError(f"refusing to overwrite {output}")
    before = {
        "head": git(repo, "rev-parse", "HEAD"),
        "branch": git(repo, "branch", "--show-current"),
        "status": git(repo, "status", "--short"),
        "fetch_url": git(repo, "remote", "get-url", "origin"),
        "push_url": git(repo, "remote", "get-url", "--push", "origin"),
        "tree_sha256": repository_tree_hash(repo),
    }
    if before["status"] or before["push_url"] != "DISABLED":
        raise RuntimeError(f"unsafe clone state for {case['repo']}: {before}")

    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    session = Path(tempfile.mkdtemp(prefix=f"{run_id}-", dir=TEMP_ROOT))
    home, treatment = make_home(session, arm)
    treatment_before = treatment["tree_sha256"]
    prompt = case["query"] + "\n\nDo not access the network. Work only from the current local clone."
    env = os.environ.copy()
    env.update({"CODEX_HOME": str(home / ".codex"), "HOME": str(home), "USERPROFILE": str(home)})
    command = [
        CODEX, "exec", "--ephemeral", "--json", "--color", "never", "--sandbox", "read-only",
        "--skip-git-repo-check", "-C", str(repo), "-m", route["model"],
        "-c", f'model_reasoning_effort="{route["reasoning_effort"]}"', "-",
    ]
    started = now()
    timed_out = False
    try:
        completed = subprocess.run(
            command, input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=TIMEOUT_SECONDS, env=env,
        )
        exit_status, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        exit_status, stdout, stderr = None, error.stdout or "", error.stderr or ""
    finished = now()
    after = {
        "head": git(repo, "rev-parse", "HEAD"),
        "branch": git(repo, "branch", "--show-current"),
        "status": git(repo, "status", "--short"),
        "fetch_url": git(repo, "remote", "get-url", "origin"),
        "push_url": git(repo, "remote", "get-url", "--push", "origin"),
        "tree_sha256": repository_tree_hash(repo),
    }
    if treatment["installed"]:
        treatment_after, _ = tree_hash(Path(treatment["path"]))
    else:
        treatment_after = None
    events = observable_events(stdout)
    contamination = before != after or treatment_before != treatment_after
    has_response = any(event["type"] == "agent_message" for event in events)
    excluded = timed_out or contamination or not has_response
    rule = "hard timeout" if timed_out else "repository or treatment changed" if contamination else "no evaluable response" if not has_response else None
    record = {
        "run_id": run_id, "case_id": case["id"], "repo": case["repo"], "arm": arm,
        "attempt": attempt, "started_at": started, "finished_at": finished,
        "model": route["model"], "reasoning_effort": route["reasoning_effort"],
        "query": prompt, "repository_before": before, "repository_after": after,
        "treatment": {**treatment, "tree_sha256_after": treatment_after},
        "raw_output": stdout, "tool_log": stderr, "events": events, "exit_status": exit_status,
        "excluded": {"value": excluded, "rule": rule},
    }
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.rmtree(session, ignore_errors=True)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--case")
    parser.add_argument("--arm", choices=["baseline", "installed-skill", "both"], default="both")
    args = parser.parse_args()
    if CODEX is None or not AUTH_SOURCE.is_file():
        raise SystemExit("Codex launcher or auth file unavailable")
    source_hash, _ = tree_hash(SKILL_SOURCE)
    if source_hash != MANIFEST["frozen_treatment_sha256"]:
        raise SystemExit(
            "skill tree differs from frozen_treatment_sha256; create a new evaluation version instead of silently changing treatment"
        )
    cases = [case for case in MANIFEST["cases"] if not args.case or case["id"] == args.case]
    if not cases:
        raise SystemExit(f"unknown case: {args.case}")
    arms = ("baseline", "installed-skill") if args.arm == "both" else (args.arm,)
    for arm in arms:
        for case in cases:
            print(f"completed {run_case(case, arm, args.attempt)}", flush=True)


if __name__ == "__main__":
    main()
