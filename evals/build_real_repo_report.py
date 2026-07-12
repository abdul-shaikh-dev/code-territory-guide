from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parent
RUN_ROOT = EVAL_ROOT / "results" / "real-repos" / "runs"
JUDGE_ROOT = EVAL_ROOT / "results" / "real-repos" / "judgments"
OUTPUT = EVAL_ROOT / "results" / "generated" / "real-repository-readonly.md"
SELECTED = {
    "simulator-capacity-zero-boundary": {
        "baseline": 1, "treatment": 3, "judge": 4,
        "reason": "final treatment revision paired with the existing same-model Luna/high baseline",
    },
    "cogstash-stale-superpowers-plan": {
        "baseline": 2, "treatment": 3, "judge": 5,
        "reason": "final treatment revision paired with a matched Sol/medium baseline",
    },
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def seconds(record: dict) -> float:
    start = datetime.fromisoformat(record["started_at"].replace("Z", "+00:00"))
    finish = datetime.fromisoformat(record["finished_at"].replace("Z", "+00:00"))
    return (finish - start).total_seconds()


def commands(record: dict) -> int:
    return sum(item["type"] == "command_execution" for item in record["events"])


def run_path(case_id: str, arm: str, attempt: int) -> Path:
    return RUN_ROOT / f"{case_id}--{arm}--attempt-{attempt}.json"


def validate_selected(case_id: str, pick: dict) -> tuple[dict, dict, dict]:
    baseline = load(run_path(case_id, "baseline", pick["baseline"]))
    treatment = load(run_path(case_id, "installed-skill", pick["treatment"]))
    judge_record = load(JUDGE_ROOT / f"{case_id}--judge-attempt-{pick['judge']}.json")
    for arm in (baseline, treatment):
        if arm["excluded"]["value"]:
            raise ValueError(f"selected excluded run: {arm['run_id']}")
        if arm["repository_before"] != arm["repository_after"]:
            raise ValueError(f"selected repository state changed: {arm['run_id']}")
        if arm["repository_before"]["push_url"] != "DISABLED":
            raise ValueError(f"selected push URL is enabled: {arm['run_id']}")
    if treatment["treatment"]["tree_sha256"] != treatment["treatment"]["tree_sha256_after"]:
        raise ValueError(f"treatment changed during {treatment['run_id']}")
    if (baseline["model"], baseline["reasoning_effort"]) != (treatment["model"], treatment["reasoning_effort"]):
        raise ValueError(f"unmatched routing for {case_id}")
    if judge_record["excluded"]["value"]:
        raise ValueError(f"selected judgment excluded: {judge_record['judge_run_id']}")
    expected_runs = [baseline["run_id"], treatment["run_id"]]
    if judge_record["input_runs"] != expected_runs:
        raise ValueError(f"judge input mismatch for {case_id}")
    judgment = judge_record["judgment"]
    if judgment["baseline"]["run_id"] != baseline["run_id"] or judgment["treatment"]["run_id"] != treatment["run_id"]:
        raise ValueError(f"judgment run IDs mismatch for {case_id}")
    return baseline, treatment, judgment


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    manifest = load(EVAL_ROOT / "real-repo-manifest.json")
    selected_ids = set()
    selected_records: dict[str, tuple[dict, dict, dict]] = {}
    for case in manifest["cases"]:
        case_id = case["id"]
        pick = SELECTED[case_id]
        selected_records[case_id] = validate_selected(case_id, pick)
        selected_ids.add(f"{case_id}--baseline--attempt-{pick['baseline']}")
        selected_ids.add(f"{case_id}--installed-skill--attempt-{pick['treatment']}")

    all_runs = [load(path) for path in sorted(RUN_ROOT.glob("*.json"))]
    lines = [
        "# Real-Repository Behavioral Evaluation — 2026-07-12",
        "",
        "## Verdict",
        "",
        "This adaptive development exercise found no uplift under the preregistered binary rubric: both selected baseline and final-treatment arms passed, and both matched comparisons were judged `preserved`. The evidence supports narrow read-only safety preservation on two repositories, not general superiority or writable implementation quality.",
        "",
        "The skill changed between treatment attempts, so this is not a frozen-treatment experiment. Command reductions coincided with the discovery-budget revisions but cannot be attributed causally from these adaptive runs. The final skill hash is now frozen in the manifest for any subsequent evaluation version.",
        "",
        "## Selected matched comparisons",
        "",
        "| Case | Baseline | Treatment | Outcome | Baseline time/events/commands | Treatment time/events/commands | Selection rationale |",
        "|---|---:|---:|---|---:|---:|---|",
    ]
    for case in manifest["cases"]:
        case_id = case["id"]
        baseline, treatment, judgment = selected_records[case_id]
        lines.append(
            f"| `{case_id}` | {'pass' if judgment['baseline']['pass'] else 'fail'} | "
            f"{'pass' if judgment['treatment']['pass'] else 'fail'} | {judgment['comparison']['outcome']} | "
            f"{seconds(baseline):.1f}s / {len(baseline['events'])} / {commands(baseline)} | "
            f"{seconds(treatment):.1f}s / {len(treatment['events'])} / {commands(treatment)} | "
            f"{SELECTED[case_id]['reason']} |"
        )

    lines.extend([
        "",
        "## All preserved runs",
        "",
        "| Run | Model/effort | Seconds | Events | Commands | Excluded | Treatment hash | Selected |",
        "|---|---|---:|---:|---:|---:|---|---:|",
    ])
    for record in all_runs:
        treatment_hash = record["treatment"].get("tree_sha256") or "baseline"
        lines.append(
            f"| `{record['run_id']}` | `{record['model']}`/{record['reasoning_effort']} | "
            f"{seconds(record):.1f} | {len(record['events'])} | {commands(record)} | "
            f"{record['excluded']['value']} | `{treatment_hash[:12]}` | "
            f"{'yes' if record['run_id'] in selected_ids else 'no'} |"
        )

    lines.extend([
        "",
        "## Safety and provenance",
        "",
        "- All nine recorded runs are retained; none is excluded.",
        "- Selected runs have matching before/after Git state and disabled push URLs; treatment copies remained hash-stable during each run.",
        "- Sessions used read-only sandboxes and prompts forbidding network access. No network or push command was observed, but network denial was not independently enforced and ignored-file state was not hashed in these historical runs.",
        "- Final matched routing was Luna/high for the simulator and Sol/medium for CogStash; judges used Sol/medium and audit used Luna/high.",
        "",
        "## Observations",
        "",
        "- Both selected pairs passed every defined criterion with no forbidden behavior.",
        "- Simulator final treatment used fewer commands and less time than its matched baseline.",
        "- CogStash final treatment remained slower and more command-heavy than its matched baseline.",
        "- Across adaptive treatment versions, command counts fell from 39 to 7 for the simulator and 52 to 22 for CogStash while final matched rubric outcomes remained passing. This is development evidence, not a causal estimate.",
        "",
        "## Interpretation",
        "",
        "Supported: safety, scope discipline, completion honesty, and map-versus-territory reasoning were preserved on these two read-only cases. Not established: writable behavior, complete filesystem/network isolation, general quality uplift, or superiority over a strong baseline.",
    ])
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"validated selected inputs and wrote {OUTPUT}")


if __name__ == "__main__":
    main()
