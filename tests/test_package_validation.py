from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_package import validate, validate_versions  # noqa: E402


class PackageValidationTests(unittest.TestCase):
    def test_repository_package_is_consistent(self) -> None:
        validate()

    def test_codex_local_build_preserves_shared_release_version(self) -> None:
        versions = {"package.json": "0.3.7", ".codex-plugin/plugin.json": "0.3.7+codex.20260905"}
        self.assertEqual(validate_versions(versions), "0.3.7")

    def test_codex_cachebuster_cannot_hide_release_drift(self) -> None:
        for codex in ("0.3.8+codex.20260905", "0.3.7+other.build", "0.3.7+codex."):
            with self.subTest(codex=codex), self.assertRaises(ValueError):
                validate_versions({"package.json": "0.3.7", ".codex-plugin/plugin.json": codex})


if __name__ == "__main__":
    unittest.main()
