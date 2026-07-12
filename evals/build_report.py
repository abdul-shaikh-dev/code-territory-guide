from __future__ import annotations

import json
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parent
JUDGMENT_ROOT = EVAL_ROOT / "results" / "judgments"
OUTPUT = EVAL_ROOT / "results" / "synthetic-evidence.md"
MANIFEST = json.loads((EVAL_ROOT / "manifest.json").read_text(encoding="utf-8"))
CASES = {case["id"]: case for case in MANIFEST["cases"]}
RUN_ROOT = EVAL_ROOT / "results" / "runs"


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


def judgment_issue(record: dict, runs: list[dict]) -> str | None:
    case = CASES.get(record.get("case_id"))
    if case is None:
        return "removed case"
    if len(runs) != 2:
        return "missing pair"
    if any(
        not run.get("harness_revision") or not run.get("routing")
        for run in runs
    ):
        return "legacy provenance"
    if len({run["harness_revision"] for run in runs}) != 1:
        return "harness mismatch"
    if len({run["routing_sha256"] for run in runs}) != 1:
        return "routing mismatch"
    if len({run["query"] for run in runs}) != 1 or runs[0]["query"] != expected_query(case):
        return "stale prompt"
    judgment = record.get("judgment")
    if not judgment:
        return "missing judgment"
    expected_ids = [item["id"] for item in case["expected_behavior"]]
    forbidden = case["forbidden_behavior"]
    critical_ids = {
        item["id"] for item in case["expected_behavior"] if item["critical"]
    }
    for arm_name in ("baseline", "treatment"):
        arm = judgment.get(arm_name, {})
        if [item.get("id") for item in arm.get("criteria", [])] != expected_ids:
            return "stale rubric"
        if [
            item.get("description") for item in arm.get("forbidden", [])
        ] != forbidden:
            return "stale rubric"
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


