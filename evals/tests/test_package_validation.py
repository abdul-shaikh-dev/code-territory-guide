from __future__ import annotations

import sys
import unittest
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL_ROOT))

from validate_package import validate  # noqa: E402


class PackageValidationTests(unittest.TestCase):
    def test_repository_package_is_consistent(self) -> None:
        validate()


if __name__ == "__main__":
    unittest.main()
