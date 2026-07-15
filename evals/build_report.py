from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from evaluation_integrity import judgment_issue
from freeze_evaluation import LOCK_PATH, lock_sha256, validate_current_lock


EVAL_ROOT = Path(__file__).resolve().parent
JUDGMENT_ROOT = EVAL_ROOT / "results" / "judgments"
RUN_ROOT = EVAL_ROOT / "results" / "runs"
OUTPUT = EVAL_ROOT / "results" / "synthetic-evidence.md"
MANIFEST = json.loads((EVAL_ROOT / "manifest.json").read_text(encoding="utf-8"))
CASES = {case["id"]: case for case in MANIFEST["cases"]}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def active_lock() -> tuple[dict | None, str | None]:
    if not LOCK_PATH.is_file():
        return None, None
    lock = validate_current_lock()
    return lock, lock_sha256(lock)


def latest_valid_run(case_id: str, arm: str) -> Path | None:
    candidates: list[tuple[int, Path]] = []
    for path in RUN_ROOT.glob(f"{case_id}--{arm}--attempt-*.json"):
        record = load(path)
        if record.get("schema_version") in (2, 3) and not record.get("excluded", {}).get("value"):
            candidates.append((record["attempt"], path))
    return max(candidates, default=(None, None), key=lambda item: item[0])[1]


def record_inputs(record: dict) -> tuple[list[Path], list[dict]]:
    paths = [EVAL_ROOT / relative for relative in record.get("input_records", [])]
    if len(paths) != 2 or not all(path.is_file() for path in paths):
        return paths, []
    runs = [load(path) for path in paths]
    by_arm = {run.get("arm"): run for run in runs}
    if set(by_arm) != {"baseline", "installed-skill"}:
        return paths, []
    return paths, [by_arm["baseline"], by_arm["installed-skill"]]


def record_issue(record: dict, expected_lock: str | None = None) -> str | None:
    case = CASES.get(record.get("case_id"))
    if case is None:
        return "removed case"
    _, runs = record_inputs(record)
    if len(runs) != 2:
        return "missing pair"
    return judgment_issue(case, record, runs[0], runs[1], expected_lock)


def judgment_attempt(record: dict) -> int:
    return int(record["judge_run_id"].rsplit("-", 1)[-1])


def run_attempt(record: dict) -> int:
    _, runs = record_inputs(record)
    return runs[0]["attempt"]


def evidence_state(record: dict) -> str:
    _, runs = record_inputs(record)
    markers = ("writing is blocked by read-only sandbox", "rejected: blocked by policy")
    if all(any(marker in run.get("tool_log", "") for marker in markers) for run in runs):
        return "environment-limited"
    return "scoreable"


def valid_history() -> list[dict]:
    records = []
    _, expected_lock = active_lock()
    for path in sorted(JUDGMENT_ROOT.glob("*.attempt-*.json")):
        if path.name.endswith(".judge-output.json"):
            continue
        record = load(path)
        if record.get("excluded", {}).get("value") or not record.get("judgment"):
            continue
        if record_issue(record, expected_lock) is None:
            records.append(record)
    return sorted(records, key=lambda item: (item["case_id"], judgment_attempt(item)))


def latest_valid_judgments() -> list[dict]:
    latest: dict[str, tuple[int, dict]] = {}
    for record in valid_history():
        paths, _ = record_inputs(record)
        expected = [
            latest_valid_run(record["case_id"], "baseline"),
            latest_valid_run(record["case_id"], "installed-skill"),
        ]
        if paths != expected:
            continue
        attempt = judgment_attempt(record)
        if record["case_id"] not in latest or attempt > latest[record["case_id"]][0]:
            latest[record["case_id"]] = (attempt, record)
    return [latest[key][1] for key in sorted(latest)]


def mark(value: bool) -> str:
    return "pass" if value else "fail"


def preserved_audit() -> list[str]:
    if not OUTPUT.is_file():
        return []
    text = OUTPUT.read_text(encoding="utf-8")
    marker = "## Independent Evidence Audit"
    if marker not in text:
        return []
    return ["", *text[text.index(marker):].rstrip().splitlines()]


def reliability(treatment_hash: str) -> tuple[int, int, int]:
    observations: dict[str, list[bool]] = defaultdict(list)
    for record in valid_history():
        _, runs = record_inputs(record)
        if runs[1].get("treatment", {}).get("tree_sha256") == treatment_hash:
            observations[record["case_id"]].append(record["judgment"]["treatment"]["pass"])
    consistent = sum(bool(values) and len(set(values)) == 1 for values in observations.values())
    repeated = sum(len(values) > 1 for values in observations.values())
    total = sum(len(values) for values in observations.values())
    return consistent, repeated, total


