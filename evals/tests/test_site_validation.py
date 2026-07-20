from __future__ import annotations

import sys
import unittest
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL_ROOT))

from validate_site import INDEX_PATH, SITE_ROOT, validate_html_text  # noqa: E402


class SiteValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.valid_html = INDEX_PATH.read_text(encoding="utf-8")

    def test_accepts_production_explainer(self) -> None:
        self.assertEqual(validate_html_text(self.valid_html, site_root=SITE_ROOT), [])

    def test_rejects_external_runtime_dependency(self) -> None:
        html = self.valid_html.replace("</head>", '<script src="https://example.com/app.js"></script></head>')
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertTrue(any("external runtime resource" in error for error in errors))

    def test_rejects_broken_fragment(self) -> None:
        html = self.valid_html.replace('href="#modes"', 'href="#missing"', 1)
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertIn("broken fragment link: #missing", errors)

    def test_rejects_missing_reduced_motion_contract(self) -> None:
        html = self.valid_html.replace("prefers-reduced-motion: reduce", "prefers-reduced-motion: no-preference")
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertIn("missing reduced-motion media query", errors)

    def test_rejects_incomplete_mode_controls(self) -> None:
        html = self.valid_html.replace('data-mode="survey"', 'data-selection="survey"', 1)
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertTrue(any("expected four mode controls" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
