from __future__ import annotations

def expected_query(case: dict) -> str:
    if case["id"] == "multi-repository-expedition":
        boundary = (
            "Work only in the named coordination, api, and worker repositories directly inside the current workspace. "
            "The common workspace is not a Git repository or artifact destination. Do not search its parent or user-profile directories."
        )
    else:
        boundary = (
            "Work only in the current repository. Do not search parent directories or user-profile directories."
        )
    return (
        case["query"]
        + "\n\n"
        + boundary
        + " Preserve unrelated existing changes and use each repository's own validation instructions."
    )


def expected_outcome(baseline_pass: bool, treatment_pass: bool) -> str:
    if treatment_pass and not baseline_pass:
        return "improved"
    if baseline_pass and not treatment_pass:
        return "regressed"
    return "preserved"


def pair_issue(
    case: dict,
    baseline: dict,
    treatment: dict,
    expected_lock_sha256: str | None = None,
) -> str | None:
    case_id = case["id"]
    if baseline.get("arm") != "baseline" or treatment.get("arm") != "installed-skill":
        return "arm identity mismatch"
    if baseline.get("case_id") != case_id or treatment.get("case_id") != case_id:
        return "case identity mismatch"
    if baseline.get("attempt") != treatment.get("attempt"):
        return "attempt mismatch"
    if baseline.get("excluded", {}).get("value") or treatment.get("excluded", {}).get("value"):
        return "excluded run"
    if baseline.get("query") != treatment.get("query"):
        return "paired prompt mismatch"
    if baseline.get("query") != expected_query(case):
        return "stale prompt"
    if baseline.get("fixture", {}).get("tree_sha256") != treatment.get("fixture", {}).get("tree_sha256"):
        return "fixture mismatch"
    if baseline.get("routing_sha256") != treatment.get("routing_sha256"):
        return "routing mismatch"
    if (baseline.get("model"), baseline.get("reasoning_effort")) != (
        treatment.get("model"),
        treatment.get("reasoning_effort"),
    ):
        return "paired model mismatch"
    if baseline.get("harness_revision") != treatment.get("harness_revision"):
        return "harness mismatch"
    if baseline.get("treatment", {}).get("installed"):
        return "baseline contains treatment"
    payload = treatment.get("treatment", {})
    if not payload.get("installed"):
        return "treatment not installed"
    if payload.get("tree_sha256") != payload.get("tree_sha256_after"):
        return "treatment mutation"
    versions = {baseline.get("schema_version"), treatment.get("schema_version")}
    if 3 in versions:
        if versions != {3}:
            return "schema mismatch"
        locks = [baseline.get("evaluation_lock", {}), treatment.get("evaluation_lock", {})]
        if any(not item.get("preregistered") for item in locks):
            return "run not preregistered"
        if len({item.get("sha256") for item in locks}) != 1:
            return "evaluation lock mismatch"
        if expected_lock_sha256 and locks[0].get("sha256") != expected_lock_sha256:
            return "active evaluation lock mismatch"
    return None


def arm_judgment_issue(case: dict, arm: dict, run: dict) -> str | None:
    if arm.get("run_id") != run.get("run_id"):
        return "judgment run identity mismatch"
    expected_ids = [item["id"] for item in case["expected_behavior"]]
    if [item.get("id") for item in arm.get("criteria", [])] != expected_ids:
        return "stale rubric"
    forbidden = case["forbidden_behavior"]
    if [item.get("description") for item in arm.get("forbidden", [])] != forbidden:
        return "stale rubric"
    critical_ids = {
        item["id"] for item in case["expected_behavior"] if item["critical"]
    }
    critical_pass = all(
        item["passed"]
        for item in arm["criteria"]
        if item["id"] in critical_ids
    )
    passed = critical_pass and not any(
        item["occurred"] for item in arm["forbidden"]
    )
    if arm.get("critical_pass") != critical_pass or arm.get("pass") != passed:
        return "inconsistent pass fields"
    return None


def judgment_issue(
    case: dict,
    record: dict,
    baseline: dict,
    treatment: dict,
    expected_lock_sha256: str | None = None,
) -> str | None:
    issue = pair_issue(case, baseline, treatment, expected_lock_sha256)
    if issue:
        return issue
    if record.get("case_id") != case["id"]:
        return "judgment case identity mismatch"
    judgment = record.get("judgment")
    if not judgment:
        return "missing judgment"
    for name, run in (("baseline", baseline), ("treatment", treatment)):
        issue = arm_judgment_issue(case, judgment.get(name, {}), run)
        if issue:
            return issue
    expected = expected_outcome(
        judgment["baseline"]["pass"],
        judgment["treatment"]["pass"],
    )
    if judgment.get("comparison", {}).get("outcome") != expected:
        return "inconsistent comparison outcome"
    blinding = record.get("blinding")
    if blinding is not None:
        if not blinding.get("enabled"):
            return "judge not blinded"
        if not blinding.get("judge_model_is_independent"):
            return "judge model not independent"
        if blinding.get("source_model") == record.get("model"):
            return "judge model matches source model"
        assignment = blinding.get("assignment", {})
        if set(assignment) != {"candidate_a", "candidate_b"}:
            return "invalid blind assignment"
        if set(assignment.values()) != {"baseline", "treatment"}:
            return "invalid blind assignment"
    return None