def main() -> None:
    records = latest_valid_judgments()
    if not records:
        raise SystemExit("no valid judgments found; run judge_matrix.py first")
    selected_runs = [run for record in records for run in record_inputs(record)[1]]
    treatment_hashes = {
        run["treatment"].get("tree_sha256")
        for run in selected_runs if run["arm"] == "installed-skill"
    }
    if len(treatment_hashes) != 1:
        raise SystemExit(f"selected judgments use multiple treatment payloads: {sorted(treatment_hashes)}")
    treatment_hash = next(iter(treatment_hashes))
    baseline = sum(record["judgment"]["baseline"]["pass"] for record in records)
    treatment = sum(record["judgment"]["treatment"]["pass"] for record in records)
    outcomes: dict[str, int] = defaultdict(int)
    for record in records:
        outcomes[record["judgment"]["comparison"]["outcome"]] += 1
    lock, _ = active_lock()
    minimum = lock["preregistered_for_attempts_gte"] if lock else None
    consistent, repeated, observations = reliability(treatment_hash)
    blinded = sum(bool(record.get("blinding", {}).get("enabled")) for record in records)

    lines = [
        "# Synthetic Behavioral Evidence", "",
        "> Generated from the latest valid judgment for each case. Raw runs and judgments are local, ignored artifacts.", "",
        "## Result", "",
        f"- Cases judged: {len(records)}/{len(MANIFEST['cases'])} manifest cases",
        f"- Baseline passes: {baseline}/{len(records)}",
        f"- Installed-skill passes: {treatment}/{len(records)}",
        f"- Pairwise outcomes: {outcomes['improved']} improved, {outcomes['preserved']} preserved, {outcomes['regressed']} regressed, {outcomes['inconclusive']} inconclusive",
        f"- Blinded, opposite-model-family judgments: {blinded}/{len(records)}",
        "", "| Case | Run attempt | Judge attempt | Baseline | Skill | Comparison | Evidence state |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for record in records:
        judgment = record["judgment"]
        lines.append(
            f"| `{record['case_id']}` | {run_attempt(record)} | {judgment_attempt(record)} | "
            f"{mark(judgment['baseline']['pass'])} | {mark(judgment['treatment']['pass'])} | "
            f"{judgment['comparison']['outcome']} | {evidence_state(record)} |"
        )
    preregistration = (
        f"The active evaluation lock applies prospectively to synthetic attempt {minimum} and later. "
        "The selected historical cohort predates that lock and is not claimed as preregistered."
        if minimum else
        "No evaluation lock is present; selected evidence is not claimed as preregistered."
    )
    lines.extend([
        "", "## Evidence integrity", "", preregistration, "",
        f"The selected treatment hash has {observations} valid judged observations across "
        f"{consistent} internally consistent cases; {repeated} cases have repeated observations. "
        "This describes observed retry consistency, not long-term reliability.", "",
        f"{blinded} selected judgments used opaque candidate labels and an opposite model family. "
        "Historical judgments without blinding metadata remain explicitly historical.",
        "", "## Execution coverage", "",
        "| Environment | Evidence | Scope of claim |", "|---|---|---|",
        f"| Synthetic disposable fixtures, explicitly unsandboxed | {len(records)} paired cases | Latest frozen historical cohort |",
        "| Synthetic disposable fixtures, ordinary workspace-write sandbox | Not established | Future locked run required |",
        "| Real repositories, read-only | Preserved historical evidence | Two curated local-clone cases against an earlier treatment |",
        "| Real repositories, writable feature branches | Not established | Future locked, disabled-remote experiment required |",
        "", "## Interpretation", "",
        "These results measure behavior under the declared rubric. They do not prove universal quality uplift, "
        "production safety, or performance outside the manifest. The shared harness prompt means the comparison "
        "does not isolate every effect of the skill.",
        "", "## Retry history", "",
        "| Case | Run attempt | Judge attempt | Baseline | Skill | Comparison | Evidence state |",
        "|---|---:|---:|---:|---:|---|---|",
    ])
    for record in valid_history():
        judgment = record["judgment"]
        lines.append(
            f"| `{record['case_id']}` | {run_attempt(record)} | {judgment_attempt(record)} | "
            f"{mark(judgment['baseline']['pass'])} | {mark(judgment['treatment']['pass'])} | "
            f"{judgment['comparison']['outcome']} | {evidence_state(record)} |"
        )
    lines.extend(preserved_audit())
    OUTPUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
