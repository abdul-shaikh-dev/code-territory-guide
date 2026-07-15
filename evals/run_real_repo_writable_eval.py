from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from freeze_evaluation import (
    lock_sha256,
    sha256_file,
    tree_hash,
    validate_lock,
)


EVAL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EVAL_ROOT.parent
SKILL_SOURCE = REPO_ROOT / "skills" / "code-territory-guide"
MANIFEST_PATH = EVAL_ROOT / "real-repo-writable-manifest.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
RESULT_ROOT = EVAL_ROOT / "results" / "real-repos-writable" / "runs"
AUTH_SOURCE = Path.home() / ".codex" / "auth.json"
CODEX = shutil.which("codex.cmd") or shutil.which("codex")
TIMEOUT_SECONDS = 900
READ_ONLY_MARKERS = (
    "writing is blocked by read-only sandbox",
    "workspace is read-only",
    "repository is read-only",
    "rejected: blocked by policy",
)
NETWORK_COMMAND = re.compile(
    r"(?i)(?:\bgit\s+(?:clone|fetch|pull|push)\b|\bgh\b|\bcurl\b|\bwget\b|"
    r"invoke-webrequest|invoke-restmethod|\bnpm\s+(?:ci|install)\b|"
    r"\bpip\s+install\b|\buv\s+sync\b|https?://)"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def resolved_child(root: Path, relative: str | Path, *, must_exist: bool = True) -> Path:
    resolved_root = root.resolve(strict=True)
    candidate = (resolved_root / relative).resolve(strict=must_exist)
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise ValueError(f"path escapes configured root: {candidate}")
    return candidate


def assert_plain_directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise ValueError(f"{label} is not a directory: {path}")
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if path.is_symlink() or bool(attributes & reparse_flag):
        raise ValueError(f"{label} must not be a symlink or junction: {path}")


def directory_hash(root: Path) -> str:
    if root.is_file():
        return sha256_file(root)
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"provisioned dependency contains a link: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def copy_provisioned_paths(seed: Path, repo: Path, relative_paths: list[str]) -> dict[str, str]:
    fingerprints: dict[str, str] = {}
    for relative in relative_paths:
        source = resolved_child(seed, relative)
        destination = resolved_child(repo, relative, must_exist=False)
        if destination.exists():
            raise ValueError(f"provisioned destination already exists: {destination}")
        if source.is_dir():
            assert_plain_directory(source, f"provisioned path {relative}")
            shutil.copytree(source, destination)
        elif source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        else:
            raise ValueError(f"unsupported provisioned path: {source}")
        fingerprints[relative] = directory_hash(destination)
    return fingerprints


def provisioned_hashes(repo: Path, relative_paths: list[str]) -> dict[str, str]:
    return {
        relative: directory_hash(resolved_child(repo, relative))
        for relative in relative_paths
    }


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
            events.append(
                {
                    "type": kind,
                    "command": command,
                    "output": output,
                    "exit_code": item.get("exit_code"),
                    "status": item.get("status"),
                }
            )
        elif kind == "file_change" and item.get("status") != "in_progress":
            events.append(
                {
                    "type": kind,
                    "changes": item.get("changes", []),
                    "status": item.get("status"),
                }
            )
    return events


def validation_results(
    events: list[dict],
    required_commands: list[str],
) -> dict[str, bool]:
    completed_commands = [
        event
        for event in events
        if event["type"] == "command_execution" and event.get("exit_code") == 0
    ]
    return {
        required: any(
            required.replace("\\", "/").lower()
            in event.get("command", "").replace("\\", "/").lower()
            for event in completed_commands
        )
        for required in required_commands
    }


def make_home(session: Path, arm: str) -> tuple[Path, dict]:
    home = session / "home"
    codex_home = home / ".codex"
    codex_home.mkdir(parents=True)
    shutil.copy2(AUTH_SOURCE, codex_home / "auth.json")
    treatment = {"installed": False, "path": None, "tree_sha256": None}
    if arm == "installed-skill":
        destination = codex_home / "skills" / "code-territory-guide"
        destination.parent.mkdir(parents=True)
        shutil.copytree(SKILL_SOURCE, destination)
        treatment = {
            "installed": True,
            "path": str(destination),
            "tree_sha256": tree_hash(destination),
        }
    return home, treatment


def codex_command(repo: Path, case: dict) -> list[str]:
    return [
        CODEX,
        "--ask-for-approval",
        "never",
        "exec",
        "--ephemeral",
        "--json",
        "--color",
        "never",
        "--sandbox",
        "workspace-write",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "-C",
        str(repo),
        "-m",
        case["model"],
        "-c",
        'windows.sandbox="elevated"',
        "-c",
        f'model_reasoning_effort="{case["reasoning_effort"]}"',
        "-",
    ]


def repository_state(repo: Path, base_commit: str) -> dict:
    return {
        "head": git(repo, "rev-parse", "HEAD"),
        "tree": git(repo, "rev-parse", "HEAD^{tree}"),
        "branch": git(repo, "branch", "--show-current"),
        "status": git(repo, "status", "--short"),
        "fetch_url": git(repo, "remote", "get-url", "origin"),
        "push_url": git(repo, "remote", "get-url", "--push", "origin"),
        "commits_from_base": int(git(repo, "rev-list", "--count", f"{base_commit}..HEAD")),
        "commit_subject": git(repo, "log", "-1", "--format=%s"),
    }


def changed_files(repo: Path, base_commit: str) -> list[dict[str, str]]:
    values = []
    for line in git(repo, "diff", "--name-status", f"{base_commit}..HEAD").splitlines():
        if not line:
            continue
        parts = line.split("\t")
        values.append({"status": parts[0], "path": parts[-1]})
    return values


def materialize_repository(case: dict, seed_root: Path, session: Path, arm: str, attempt: int) -> tuple[Path, dict]:
    seed = resolved_child(seed_root, case["repo"])
    assert_plain_directory(seed, f"seed repository {case['repo']}")
    if not (seed / ".git").exists():
        raise ValueError(f"seed is not a Git repository: {seed}")
    seed_head = git(seed, "rev-parse", "HEAD")
    seed_status = git(seed, "status", "--short")
    if seed_head != case["base_commit"] or seed_status:
        raise ValueError(
            f"seed mismatch for {case['id']}: head={seed_head} status={seed_status!r}"
        )
    for relative in case.get("provisioned_paths", []):
        resolved_child(seed, relative)

    repo = session / "repo"
    clone = subprocess.run(
        ["git", "clone", "--local", "--no-hardlinks", str(seed), str(repo)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if clone.returncode != 0:
        raise RuntimeError(f"local clone failed: {clone.stderr.strip()}")
    git(repo, "checkout", "--detach", case["base_commit"])
    branch = f"eval/{case['id']}/{arm}/attempt-{attempt}"
    git(repo, "checkout", "-b", branch)
    git(repo, "remote", "set-url", "origin", "DISABLED")
    git(repo, "remote", "set-url", "--push", "origin", "DISABLED")
    provisioned = copy_provisioned_paths(
        seed,
        repo,
        case.get("provisioned_paths", []),
    )
    state = repository_state(repo, case["base_commit"])
    if state["status"] or state["fetch_url"] != "DISABLED" or state["push_url"] != "DISABLED":
        raise ValueError(f"unsafe materialized repository: {state}")
    return repo, {
        "path": str(seed),
        "head": seed_head,
        "tree": git(seed, "rev-parse", "HEAD^{tree}"),
        "provisioned_sha256": provisioned,
    }


def exclusion_reasons(
    raw: str,
    events: list[dict],
    before: dict,
    after: dict,
    treatment_before: str | None,
    treatment_after: str | None,
    provisioned_before: dict[str, str],
    provisioned_after: dict[str, str],
    timed_out: bool,
    exit_status: int | None,
    changed: list[dict[str, str]],
    validation_observed: dict[str, bool],
    commit_subject_pattern: str,
) -> list[str]:
    reasons = []
    lowered = raw.lower()
    if timed_out:
        reasons.append("hard timeout")
    elif exit_status != 0:
        reasons.append("model process exited unsuccessfully")
    if not any(event["type"] == "agent_message" for event in events):
        reasons.append("no evaluable agent response")
    if any(marker in lowered for marker in READ_ONLY_MARKERS):
        reasons.append("workspace-write downgraded to read-only")
    if any(
        NETWORK_COMMAND.search(event.get("command", ""))
        for event in events
        if event["type"] == "command_execution"
    ):
        reasons.append("network-capable command observed")
    if after["fetch_url"] != "DISABLED" or after["push_url"] != "DISABLED":
        reasons.append("remote URL changed or enabled")
    if after["branch"] != before["branch"]:
        reasons.append("evaluation branch changed")
    if after["commits_from_base"] != 1:
        reasons.append("expected exactly one local commit")
    if after["status"]:
        reasons.append("uncommitted repository changes remain")
    if not changed:
        reasons.append("no committed task delta")
    if not all(validation_observed.values()):
        reasons.append("required validation command not observed")
    if not re.match(commit_subject_pattern, after["commit_subject"], flags=re.IGNORECASE):
        reasons.append("commit message does not match the registered convention")
    if treatment_before != treatment_after:
        reasons.append("treatment payload changed")
    if provisioned_before != provisioned_after:
        reasons.append("provisioned dependencies changed")
    return reasons


def run_case(
    case: dict,
    arm: str,
    attempt: int,
    evaluation_lock: dict,
    seed_root: Path,
    session_root: Path,
    keep_workspace: bool,
) -> Path:
    run_id = f"{case['id']}--{arm}--attempt-{attempt}"
    output = RESULT_ROOT / f"{run_id}.json"
    if output.exists():
        raise RuntimeError(f"refusing to overwrite {output}")
    session = Path(tempfile.mkdtemp(prefix=f"{run_id}-", dir=session_root))
    repo, seed = materialize_repository(case, seed_root, session, arm, attempt)
    home, treatment = make_home(session, arm)
    treatment_before = treatment["tree_sha256"]
    provisioned_before = seed["provisioned_sha256"]
    before = repository_state(repo, case["base_commit"])
    prompt = (
        case["query"]
        + "\n\nWork only in the current disposable repository. "
        "Do not inspect parent directories or other repositories. "
        "The fetch and push URLs are disabled and must remain disabled. "
        "Do not access the network or install dependencies. "
        "Use only the already-provisioned local dependencies. "
        f"Required validation commands: {json.dumps(case['validation_commands'])}. "
        f"Commit convention: {case['commit_convention']}."
    )
    inherited = (
        "PATH",
        "SystemRoot",
        "WINDIR",
        "ComSpec",
        "PATHEXT",
        "NUMBER_OF_PROCESSORS",
        "PROCESSOR_ARCHITECTURE",
    )
    env = {key: os.environ[key] for key in inherited if key in os.environ}
    temp = session / "tmp"
    temp.mkdir()
    env.update(
        {
            "CODEX_HOME": str(home / ".codex"),
            "HOME": str(home),
            "USERPROFILE": str(home),
            "TEMP": str(temp),
            "TMP": str(temp),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    command = codex_command(repo, case)
    started = now()
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_SECONDS,
            env=env,
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
    events = observable_events(stdout)
    after = repository_state(repo, case["base_commit"])
    changed = changed_files(repo, case["base_commit"])
    diff = git(repo, "diff", "--binary", f"{case['base_commit']}..HEAD")
    treatment_after = tree_hash(Path(treatment["path"])) if treatment["installed"] else None
    provisioned_after = provisioned_hashes(
        repo,
        case.get("provisioned_paths", []),
    )
    validation_observed = validation_results(events, case["validation_commands"])
    reasons = exclusion_reasons(
        stdout + "\n" + stderr,
        events,
        before,
        after,
        treatment_before,
        treatment_after,
        provisioned_before,
        provisioned_after,
        timed_out,
        exit_status,
        changed,
        validation_observed,
        case["commit_subject_pattern"],
    )
    record = {
        "schema_version": 1,
        "run_id": run_id,
        "case_id": case["id"],
        "repo": case["repo"],
        "arm": arm,
        "attempt": attempt,
        "started_at": started,
        "finished_at": finished,
        "model": case["model"],
        "reasoning_effort": case["reasoning_effort"],
        "query": prompt,
        "execution": {
            "sandbox": "workspace-write",
            "windows_sandbox": "elevated",
            "approval_policy": "never",
            "network_policy": "prohibited-and-observed",
            "workspace": str(repo),
            "kept": keep_workspace,
        },
        "seed": seed,
        "repository_before": before,
        "repository_after": after,
        "treatment": {
            **treatment,
            "tree_sha256_after": treatment_after,
        },
        "evaluation_lock": {
            "release_id": evaluation_lock["release_id"],
            "sha256": lock_sha256(evaluation_lock),
            "preregistered": True,
        },
        "events": events,
        "raw_output": stdout,
        "tool_log": stderr,
        "diff": diff,
        "changed_files": changed,
        "provisioned_sha256_after": provisioned_after,
        "validation_observed": validation_observed,
        "exit_status": exit_status,
        "excluded": {"value": bool(reasons), "rules": reasons},
    }
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if not keep_workspace:
        shutil.rmtree(session, ignore_errors=True)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--case")
    parser.add_argument(
        "--arm",
        choices=["baseline", "installed-skill", "both"],
        default="both",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--keep-workspaces", action="store_true")
    args = parser.parse_args()
    if CODEX is None or not AUTH_SOURCE.is_file():
        raise SystemExit("Codex launcher or auth file unavailable")
    try:
        evaluation_lock = validate_lock(args.attempt)
    except ValueError as error:
        raise SystemExit(f"evaluation lock rejected before model execution: {error}") from error
    if tree_hash(SKILL_SOURCE) != MANIFEST["frozen_treatment_sha256"]:
        raise SystemExit("writable manifest treatment hash does not match the skill")
    if evaluation_lock["treatment_tree_sha256"] != MANIFEST["frozen_treatment_sha256"]:
        raise SystemExit("active evaluation lock does not match the writable manifest")

    seed_value = os.environ.get(MANIFEST["seed_root_env"])
    session_value = os.environ.get(MANIFEST["session_root_env"])
    if not seed_value or not session_value:
        raise SystemExit(
            f"set {MANIFEST['seed_root_env']} and {MANIFEST['session_root_env']}"
        )
    seed_root = Path(seed_value)
    session_root = Path(session_value)
    assert_plain_directory(seed_root, "seed root")
    session_root.mkdir(parents=True, exist_ok=True)
    assert_plain_directory(session_root, "session root")
    resolved_seed = seed_root.resolve()
    resolved_session = session_root.resolve()
    if (
        resolved_seed == resolved_session
        or resolved_seed in resolved_session.parents
        or resolved_session in resolved_seed.parents
    ):
        raise SystemExit("seed and session roots must not overlap")

    cases = [
        case
        for case in MANIFEST["cases"]
        if not args.case or case["id"] == args.case
    ]
    if not cases:
        raise SystemExit(f"unknown case: {args.case}")
    arms = (
        ("baseline", "installed-skill")
        if args.arm == "both"
        else (args.arm,)
    )
    failures = []
    for case in cases:
        for arm in arms:
            output = RESULT_ROOT / f"{case['id']}--{arm}--attempt-{args.attempt}.json"
            if output.exists() and args.resume:
                print(f"resume: preserved {output}", flush=True)
                continue
            try:
                path = run_case(
                    case,
                    arm,
                    args.attempt,
                    evaluation_lock,
                    seed_root,
                    session_root,
                    args.keep_workspaces,
                )
                record = json.loads(path.read_text(encoding="utf-8"))
                print(
                    f"completed {case['id']}/{arm}: excluded={record['excluded']['value']} -> {path}",
                    flush=True,
                )
                if record["excluded"]["value"]:
                    failures.append((case["id"], arm, record["excluded"]["rules"]))
                    break
            except Exception as error:
                failures.append((case["id"], arm, [str(error)]))
                break
        if failures:
            break
    if failures:
        raise SystemExit(f"writable evaluation stopped: {failures}")


if __name__ == "__main__":
    main()