def latest_valid_run(case_id: str, arm: str) -> Path | None:
    candidates = []
    for path in RUN_ROOT.glob(f"{case_id}--{arm}--attempt-*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("schema_version") == 2 and not record.get("excluded", {}).get("value"):
            candidates.append((record["attempt"], path))
    return max(candidates, default=(None, None), key=lambda item: item[0])[1]


def load_latest_valid_judgments() -> list[dict]:
    latest: dict[str, tuple[int, dict]] = {}
    for path in sorted(JUDGMENT_ROOT.glob("*.attempt-*.json")):
        if path.name.endswith(".judge-output.json"):
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("excluded", {}).get("value") or not record.get("judgment"):
            continue
        inputs = [EVAL_ROOT / relative for relative in record.get("input_records", [])]
        if len(inputs) != 2 or not all(path.is_file() for path in inputs):
            continue
        input_records = [json.loads(path.read_text(encoding="utf-8")) for path in inputs]
        if not all(item.get("schema_version") == 2 for item in input_records):
            continue
        if judgment_issue(record, input_records):
            continue
        expected_inputs = [
            latest_valid_run(record["case_id"], "baseline"),
            latest_valid_run(record["case_id"], "installed-skill"),
        ]
        if inputs != expected_inputs:
            continue
        attempt = int(record["judge_run_id"].rsplit("-", 1)[-1])
        current = latest.get(record["case_id"])
        if current is None or attempt > current[0]:
            latest[record["case_id"]] = (attempt, record)
    return [latest[key][1] for key in sorted(latest)]


def mark(value: bool) -> str:
    return "pass" if value else "fail"


def judgment_attempt(record: dict) -> int:
    return int(record["judge_run_id"].rsplit("-", 1)[-1])


def selected_run_attempt(record: dict) -> int:
    path = EVAL_ROOT / record["input_records"][0]
    return json.loads(path.read_text(encoding="utf-8"))["attempt"]


def selected_runs(records: list[dict]) -> list[dict]:
    return [
        json.loads((EVAL_ROOT / relative).read_text(encoding="utf-8"))
        for record in records
        for relative in record["input_records"]
    ]


def valid_current_judgment_history() -> list[dict]:
    history = []
    for path in sorted(JUDGMENT_ROOT.glob("*.attempt-*.json")):
        if path.name.endswith(".judge-output.json"):
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("excluded", {}).get("value") or not record.get("judgment"):
            continue
        inputs = [EVAL_ROOT / relative for relative in record.get("input_records", [])]
        if len(inputs) != 2 or not all(item.is_file() for item in inputs):
            continue
        runs = [json.loads(item.read_text(encoding="utf-8")) for item in inputs]
        if all(run.get("schema_version") == 2 for run in runs):
            history.append(record)
    return sorted(history, key=lambda item: (item["case_id"], judgment_attempt(item)))


def history_state(record: dict) -> str:
    inputs = [EVAL_ROOT / relative for relative in record.get("input_records", [])]
    if len(inputs) != 2 or not all(path.is_file() for path in inputs):
        return "missing pair"
    runs = [json.loads(path.read_text(encoding="utf-8")) for path in inputs]
    issue = judgment_issue(record, runs)
    if issue:
        return issue
    return evidence_state(record)


def environment_limited(record: dict) -> bool:
    inputs = [EVAL_ROOT / relative for relative in record.get("input_records", [])]
    if len(inputs) != 2 or not all(path.is_file() for path in inputs):
        return False
    markers = ("writing is blocked by read-only sandbox", "rejected: blocked by policy")
    run_records = [json.loads(path.read_text(encoding="utf-8")) for path in inputs]
    return all(any(marker in item.get("tool_log", "") for marker in markers) for item in run_records)


def evidence_state(record: dict) -> str:
    inputs = [EVAL_ROOT / relative for relative in record.get("input_records", [])]
    runs = [json.loads(path.read_text(encoding="utf-8")) for path in inputs]
    if runs[0]["fixture"]["tree_sha256"] != runs[1]["fixture"]["tree_sha256"]:
        return "non-comparable fixture mismatch"
    if environment_limited(record):
        return "environment-limited"
    return "scoreable"


def main() -> None:
    records = load_latest_valid_judgments()
    if not records:
        raise SystemExit("no valid judgments found; run judge_matrix.py first")
    runs = selected_runs(records)
    treatment_hashes = {
        run["treatment"].get("tree_sha256")
        for run in runs
        if run["arm"] == "installed-skill"
    }
    if len(treatment_hashes) != 1:
        raise SystemExit(
            "selected judgments use multiple treatment payloads; rerun a frozen full matrix "
            f"before building an aggregate report: {sorted(treatment_hashes)}"
        )

    baseline = sum(record["judgment"]["baseline"]["pass"] for record in records)
    treatment = sum(record["judgment"]["treatment"]["pass"] for record in records)
    outcomes = {name: 0 for name in ("improved", "preserved", "regressed", "inconclusive")}
    for record in records:
        outcomes[record["judgment"]["comparison"]["outcome"]] += 1
    limited = sum(environment_limited(record) for record in records)

    lines = [
        "# Synthetic Behavioral Evidence",
        "",
        "> Generated from the latest valid judgment for each case. Raw runs and judgments are local, ignored artifacts.",
        "",
        "## Result",
        "",
        f"- Cases judged: {len(records)}/{len(MANIFEST['cases'])} manifest cases",
        f"- Baseline passes: {baseline}/{len(records)}",
        f"- Installed-skill passes: {treatment}/{len(records)}",
        f"- Pairwise outcomes: {outcomes['improved']} improved, {outcomes['preserved']} preserved, "
        f"{outcomes['regressed']} regressed, {outcomes['inconclusive']} inconclusive",
        f"- Environment-limited pairs: {limited}/{len(records)}",
        "",
        "| Case | Run attempt | Judge attempt | Baseline | Skill | Comparison | Evidence state |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for record in records:
        judgment = record["judgment"]
        lines.append(
            f"| `{record['case_id']}` | {selected_run_attempt(record)} | {judgment_attempt(record)} | "
            f"{mark(judgment['baseline']['pass'])} | "
            f"{mark(judgment['treatment']['pass'])} | {judgment['comparison']['outcome']} | "
            f"{evidence_state(record)} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "This report measures behavior under the declared rubric. It does not prove universal quality uplift, "
        "production safety, or performance on tasks outside the manifest. Inspect the preserved local run and "
        "judgment records before making stronger claims.",
        "",
        (
            f"Coverage includes all {len(records)} current-schema scoreable cases."
            if len(records) == len(MANIFEST["cases"])
            else (
                f"Coverage is limited to {len(records)} of {len(MANIFEST['cases'])} current-schema scoreable cases. "
                "The remaining cases have only legacy, excluded, or not-yet-rerun evidence under the current harness."
            )
        ),
        "",
        "All selected runs used explicitly authorized unsandboxed execution inside disposable, disabled-remote "
        "fixtures. These results do not establish behavior under the ordinary sandboxed path.",
        "",
        "Judgments were produced by separate Sol/medium evaluator calls with installed skill output redacted. "
        "For Sol/medium treatment cases this is evaluator-call separation, not model independence.",
        "",
        "The harness appends the same repository boundary and validation reminder to both arms. Results are "
        "within-harness comparisons and do not isolate the skill from that shared prompt framing.",
        "",
        (
            "All selected runs record the same harness revision and an exact per-case routing snapshot."
            if all(run.get("harness_revision") and run.get("routing") for run in runs)
            and len({run["harness_revision"] for run in runs}) == 1
            else (
                "Some selected historical records predate exact harness or routing snapshots, so their execution "
                "configuration is not independently recoverable."
            )
        ),
        "",
        "An environment-limited pair retains its separate-call judge outcome, but cannot establish writable artifact, "
        "commit, hook, or multi-repository implementation behavior when both arms were denied shell execution or writes.",
        "",
        "## Retry history",
        "",
        "| Case | Run attempt | Judge attempt | Baseline | Skill | Comparison | Evidence state |",
        "|---|---:|---:|---:|---:|---|---|",
    ])
    for record in valid_current_judgment_history():
        judgment = record["judgment"]
        lines.append(
            f"| `{record['case_id']}` | {selected_run_attempt(record)} | {judgment_attempt(record)} | "
            f"{mark(judgment['baseline']['pass'])} | {mark(judgment['treatment']['pass'])} | "
            f"{judgment['comparison']['outcome']} | "
            f"{history_state(record)} |"
        )
    lines.append("")
    lines.extend([
        "## Current-schema run inventory",
        "",
        "| Case | Baseline attempts | Treatment attempts | Judged paired attempts |",
        "|---|---|---|---|",
    ])
    for case_id in sorted({record["case_id"] for record in records}):
        arms = {}
        for arm in ("baseline", "installed-skill"):
            values = []
            for path in sorted(RUN_ROOT.glob(f"{case_id}--{arm}--attempt-*.json")):
                run = json.loads(path.read_text(encoding="utf-8"))
                if run.get("schema_version") != 2:
                    continue
                label = str(run["attempt"])
                if run.get("excluded", {}).get("value"):
                    label += " excluded"
                values.append(label)
            arms[arm] = ", ".join(values) or "none"
        judged = sorted(
            {
                selected_run_attempt(item)
                for item in valid_current_judgment_history()
                if item["case_id"] == case_id
            }
        )
        lines.append(
            f"| `{case_id}` | {arms['baseline']} | {arms['installed-skill']} | "
            f"{', '.join(map(str, judged)) or 'none'} |"
        )
    lines.append("")
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
