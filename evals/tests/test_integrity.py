from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL_ROOT))

from evaluation_integrity import judgment_issue, pair_issue  # noqa: E402


class IntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = {
            "id": "sample",
            "query": "Implement the sample.",
            "expected_behavior": [{"id": "did-it", "critical": True}],
            "forbidden_behavior": ["changed unrelated files"],
        }
        full_query = (
            "Implement the sample.\n\nWork only in the current repository. "
            "Do not search parent directories or user-profile directories. "
            "Preserve unrelated existing changes and use each repository's own validation instructions."
        )
        common = {
            "case_id": "sample",
            "attempt": 20,
            "query": full_query,
            "fixture": {"tree_sha256": "fixture"},
            "routing_sha256": "routing",
            "model": "source-model",
            "reasoning_effort": "medium",
            "harness_revision": "v4",
            "schema_version": 3,
            "evaluation_lock": {"sha256": "lock", "preregistered": True},
            "excluded": {"value": False},
        }
        self.baseline = {
            **common,
            "run_id": "sample--baseline--attempt-20",
            "arm": "baseline",
            "treatment": {"installed": False},
        }
        self.treatment = {
            **common,
            "run_id": "sample--installed-skill--attempt-20",
            "arm": "installed-skill",
            "treatment": {
                "installed": True,
                "tree_sha256": "skill",
                "tree_sha256_after": "skill",
            },
        }
        arm = {
            "criteria": [{"id": "did-it", "passed": True}],
            "forbidden": [{"description": "changed unrelated files", "occurred": False}],
            "critical_pass": True,
            "pass": True,
        }
        self.record = {
            "case_id": "sample",
            "model": "judge-model",
            "blinding": {
                "enabled": True,
                "source_model": "source-model",
                "judge_model_is_independent": True,
                "assignment": {"candidate_a": "baseline", "candidate_b": "treatment"},
            },
            "judgment": {
                "baseline": {"run_id": self.baseline["run_id"], **copy.deepcopy(arm)},
                "treatment": {"run_id": self.treatment["run_id"], **copy.deepcopy(arm)},
                "comparison": {"outcome": "preserved"},
            },
        }

    def test_valid_pair_and_judgment(self) -> None:
        self.assertIsNone(pair_issue(self.case, self.baseline, self.treatment, "lock"))
        self.assertIsNone(
            judgment_issue(self.case, self.record, self.baseline, self.treatment, "lock")
        )

    def test_rejects_lock_and_comparison_tampering(self) -> None:
        changed = copy.deepcopy(self.treatment)
        changed["evaluation_lock"]["sha256"] = "other"
        self.assertEqual(pair_issue(self.case, self.baseline, changed, "lock"), "evaluation lock mismatch")
        changed_record = copy.deepcopy(self.record)
        changed_record["judgment"]["comparison"]["outcome"] = "improved"
        self.assertEqual(
            judgment_issue(self.case, changed_record, self.baseline, self.treatment, "lock"),
            "inconsistent comparison outcome",
        )

    def test_rejects_unblinded_or_same_model_judge(self) -> None:
        changed = copy.deepcopy(self.record)
        changed["blinding"]["source_model"] = "judge-model"
        self.assertEqual(
            judgment_issue(self.case, changed, self.baseline, self.treatment, "lock"),
            "judge model matches source model",
        )


if __name__ == "__main__":
    unittest.main()
