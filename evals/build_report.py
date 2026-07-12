from __future__ import annotations

import json
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parent
JUDGMENT_ROOT = EVAL_ROOT / "results" / "judgments"
OUTPUT = EVAL_ROOT / "results" / "synthetic-evidence.md"


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
        attempt = int(record["judge_run_id"].rsplit("-", 1)[-1])
        current = latest.get(record["case_id"])
        if current is None or attempt > current[0]:
            latest[record["case_id"]] = (attempt, record)
    return [latest[key][1] for key in sorted(latest)]


def mark(value: bool) -> str:
    return "pass" if value else "fail"


def main() -> None:
    records = load_latest_valid_judgments()
    if not records:
        raise SystemExit("no valid judgments found; run judge_matrix.py first")

    baseline = sum(record["judgment"]["baseline"]["pass"] for record in records)
    treatment = sum(record["judgment"]["treatment"]["pass"] for record in records)
    outcomes = {name: 0 for name in ("improved", "preserved", "regressed", "inconclusive")}
    for record in records:
        outcomes[record["judgment"]["comparison"]["outcome"]] += 1

    lines = [
        "# Synthetic Behavioral Evidence",
        "",
        "> Generated from the latest valid judgment for each case. Raw runs and judgments are local, ignored artifacts.",
        "",
        "## Result",
        "",
        f"- Cases judged: {len(records)}",
        f"- Baseline passes: {baseline}/{len(records)}",
        f"- Installed-skill passes: {treatment}/{len(records)}",
        f"- Pairwise outcomes: {outcomes['improved']} improved, {outcomes['preserved']} preserved, "
        f"{outcomes['regressed']} regressed, {outcomes['inconclusive']} inconclusive",
        "",
        "| Case | Baseline | Skill | Comparison |",
        "|---|---:|---:|---|",
    ]
    for record in records:
        judgment = record["judgment"]
        lines.append(
            f"| `{record['case_id']}` | {mark(judgment['baseline']['pass'])} | "
            f"{mark(judgment['treatment']['pass'])} | {judgment['comparison']['outcome']} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "This report measures behavior under the declared rubric. It does not prove universal quality uplift, "
        "production safety, or performance on tasks outside the manifest. Inspect the preserved local run and "
        "judgment records before making stronger claims.",
        "",
    ])
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
