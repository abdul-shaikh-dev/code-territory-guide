from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


EVAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL_ROOT))

import run_matrix  # noqa: E402


class RunnerPreflightTests(unittest.TestCase):
    def test_duplicate_run_is_rejected_before_materialization(self) -> None:
        case = {"id": "duplicate"}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "duplicate--baseline--attempt-20.json").write_text("{}", encoding="utf-8")
            with (
                patch.object(run_matrix, "RUN_ROOT", root),
                patch.object(run_matrix, "materialize") as materialize,
            ):
                with self.assertRaisesRegex(RuntimeError, "refusing to overwrite"):
                    run_matrix.run_one(case, "baseline", 20, False, {})
                materialize.assert_not_called()


if __name__ == "__main__":
    unittest.main()
