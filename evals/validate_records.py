from __future__ import annotations

import json
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parent

RUN_REQUIRED = {
    "schema_version", "run_id", "case_id", "arm", "attempt", "started_at", "finished_at",
    "harness", "model", "reasoning_effort", "routing_sha256", "query", "fixture", "treatment",
    "raw_output", "tool_log", "worktree_before", "worktree_after", "diff", "files_before",
    "files_after", "changed_files", "tool_events", "repository_before", "repository_after",
    "exit_status", "excluded",
}


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


def main() -> None:
    for schema in ("run-record.schema.json", "judge-output.schema.json"):
        load(EVAL_ROOT / schema)

    candidates = sorted((EVAL_ROOT / "results" / "runs").glob("*.json"))
    run_paths = []
    legacy_paths = []
    for path in candidates:
        record = load(path)
        if record.get("schema_version") != 2:
            legacy_paths.append(path)
            continue
        if path.stem != record.get("run_id"):
            raise ValueError(f"filename/run_id mismatch in {path}")
        require(record, RUN_REQUIRED, path)
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
        if not all(item.get("schema_version") == 2 for item in input_records):
            legacy_judgments.append(path)
            continue
        judge_paths.append(path)

    print(
        f"validated schemas, {len(run_paths)} canonical runs, and {len(judge_paths)} canonical judgments; "
        f"ignored {len(legacy_paths)} legacy runs and {len(legacy_judgments)} legacy judgments"
    )


if __name__ == "__main__":
    main()
