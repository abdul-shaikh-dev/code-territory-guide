from __future__ import annotations

import json
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parent

V1_REQUIRED = {
    "run_id", "case_id", "arm", "seed", "started_at", "finished_at", "harness", "model",
    "reasoning_effort", "query", "context", "treatment", "raw_output", "exit_status",
    "excluded", "criteria", "forbidden", "scorer",
}
V2_REQUIRED = {
    "schema_version", "run_id", "case_id", "arm", "attempt", "started_at", "finished_at",
    "harness", "model", "reasoning_effort", "routing_sha256", "query", "fixture", "treatment",
    "raw_output", "tool_log", "worktree_before", "worktree_after", "diff", "files_before",
    "files_after", "changed_files", "tool_events", "exit_status", "excluded",
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
    for schema in ("run-record.schema.json", "run-record-v2.schema.json", "judge-output.schema.json"):
        load(EVAL_ROOT / schema)

    v1_paths = sorted((EVAL_ROOT / "results" / "runs").glob("*.json"))
    for path in v1_paths:
        require(load(path), V1_REQUIRED, path)

    v2_paths = sorted((EVAL_ROOT / "results" / "runs-v2").glob("*.json"))
    for path in v2_paths:
        record = load(path)
        require(record, V2_REQUIRED, path)
        if record["schema_version"] != 2:
            raise ValueError(f"wrong schema_version in {path}")
        if record["treatment"].get("installed") and not record["treatment"].get("tree_sha256"):
            raise ValueError(f"missing treatment hash in {path}")

    judge_paths = sorted((EVAL_ROOT / "results" / "judgments").glob("*.attempt-2.json"))
    judge_paths = [path for path in judge_paths if not path.name.endswith(".judge-output.json")]
    for path in judge_paths:
        record = load(path)
        if record.get("excluded", {}).get("value"):
            raise ValueError(f"valid-judgment set contains exclusion: {path}")
        if not record.get("judgment"):
            raise ValueError(f"missing judgment: {path}")

    print(f"validated schemas, {len(v1_paths)} v1 runs, {len(v2_paths)} v2 runs, and {len(judge_paths)} judgments")


if __name__ == "__main__":
    main()
