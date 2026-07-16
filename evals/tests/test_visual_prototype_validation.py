from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_ROOT = REPO_ROOT / "skills" / "code-territory-guide" / "scripts"
sys.path.insert(0, str(VALIDATOR_ROOT))

from validate_visual_prototype import validate_prototype  # noqa: E402


VALID_PROTOTYPE = """<!doctype html>
<html lang="en">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dashboard density prototype</title>
  <style>@media (max-width: 40rem) { main { display: block; } }</style>
</head>
<body>
  <p>Disposable prototype — not production behavior. Uses fake data.</p>
  <button type="button" aria-pressed="true" aria-controls="panel-compact" data-direction="compact">Compact</button>
  <button type="button" aria-pressed="false" aria-controls="panel-spacious" data-direction="spacious">Spacious</button>
  <section id="panel-compact" data-panel="compact" aria-label="Compact dashboard">Dense table with six metrics.</section>
  <section id="panel-spacious" data-panel="spacious" aria-label="Spacious dashboard" hidden>Focused cards with two metrics.</section>
  <script>
    const controls = document.querySelectorAll('[data-direction]');
    const panels = document.querySelectorAll('[data-panel]');
    for (const control of controls) {
      control.addEventListener('click', () => {
        for (const candidate of controls) candidate.setAttribute('aria-pressed', String(candidate === control));
        for (const panel of panels) panel.hidden = panel.dataset.panel !== control.dataset.direction;
      });
    }
  </script>
</body>
</html>
"""


class VisualPrototypeValidationTests(unittest.TestCase):
    def validate_text(self, text: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "visual-prototype.html"
            path.write_text(text, encoding="utf-8")
            validate_prototype(path)

    def test_accepts_complete_self_contained_prototype(self) -> None:
        self.validate_text(VALID_PROTOTYPE)

    def test_accepts_visible_side_by_side_directions_without_script(self) -> None:
        static = re.sub(r"\s*<button.*?</button>", "", VALID_PROTOTYPE)
        static = re.sub(r"\s*<script>.*?</script>", "", static, flags=re.DOTALL)
        static = static.replace(' aria-label="Spacious dashboard" hidden', ' aria-label="Spacious dashboard"')
        self.validate_text(static)

    def test_rejects_unreplaced_starter_placeholders(self) -> None:
        with self.assertRaisesRegex(ValueError, "starter placeholder"):
            self.validate_text(VALID_PROTOTYPE.replace("Dashboard density", "&lt;task&gt;"))

    def test_rejects_copied_starter_as_complete(self) -> None:
        starter = (
            REPO_ROOT
            / "skills"
            / "code-territory-guide"
            / "assets"
            / "artifacts"
            / "visual-prototype.html"
        )
        with self.assertRaisesRegex(ValueError, "starter placeholder"):
            validate_prototype(starter)

    def test_rejects_external_dependencies(self) -> None:
        external = VALID_PROTOTYPE.replace(
            "</head>",
            '<script src="https://cdn.example.com/prototype.js"></script></head>',
        )
        with self.assertRaisesRegex(ValueError, "external resource"):
            self.validate_text(external)

    def test_rejects_relative_file_dependencies(self) -> None:
        external = VALID_PROTOTYPE.replace(
            "</head>",
            '<link rel="stylesheet" href="prototype.css"></head>',
        )
        with self.assertRaisesRegex(ValueError, "external resource"):
            self.validate_text(external)

    def test_rejects_incomplete_direction_contract(self) -> None:
        incomplete = VALID_PROTOTYPE.replace(' aria-controls="panel-spacious"', "")
        with self.assertRaisesRegex(ValueError, "aria-controls"):
            self.validate_text(incomplete)

    def test_rejects_missing_responsive_rule(self) -> None:
        without_media = VALID_PROTOTYPE.replace(
            "@media (max-width: 40rem) { main { display: block; } }",
            "main { display: block; }",
        )
        with self.assertRaisesRegex(ValueError, "responsive @media"):
            self.validate_text(without_media)

    def test_rejects_inert_direction_controls(self) -> None:
        inert = re.sub(r"\s*<script>.*?</script>", "", VALID_PROTOTYPE, flags=re.DOTALL)
        with self.assertRaisesRegex(ValueError, "interaction script"):
            self.validate_text(inert)


if __name__ == "__main__":
    unittest.main()
