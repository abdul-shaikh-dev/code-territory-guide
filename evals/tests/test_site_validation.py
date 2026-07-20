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

    def test_rejects_incomplete_decision_map(self) -> None:
        html = self.valid_html.replace(
            'data-compass-mode="survey"><span>',
            'data-compass-mode="unknown"><span>',
            1,
        )
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertIn("decision map and mode controls must have matching keys", errors)

    def test_rejects_inert_decision_map_route(self) -> None:
        html = self.valid_html.replace(
            '<a class="mode-route" href="#tab-survey" data-compass-mode="survey">',
            '<div class="mode-route" data-compass-mode="survey">',
            1,
        ).replace("</small></a>", "</small></div>", 1)
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertTrue(any("decision map routes must be links" in error for error in errors))

    def test_rejects_missing_viewport_chapter_contract(self) -> None:
        html = self.valid_html.replace("min-height: 100svh;", "min-height: auto;")
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertIn("missing desktop one-viewport chapter contract", errors)

    def test_rejects_page_level_scroll_snapping(self) -> None:
        html = self.valid_html.replace("html { scroll-behavior: smooth; }", "html { scroll-behavior: smooth; scroll-snap-type: y proximity; }")
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertIn("page-level scroll snapping must not interrupt natural scrolling", errors)

    def test_rejects_missing_worked_example(self) -> None:
        html = self.valid_html.replace('id="example"', 'id="request-walkthrough"', 1)
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertIn("missing required explainer section: example", errors)

    def test_rejects_missing_guardrails(self) -> None:
        html = self.valid_html.replace('id="guardrails"', 'id="workflow-rules"', 1)
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertIn("missing required explainer section: guardrails", errors)

    def test_rejects_missing_scope_guardrail(self) -> None:
        html = self.valid_html.replace("Gate material scope expansion", "Review the planned scope", 1)
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertIn("missing required workflow concept: gate material scope expansion", errors)

    def test_rejects_incomplete_progressive_disclosure(self) -> None:
        html = self.valid_html.replace("<details", "<div", 1).replace("</details>", "</div>", 1)
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertIn("expected six progressive-disclosure sections, found 5", errors)

    def test_rejects_retired_high_intensity_palette(self) -> None:
        html = self.valid_html.replace(
            "--signal-deep: oklch(0.27 0.055 350);",
            "--signal-deep: oklch(0.27 0.055 350); --caution: oklch(0.84 0.16 92);",
            1,
        )
        errors = validate_html_text(html, site_root=SITE_ROOT)
        self.assertIn("retired high-intensity caution palette must not return", errors)


if __name__ == "__main__":
    unittest.main()
