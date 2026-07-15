from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from freeze_evaluation import lock_sha256, validate_lock
from judge_real_repo_writable_eval import validate_pair
from judge_matrix import validate_judgment


EVAL_ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads(
    (EVAL_ROOT / "real-repo-writable-manifest.json").read_text(encoding="utf-8")
)
RUN_ROOT = EVAL_ROOT / "results" / "real-repos-writable" / "runs"
JUDGE_ROOT = EVAL_ROOT / "results" / "real-repos-writable" / "judgments"
OUTPUT = EVAL_ROOT / "results" / "real-repository-writable-evidence.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def seconds(record: dict) -> float:
    start = datetime.fromisoformat(record["started_at"].replace("Z", "+00:00"))
    finish = datetime.fromisoformat(record["finished_at"].replace("Z", "+00:00"))
    return (finish - start).total_seconds()


def command_count(record: dict) -> int:
    return sum(event["type"] == "command_execution" for event in record["events"])


def selected_records(
    case: dict,
    run_attempt: int,
    judge_attempt: int,
    expected_lock: str,
) -> tuple[dict, dict, dict]:
    baseline_path = (
        RUN_ROOT / f"{case['id']}--baseline--attempt-{run_attempt}.json"
    )
    treatment_path = (
        RUN_ROOT / f"{case['id']}--installed-skill--attempt-{run_attempt}.json"
    )
    judge_path = JUDGE_ROOT / f"{case['id']}--judge-attempt-{judge_attempt}.json"
    baseline = load(baseline_path)
    treatment = load(treatment_path)
    judge = load(judge_path)
    if baseline["attempt"] != run_attempt or treatment["attempt"] != run_attempt:
        raise ValueError(f"run attempt mismatch for {case['id']}")
    if judge["judge_run_id"] != f"{case['id']}--judge-attempt-{judge_attempt}":
        raise ValueError(f"judge attempt mismatch for {case['id']}")
    for record in (baseline, treatment, judge):
        if record.get("evaluation_lock", {}).get("sha256") != expected_lock:
            raise ValueError(f"evaluation lock mismatch for {case['id']}")
    if baseline["excluded"]["value"] or treatment["excluded"]["value"]:
        raise ValueError(f"selected excluded run for {case['id']}")
    validate_pair(case, baseline, treatment)
    if baseline["seed"]["head"] != case["base_commit"]:
        raise ValueError(f"baseline seed mismatch for {case['id']}")
    if treatment["seed"]["head"] != case["base_commit"]:
        raise ValueError(f"treatment seed mismatch for {case['id']}")
    for run in (baseline, treatment):
        after = run["repository_after"]
        if after["commits_from_base"] != 1 or after["status"]:
            raise ValueError(f"incomplete committed state: {run['run_id']}")
        if after["fetch_url"] != "DISABLED" or after["push_url"] != "DISABLED":
            raise ValueError(f"remote enabled: {run['run_id']}")
        if not run["changed_files"]:
            raise ValueError(f"missing task delta: {run['run_id']}")
        if not all(run["validation_observed"].values()):
            raise ValueError(f"missing validation evidence: {run['run_id']}")
    if judge["excluded"]["value"] or not judge.get("judgment"):
        raise ValueError(f"excluded or missing judgment for {case['id']}")
    expected_inputs = [
        str(baseline_path.relative_to(EVAL_ROOT)),
        str(treatment_path.relative_to(EVAL_ROOT)),
    ]
    if judge["input_records"] != expected_inputs:
        raise ValueError(f"judge input mismatch for {case['id']}")
    validate_judgment(case, baseline, treatment, judge["judgment"])
    return baseline, treatment, judge


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-attempt", type=int, required=True)
    parser.add_argument("--judge-attempt", type=int, required=True)
    args = parser.parse_args()
    lock = validate_lock(max(args.run_attempt, args.judge_attempt))
    expected_lock = lock_sha256(lock)
    records = {
        case["id"]: selected_records(
            case,
            args.run_attempt,
            args.judge_attempt,
            expected_lock,
        )
        for case in MANIFEST["cases"]
    }
    outcomes = {"improved": 0, "preserved": 0, "regressed": 0, "inconclusive": 0}
    baseline_passes = 0
    treatment_passes = 0
    for _, _, judge in records.values():
        judgment = judge["judgment"]
        baseline_passes += int(judgment["baseline"]["pass"])
        treatment_passes += int(judgment["treatment"]["pass"])
        outcomes[judgment["comparison"]["outcome"]] += 1

    lines = [
        "# Writable Real-Repository Behavioral Evidence",
        "",
        "## Result",
        "",
        f"- Run attempt: {args.run_attempt}",
        f"- Judge attempt: {args.judge_attempt}",
        f"- Evaluation lock: {lock['release_id']} ({expected_lock})",
        f"- Cases judged: {len(records)}/{len(MANIFEST['cases'])}",
        f"- Baseline passes: {baseline_passes}/{len(records)}",
        f"- Installed-skill passes: {treatment_passes}/{len(records)}",
        f"- Pairwise outcomes: {outcomes['improved']} improved, {outcomes['preserved']} preserved, "
        f"{outcomes['regressed']} regressed, {outcomes['inconclusive']} inconclusive",
        "",
        "| Case | Baseline | Skill | Outcome | Baseline seconds/commands | Skill seconds/commands | Files changed |",
        "|---|---:|---:|---|---:|---:|---|",
    ]
    for case in MANIFEST["cases"]:
        baseline, treatment, judge = records[case["id"]]
        judgment = judge["judgment"]
        files = sorted(
            {
                item["path"]
                for run in (baseline, treatment)
                for item in run["changed_files"]
            }
        )
        lines.append(
            f"| {case['id']} | {'pass' if judgment['baseline']['pass'] else 'fail'} | "
            f"{'pass' if judgment['treatment']['pass'] else 'fail'} | "
            f"{judgment['comparison']['outcome']} | "
            f"{seconds(baseline):.1f}/{command_count(baseline)} | "
            f"{seconds(treatment):.1f}/{command_count(treatment)} | "
            f"{', '.join(files)} |"
        )
    lines.extend(
        [
            "",
            "## Integrity and scope",
            "",
            "- Every selected arm started from the registered commit in a separate disposable local clone.",
            "- Every selected arm requested workspace-write through the native elevated Windows sandbox backend.",
            "- Every selected arm retained disabled fetch and push URLs, produced exactly one local commit, left a clean worktree, and recorded the required validation commands.",
            "- Treatment payloads and provisioned dependency copies remained hash-stable during each selected run.",
            "- Judges received sanitized opaque candidates and used the configured opposite model family.",
            "- Network use was prohibited and network-capable commands were grounds for exclusion. Network denial was not independently enforced because Codex required API connectivity.",
            "- This evidence covers three bounded implementation tasks. It does not establish universal quality uplift, deployment safety, or behavior outside the registered repositories and rubrics.",
            "",
            "## Local commit evidence",
            "",
            "| Case | Baseline commit | Skill commit |",
            "|---|---|---|",
        ]
    )
    for case in MANIFEST["cases"]:
        baseline, treatment, _ = records[case["id"]]
        lines.append(
            f"| {case['id']} | {baseline['repository_after']['commit_subject']} | "
            f"{treatment['repository_after']['commit_subject']} |"
        )
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"validated selected writable evidence and wrote {OUTPUT}")


if __name__ == "__main__":
    main()
