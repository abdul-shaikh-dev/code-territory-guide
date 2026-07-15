from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL_ROOT))

from evidence_sanitizer import REDACTED_COMMAND, REDACTED_TEXT, evidence_view  # noqa: E402
from judge_matrix import build_prompt, normalize_judgment  # noqa: E402


def record(run_id: str, arm: str) -> dict:
    return {
        "run_id": run_id,
        "arm": arm,
        "model": "gpt-source",
        "query": "shared query",
        "execution": {"workspace": r"G:\private\session\repo"},
        "seed": {"path": r"G:\private\seeds\repo"},
        "treatment": {"path": r"C:\private\skill" if arm == "installed-skill" else None},
        "tool_events": [
            {
                "type": "agent_message",
                "text": f"I am {run_id}, arm={arm}, model=gpt-source",
            },
            {
                "type": "command_execution",
                "command": r"Get-Content C:\private\skill\SKILL.md",
                "output": "secret",
                "status": "completed",
                "exit_code": 0,
            },
        ],
    }


class BlindingAndSanitizerTests(unittest.TestCase):
    def test_evidence_removes_paths_and_source_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text("A distinctive secret sentence " * 5, encoding="utf-8")
            item = record("case--installed-skill--attempt-20", "installed-skill")
            item["tool_events"][0]["text"] = item["tool_events"][0]["text"].upper()
            evidence = evidence_view(item, root)
        text = str(evidence)
        self.assertNotIn("case--installed-skill--attempt-20", text)
        self.assertNotIn("gpt-source", text)
        self.assertNotIn(r"C:\private\skill", text)
        self.assertNotIn(r"G:\private\session\repo", text)
        self.assertNotIn(r"G:\private\seeds\repo", text)
        self.assertIn(REDACTED_TEXT, text)
        self.assertIn(REDACTED_COMMAND, text)

    def test_prompt_uses_only_opaque_candidates(self) -> None:
        case = {
            "id": "case",
            "query": "shared query",
            "expected_behavior": [{"id": "x", "critical": True}],
            "forbidden_behavior": [],
        }
        baseline = record("case--baseline--attempt-20", "baseline")
        treatment = record("case--installed-skill--attempt-20", "installed-skill")
        prompt, assignment = build_prompt(case, baseline, treatment)
        self.assertIn("candidate_a", prompt)
        self.assertIn("candidate_b", prompt)
        self.assertNotIn(baseline["run_id"], prompt)
        self.assertNotIn(treatment["run_id"], prompt)
        self.assertNotIn("gpt-source", prompt)
        self.assertEqual(set(assignment.values()), {"baseline", "treatment"})

    def test_normalization_ignores_blind_preference_for_outcome(self) -> None:
        baseline = record("base", "baseline")
        treatment = record("treat", "installed-skill")
        arm = {
            "criteria": [{"id": "x", "passed": True}],
            "forbidden": [],
            "critical_pass": True,
            "pass": True,
        }
        blind = {
            "case_id": "case",
            "candidate_a": arm,
            "candidate_b": arm,
            "comparison": {"preference": "candidate_a", "explanation": "same pass status"},
        }
        normalized = normalize_judgment(
            blind,
            {"candidate_a": "treatment", "candidate_b": "baseline"},
            baseline,
            treatment,
        )
        self.assertEqual(normalized["comparison"]["outcome"], "preserved")


if __name__ == "__main__":
    unittest.main()
