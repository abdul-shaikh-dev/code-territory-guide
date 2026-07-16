from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


EVAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL_ROOT))

import freeze_evaluation  # noqa: E402
from validate_records import expected_lock_for_attempt  # noqa: E402


class EvaluationLockTests(unittest.TestCase):
    def test_prospective_lock_does_not_reclassify_preserved_history(self) -> None:
        lock = {"preregistered_for_attempts_gte": 22}
        self.assertIsNone(expected_lock_for_attempt(20, lock, "active"))
        self.assertEqual(expected_lock_for_attempt(22, lock, "active"), "active")
        self.assertEqual(expected_lock_for_attempt(23, lock, "active"), "active")

    def test_text_hash_is_line_ending_independent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for suffix in (".md", ".html"):
                with self.subTest(suffix=suffix):
                    lf = root / f"lf{suffix}"
                    crlf = root / f"crlf{suffix}"
                    lf.write_bytes(b"one\ntwo\n")
                    crlf.write_bytes(b"one\r\ntwo\r\n")
                    self.assertEqual(
                        freeze_evaluation.sha256_file(lf),
                        freeze_evaluation.sha256_file(crlf),
                    )

    def test_tree_hash_is_independent_of_discovery_order(self) -> None:
        forward = {"SKILL.md": "first", "references/modes.md": "second"}
        reverse = dict(reversed(tuple(forward.items())))
        self.assertEqual(
            freeze_evaluation.tree_hash_from_entries(forward),
            freeze_evaluation.tree_hash_from_entries(reverse),
        )

    def test_attempt_floor_and_snapshot_are_enforced(self) -> None:
        snapshot = {"treatment_tree_sha256": "skill", "files": {"a": "hash"}}
        lock = {
            "schema_version": 1,
            "release_id": "release",
            "preregistered_for_attempts_gte": 20,
            **snapshot,
        }
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "evaluation-lock.json"
            lock_path.write_text(json.dumps(lock), encoding="utf-8")
            with (
                patch.object(freeze_evaluation, "LOCK_PATH", lock_path),
                patch.object(freeze_evaluation, "current_snapshot", return_value=snapshot),
            ):
                self.assertEqual(freeze_evaluation.validate_lock(20), lock)
                with self.assertRaisesRegex(ValueError, "minimum is 20"):
                    freeze_evaluation.validate_lock(19)
                with patch.object(
                    freeze_evaluation,
                    "current_snapshot",
                    return_value={"treatment_tree_sha256": "changed", "files": {"a": "hash"}},
                ):
                    with self.assertRaisesRegex(ValueError, "evaluation lock mismatch"):
                        freeze_evaluation.validate_current_lock()


if __name__ == "__main__":
    unittest.main()
