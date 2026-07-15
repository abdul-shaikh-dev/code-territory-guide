from __future__ import annotations

import json
import re
from pathlib import Path

from freeze_evaluation import LOCK_PATH, load_lock, lock_sha256, tree_hash


EVAL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EVAL_ROOT.parent
MANIFEST_PATH = EVAL_ROOT / "real-repo-writable-manifest.json"
SCHEMA_PATH = EVAL_ROOT / "real-repo-writable-run.schema.json"
RUN_ROOT = EVAL_ROOT / "results" / "real-repos-writable" / "runs"
JUDGE_ROOT = EVAL_ROOT / "results" / "real-repos-writable" / "judgments"
REPORT = EVAL_ROOT / "results" / "real-repository-writable-evidence.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(record: dict, names: set[str], path: Path) -> None:
    missing = sorted(names - set(record))
    if missing:
        raise ValueError(f"missing keys in {path}: {missing}")


def validate_manifest(manifest: dict) -> None:
    if manifest.get("schema_version") != 2:
        raise ValueError("unsupported writable manifest schema")
    if manifest.get("evaluation_phase") != "preregistered-writable":
        raise ValueError("writable manifest must be preregistered")
    case_ids = [case["id"] for case in manifest["cases"]]
    repo_ids = [case["repo"] for case in manifest["cases"]]
    if len(case_ids) != 3 or len(case_ids) != len(set(case_ids)):
        raise ValueError("writable manifest requires three unique cases")
    if len(repo_ids) != len(set(repo_ids)):
        raise ValueError("writable manifest requires one case per repository")
    if manifest.get("execution") != {
        "sandbox": "workspace-write",
        "windows_sandbox": "elevated",
        "approval_policy": "never",
        "network": "prohibited",
        "require_local_commit": True,
    }:
        raise ValueError("unexpected writable execution policy")
    required_case = {
        "id",
        "repo",
        "base_commit",
        "model",
        "reasoning_effort",
        "commit_convention",
        "commit_subject_pattern",
        "provisioned_paths",
        "validation_commands",
        "query",
        "expected_behavior",
        "forbidden_behavior",
    }
    for case in manifest["cases"]:
        require(case, required_case, MANIFEST_PATH)
        if len(case["base_commit"]) != 40:
            raise ValueError(f"invalid base commit for {case['id']}")
        if not case["validation_commands"]:
            raise ValueError(f"missing validation commands for {case['id']}")
        if case["reasoning_effort"] not in {"medium", "high"}:
            raise ValueError(f"unexpected reasoning effort for {case['id']}")
        if not any(item["critical"] for item in case["expected_behavior"]):
            raise ValueError(f"missing critical criteria for {case['id']}")


def main() -> None:
    manifest = load(MANIFEST_PATH)
    load(SCHEMA_PATH)
    validate_manifest(manifest)
    skill_hash = tree_hash(REPO_ROOT / "skills" / "code-territory-guide")
    if skill_hash != manifest["frozen_treatment_sha256"]:
        raise ValueError("current skill does not match writable manifest")
    if LOCK_PATH.is_file():
        lock = load_lock()
        if lock["treatment_tree_sha256"] != manifest["frozen_treatment_sha256"]:
            raise ValueError("active lock does not match writable manifest")
        expected_lock = lock_sha256(lock)
        minimum_attempt = lock["preregistered_for_attempts_gte"]
    else:
        expected_lock = None
        minimum_attempt = None

    cases = {case["id"]: case for case in manifest["cases"]}
    run_paths = sorted(RUN_ROOT.glob("*.json"))
    judge_paths = sorted(
        path
        for path in JUDGE_ROOT.glob("*.json")
        if not path.name.endswith(".output.json")
    )
    if not run_paths and not judge_paths and not REPORT.exists():
        print("validated writable manifest and schema; no generated evidence is present")
        return

    required_run = set(load(SCHEMA_PATH)["required"])
    for path in run_paths:
        record = load(path)
        require(record, required_run, path)
        if path.stem != record["run_id"]:
            raise ValueError(f"filename/run identity mismatch: {path}")
        case = cases.get(record["case_id"])
        if case is None:
            raise ValueError(f"unregistered case: {path}")
        expected_id = (
            f"{case['id']}--{record['arm']}--attempt-{record['attempt']}"
        )
        if record["run_id"] != expected_id:
            raise ValueError(f"malformed run identity: {path}")
        if record["repo"] != case["repo"]:
            raise ValueError(f"repository mismatch: {path}")
        if record["seed"]["head"] != case["base_commit"]:
            raise ValueError(f"unregistered seed commit: {path}")
        if (record["model"], record["reasoning_effort"]) != (
            case["model"],
            case["reasoning_effort"],
        ):
            raise ValueError(f"model routing mismatch: {path}")
        if record["execution"]["sandbox"] != "workspace-write":
            raise ValueError(f"execution mode mismatch: {path}")
        prospective = (
            minimum_attempt is not None and record["attempt"] >= minimum_attempt
        )
        if prospective:
            if record["execution"].get("windows_sandbox") != "elevated":
                raise ValueError(f"Windows sandbox backend mismatch: {path}")
            if record["evaluation_lock"]["sha256"] != expected_lock:
                raise ValueError(f"evaluation lock mismatch: {path}")
        if record["repository_after"]["fetch_url"] != "DISABLED":
            raise ValueError(f"fetch remote enabled: {path}")
        if record["repository_after"]["push_url"] != "DISABLED":
            raise ValueError(f"push remote enabled: {path}")
        if record["treatment"]["installed"] and (
            record["treatment"]["tree_sha256"]
            != record["treatment"]["tree_sha256_after"]
        ):
            raise ValueError(f"treatment mutation: {path}")

    if REPORT.exists():
        text = REPORT.read_text(encoding="utf-8")
        required_phrases = [
            "separate disposable local clone",
            "exactly one local commit",
            "Network denial was not independently enforced",
            "does not establish universal quality uplift",
        ]
        missing = [value for value in required_phrases if value not in text]
        if missing:
            raise ValueError(f"writable report missing qualifications: {missing}")
        run_match = re.search(r"^- Run attempt: (\d+)$", text, flags=re.MULTILINE)
        judge_match = re.search(
            r"^- Judge attempt: (\d+)$", text, flags=re.MULTILINE
        )
        if not run_match or not judge_match:
            raise ValueError("writable report does not identify selected attempts")
        run_attempt = int(run_match.group(1))
        judge_attempt = int(judge_match.group(1))
        for case_id in cases:
            for arm in ("baseline", "installed-skill"):
                path = RUN_ROOT / f"{case_id}--{arm}--attempt-{run_attempt}.json"
                if not path.is_file() or load(path)["excluded"]["value"]:
                    raise ValueError(f"missing valid selected run: {path}")
            path = JUDGE_ROOT / f"{case_id}--judge-attempt-{judge_attempt}.json"
            if not path.is_file():
                raise ValueError(f"missing selected judgment: {path}")
            judgment = load(path)
            if judgment["excluded"]["value"] or not judgment.get("judgment"):
                raise ValueError(f"invalid selected judgment: {path}")
    print(
        f"validated writable manifest, schema, {len(run_paths)} runs, "
        f"{len(judge_paths)} judgments, report_present={REPORT.exists()}"
    )


if __name__ == "__main__":
    main()
