from __future__ import annotations

import json
import sys
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EVAL_ROOT.parent
RUN_ROOT = EVAL_ROOT / "results" / "real-repos" / "runs"
REPORT = EVAL_ROOT / "results" / "generated" / "real-repository-readonly.md"

sys.path.insert(0, str(EVAL_ROOT))
from build_real_repo_report import SELECTED, validate_selected  # noqa: E402
from run_real_repo_eval import SKILL_SOURCE, tree_hash  # noqa: E402


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    manifest = load(EVAL_ROOT / "real-repo-manifest.json")
    skill_hash, _ = tree_hash(SKILL_SOURCE)
    current_skill_matches_evidence = skill_hash == manifest["frozen_treatment_sha256"]

    runs = [load(path) for path in sorted(RUN_ROOT.glob("*.json"))]
    if len(runs) != 9:
        raise ValueError(f"expected 9 preserved runs, found {len(runs)}")
    for record in runs:
        if record["excluded"]["value"]:
            raise ValueError(f"unexpected excluded run: {record['run_id']}")
        if record["repository_before"] != record["repository_after"]:
            raise ValueError(f"repository state changed: {record['run_id']}")
        if record["repository_before"]["push_url"] != "DISABLED":
            raise ValueError(f"push URL enabled: {record['run_id']}")
        treatment = record["treatment"]
        if treatment["installed"] and treatment["tree_sha256"] != treatment["tree_sha256_after"]:
            raise ValueError(f"treatment changed: {record['run_id']}")

    for case_id, pick in SELECTED.items():
        baseline, treatment, judgment = validate_selected(case_id, pick)
        if treatment["treatment"]["tree_sha256"] != manifest["frozen_treatment_sha256"]:
            raise ValueError(f"selected treatment does not match frozen hash: {case_id}")
        if not judgment["baseline"]["pass"] or not judgment["treatment"]["pass"]:
            raise ValueError(f"selected arm failed: {case_id}")
        if judgment["comparison"]["outcome"] != "preserved":
            raise ValueError(f"unexpected comparison outcome: {case_id}")
        if (baseline["model"], baseline["reasoning_effort"]) != (treatment["model"], treatment["reasoning_effort"]):
            raise ValueError(f"selected route mismatch: {case_id}")

    text = REPORT.read_text(encoding="utf-8")
    required_phrases = [
        "adaptive development exercise",
        "no uplift under the preregistered binary rubric",
        "All nine recorded runs are retained",
        "network denial was not independently enforced",
        "development evidence, not a causal estimate",
        "Not established: writable behavior",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in text]
    if missing:
        raise ValueError(f"report is missing required qualifications: {missing}")

    print(
        "validated frozen treatment hash against selected runs, 9 preserved runs, 4 selected arms, "
        "2 matched judgments, repository/push/treatment integrity, and qualified report claims; "
        f"current skill matches historical treatment={current_skill_matches_evidence}"
    )


if __name__ == "__main__":
    main()
