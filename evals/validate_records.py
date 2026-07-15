from __future__ import annotations

import json
from pathlib import Path

from evaluation_integrity import judgment_issue
from freeze_evaluation import LOCK_PATH, lock_sha256, validate_current_lock


EVAL_ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((EVAL_ROOT / "manifest.json").read_text(encoding="utf-8"))
CASES = {case["id"]: case for case in MANIFEST["cases"]}

RUN_REQUIRED = {
    "schema_version", "run_id", "case_id", "arm", "attempt", "started_at", "finished_at",
    "harness", "model", "reasoning_effort", "routing_sha256", "query", "fixture", "treatment",
    "raw_output", "tool_log", "worktree_before", "worktree_after", "diff", "files_before",
    "files_after", "changed_files", "tool_events", "repository_before", "repository_after",
    "exit_status", "excluded",
}
REPORTABLE_REQUIRED = {
    "harness_revision", "execution_mode", "execution_authorization", "routing"
}
V3_REQUIRED = REPORTABLE_REQUIRED | {"evaluation_lock"}


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON: {path}: {error}") from error


def require(record: dict, required: set[str], path: Path) -> None:
    missing = sorted(required - set(record))
    if missing:
        raise ValueError(f"missing keys in {path}: {missing}")
    if not isinstance(record["excluded"], dict) or not isinstance(record["excluded"].get("value"), bool):
        raise ValueError(f"invalid exclusion in {path}")


def expected_lock_for_attempt(
    attempt: int,
    active_lock: dict | None,
    active_lock_sha256: str | None,
) -> str | None:
    if active_lock is None or active_lock_sha256 is None:
        return None
    minimum = active_lock["preregistered_for_attempts_gte"]
    return active_lock_sha256 if attempt >= minimum else None


def main() -> None:
    active_lock = None
    expected_lock = None
    if LOCK_PATH.is_file():
        active_lock = validate_current_lock()
        expected_lock = lock_sha256(active_lock)
    for schema in (
        "run-record.schema.json",
        "judge-output.schema.json",
        "judge-blind-output.schema.json",
    ):
        load(EVAL_ROOT / schema)

    candidates = sorted((EVAL_ROOT / "results" / "runs").glob("*.json"))
    run_paths = []
    legacy_paths = []
    for path in candidates:
        record = load(path)
        if record.get("schema_version") not in {2, 3}:
            legacy_paths.append(path)
            continue
        if path.stem != record.get("run_id"):
            raise ValueError(f"filename/run_id mismatch in {path}")
        require(record, RUN_REQUIRED, path)
        if record["schema_version"] == 3:
            require(record, V3_REQUIRED, path)
            lock = record["evaluation_lock"]
            if not lock.get("preregistered") or not lock.get("sha256"):
                raise ValueError(f"invalid evaluation lock in {path}")
            record_lock = expected_lock_for_attempt(
                record["attempt"],
                active_lock,
                expected_lock,
            )
            if record_lock and lock["sha256"] != record_lock:
                raise ValueError(f"run does not match active evaluation lock: {path}")
        run_paths.append(path)
        if record["treatment"].get("installed") and not record["treatment"].get("tree_sha256"):
            raise ValueError(f"missing treatment hash in {path}")

    judge_candidates = sorted((EVAL_ROOT / "results" / "judgments").glob("*.attempt-*.json"))
    judge_candidates = [path for path in judge_candidates if not path.name.endswith(".judge-output.json")]
    judge_paths = []
    legacy_judgments = []
    for path in judge_candidates:
        record = load(path)
        expected_prefix = f"{record.get('case_id')}.attempt-"
        if not path.stem.startswith(expected_prefix):
            raise ValueError(f"filename/case_id mismatch in {path}")
        if record.get("excluded", {}).get("value"):
            continue
        if not record.get("judgment"):
            raise ValueError(f"missing judgment: {path}")
        inputs = [EVAL_ROOT / relative for relative in record.get("input_records", [])]
        if len(inputs) != 2 or not all(item.is_file() for item in inputs):
            legacy_judgments.append(path)
            continue
        input_records = [load(item) for item in inputs]
        if not all(item.get("schema_version") in {2, 3} for item in input_records):
            legacy_judgments.append(path)
            continue
        case = CASES.get(record.get("case_id"))
        if case is None:
            raise ValueError(f"unknown judgment case: {path}")
        pair_lock = expected_lock_for_attempt(
            input_records[0]["attempt"],
            active_lock,
            expected_lock,
        )
        issue = judgment_issue(
            case,
            record,
            input_records[0],
            input_records[1],
            pair_lock,
        )
        if issue and (
            any(item.get("schema_version") == 3 for item in input_records)
            or record.get("blinding") is not None
        ):
            raise ValueError(f"{issue}: {path}")
        judge_paths.append(path)

    print(
        f"validated schemas, {len(run_paths)} canonical runs, and {len(judge_paths)} canonical judgments; "
        f"ignored {len(legacy_paths)} legacy runs and {len(legacy_judgments)} legacy judgments"
    )
    reportable = sum(
        REPORTABLE_REQUIRED <= set(load(path))
        for path in run_paths
    )
    print(
        f"{reportable}/{len(run_paths)} canonical runs contain complete reportable provenance"
    )


if __name__ == "__main__":
    main()
