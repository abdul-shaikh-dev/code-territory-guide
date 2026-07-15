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


class EvaluationLockTests(unittest.TestCase):
    def test_text_hash_is_line_ending_independent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lf = root / "lf.md"
            crlf = root / "crlf.md"
            lf.write_bytes(b"one\ntwo\n")
            crlf.write_bytes(b"one\r\ntwo\r\n")
            self.assertEqual(
                freeze_evaluation.sha256_file(lf),
                freeze_evaluation.sha256_file(crlf),
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
