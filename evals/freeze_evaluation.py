from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EVAL_ROOT.parent
LOCK_PATH = EVAL_ROOT / "evaluation-lock.json"
SKILL_ROOT = REPO_ROOT / "skills" / "code-territory-guide"
TEXT_SUFFIXES = {".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
PINNED_FILES = (
    "freeze_evaluation.py",
    "manifest.json",
    "model-routing.json",
    "materialize_fixture.py",
    "run_matrix.py",
    "run-record.schema.json",
    "judge_matrix.py",
    "judge-blind-output.schema.json",
    "judge-output.schema.json",
    "evidence_sanitizer.py",
    "evaluation_integrity.py",
    "validate_records.py",
    "build_report.py",
    "run_real_repo_eval.py",
    "validate_real_repo_eval.py",
    "validate_manifest.py",
    "exclusion-policy.md",
    "audit_evidence.py",
    "real-repo-manifest.json",
    "judge_real_repo_eval.py",
    "build_real_repo_report.py",
    "audit_real_repo_eval.py",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_file_bytes(path: Path) -> bytes:
    value = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        return value.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return value


def sha256_file(path: Path) -> str:
    return sha256_bytes(canonical_file_bytes(path))


def tree_hash(root: Path) -> str:
    files = {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in root.rglob("*")
        if path.is_file()
    }
    return tree_hash_from_entries(files)


def tree_hash_from_entries(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(files):
        file_hash = files[relative]
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def pinned_paths() -> dict[str, Path]:
    paths = {relative: EVAL_ROOT / relative for relative in PINNED_FILES}
    for path in sorted((EVAL_ROOT / "fixtures").rglob("*")):
        if path.is_file():
            paths[path.relative_to(EVAL_ROOT).as_posix()] = path
    return paths


def current_snapshot() -> dict:
    paths = pinned_paths()
    missing = [relative for relative, path in paths.items() if not path.is_file()]
    if missing:
        raise ValueError(f"cannot freeze missing evaluation files: {missing}")
    return {
        "treatment_tree_sha256": tree_hash(SKILL_ROOT),
        "files": {
            relative: sha256_file(path)
            for relative, path in paths.items()
        },
    }


def lock_sha256(lock: dict) -> str:
    payload = json.dumps(lock, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def load_lock() -> dict:
    if not LOCK_PATH.is_file():
        raise ValueError(
            "evaluation-lock.json is missing; run freeze_evaluation.py before any model session"
        )
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if lock.get("schema_version") != 1:
        raise ValueError("unsupported evaluation lock schema")
    return lock


def validate_current_lock() -> dict:
    lock = load_lock()
    expected = {
        "treatment_tree_sha256": lock.get("treatment_tree_sha256"),
        "files": lock.get("files"),
    }
    actual = current_snapshot()
    if actual != expected:
        changed = [
            key
            for key in sorted(set(actual["files"]) | set(expected.get("files") or {}))
            if actual["files"].get(key) != (expected.get("files") or {}).get(key)
        ]
        if actual["treatment_tree_sha256"] != expected["treatment_tree_sha256"]:
            changed.insert(0, "skills/code-territory-guide")
        raise ValueError(f"evaluation lock mismatch; refreeze intentionally: {changed}")
    return lock


def validate_lock(attempt: int) -> dict:
    lock = validate_current_lock()
    minimum = lock.get("preregistered_for_attempts_gte")
    if not isinstance(minimum, int) or attempt < minimum:
        raise ValueError(
            f"attempt {attempt} is not preregistered by this lock; minimum is {minimum}"
        )
    return lock


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--minimum-attempt", type=int, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.minimum_attempt < 1:
        raise SystemExit("--minimum-attempt must be positive")
    if LOCK_PATH.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite {LOCK_PATH}; pass --force intentionally")
    snapshot = current_snapshot()
    lock = {
        "schema_version": 1,
        "release_id": args.release_id,
        "preregistered_for_attempts_gte": args.minimum_attempt,
        "historical_evidence": {
            "through_attempt": args.minimum_attempt - 1,
            "status": "not preregistered by this lock",
        },
        **snapshot,
    }
    LOCK_PATH.write_text(
        json.dumps(lock, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {LOCK_PATH} sha256={lock_sha256(lock)}")


if __name__ == "__main__":
    main()
