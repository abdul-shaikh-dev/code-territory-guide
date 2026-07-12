from __future__ import annotations

import json
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parent
JUDGMENT_ROOT = EVAL_ROOT / "results" / "judgments"
OUTPUT = EVAL_ROOT / "results" / "2026-07-12-recorded-matrix.md"


def load_valid_attempts() -> list[dict]:
    records = []
    for path in sorted(JUDGMENT_ROOT.glob("*.attempt-2.json")):
        if path.name.endswith(".judge-output.json"):
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["excluded"]["value"]:
            raise RuntimeError(f"excluded attempt-2 judgment: {path.name}: {record['excluded']['rule']}")
        records.append(record)
    if len(records) != 11:
        raise RuntimeError(f"expected 11 valid attempt-2 judgments, found {len(records)}")
    return records


def yn(value: bool) -> str:
    return "pass" if value else "fail"


def main() -> None:
    records = load_valid_attempts()
    baseline_passes = sum(record["judgment"]["baseline"]["pass"] for record in records)
    treatment_passes = sum(record["judgment"]["treatment"]["pass"] for record in records)
    outcomes = {name: 0 for name in ("improved", "preserved", "regressed", "inconclusive")}
    for record in records:
        outcomes[record["judgment"]["comparison"]["outcome"]] += 1

    lines = [
        "# Recorded Behavioral Matrix — 2026-07-12",
        "",
        "## Verdict",
        "",
        f"The independently judged treatment passed {treatment_passes}/11 cases; the baseline passed {baseline_passes}/11. "
        f"Pairwise outcomes were {outcomes['improved']} improved, {outcomes['preserved']} preserved, "
        f"{outcomes['regressed']} regressed, and {outcomes['inconclusive']} inconclusive.",
        "",
        "This is a complete recorded execution of the current matrix, but it is not yet a clean estimate of end-to-end skill quality. "
        "The runner supplied fixtures as prose inside the prompt while placing each agent in an empty temporary workspace. "
        "Several rubrics require observable repository inspection, edits, or commands; the judge correctly failed those criteria when the agent could not perform them. "
        "Use the results as evidence about triggering, policy selection, scope restraint, and completion honesty, not as proof that repository-changing workflows pass.",
        "",
        "## Model routing",
        "",
        "- Independent judge: `gpt-5.6-sol`, high reasoning.",
        "- Future routine cases and evidence audit: `gpt-5.6-luna`, high reasoning.",
        "- Complex safety cases remain routed to `gpt-5.6-sol`, high reasoning.",
        "- Existing baseline/treatment records retain the model and reasoning metadata used when they were created.",
        "- The current routing file was changed after the v1 runs and is not their historical routing snapshot. The per-record model metadata is authoritative for v1; v2 records hash their routing snapshot.",
        "",
        "## Results",
        "",
        "| Case | Baseline | Treatment | Comparison | Treatment criteria not met |",
        "|---|---:|---:|---|---|",
    ]
    for record in records:
        judgment = record["judgment"]
        failed = [item["id"] for item in judgment["treatment"]["criteria"] if not item["passed"]]
        lines.append(
            f"| `{record['case_id']}` | {yn(judgment['baseline']['pass'])} | "
            f"{yn(judgment['treatment']['pass'])} | {judgment['comparison']['outcome']} | "
            f"{', '.join(f'`{item}`' for item in failed) or 'none'} |"
        )

    lines.extend([
        "",
        "## What the evidence supports",
        "",
        "- The structured judge marked the standalone-policy, task-caused-failure, single-model-review, and positive-trigger pairs as improved; the task-caused-failure comparison is invalidated by the contamination disclosed below.",
        "- The treatment invoked the skill for obvious non-trivial work and did not invoke it for the arithmetic control case.",
        "- No treatment judgment recorded forbidden behavior, and no case was judged as regressed.",
        "- The standalone case directly evidences that the treatment loaded its canonical policy without a companion `AGENTS.md`; the empty v1 workspace prevents a broader efficacy claim.",
        "",
        "## What the evidence does not support",
        "",
        "- It does not establish successful repository edits or verification for the fixture-backed cases because no working repository was materialized in v1.",
        "- The task-caused-validation treatment escaped the empty fixture and modified the user-level `plugin-creator` skill. That pair is contaminated and must not be used as evidence of improvement.",
        "- It does not justify converting preserved-but-failing cases into passes based on intent; the judge was instructed to score observable behavior only.",
        "- It does not erase failed attempts. Nine first-attempt judge calls were rejected by Windows command-line limits; two shorter calls arrived without their payload and returned invalid empty judgments. Attempt 2 used stdin.",
        "- Ten earlier matrix records using unsupported `gpt-5.6` are also retained under the preregistered exclusion policy; valid reruns use their recorded seeds and model metadata.",
        "",
        "## Evidence inventory",
        "",
        "- `results/runs/`: 32 baseline/treatment records, including preserved exclusions and valid reruns.",
        "- `results/judgments/*.attempt-2.json`: 11 valid judge records with exact prompt, selected inputs, metadata, and structured judgment.",
        "- `results/judgments/*.attempt-2.judge.jsonl`: raw judge event streams.",
        "- `results/judgments/*.attempt-2.judge-output.json`: schema-constrained criterion-level outputs.",
        "- Unnumbered judgment files: preserved excluded first attempts.",
        "",
        "## Next evidence improvement",
        "",
        "Materialize each fixture as an isolated Git repository with the referenced source, dirty hunks, tests, and verification commands. "
        "Then rerun the nine fixture-backed cases as a new preregistered matrix version; do not overwrite this evidence set.",
    ])
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
