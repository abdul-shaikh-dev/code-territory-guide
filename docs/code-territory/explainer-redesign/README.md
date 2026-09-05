# Visual explainer redesign

The visual explainer now uses a deep-green and lime field-guide palette, a
procedural topographic SVG, clearer typography, and responsive section layouts.
All runtime styling and behavior remain in `site/index.html`; no dependencies
or remote assets were introduced.

Copy now matches the current guide: routine work is direct, Expedition is for
complex coordination, supporting references load conditionally, prior delivery
authorization is reused, portable editions are distinguished, and model routing
and validation claims reflect the merged source.

## Verification

- All 32 local tests and the site validator pass.
- Headless Chromium checked widths 320, 390, 768, 1024, and 1440 pixels.
- Four mode controls, keyboard End navigation, six capability controls, expanded
  disclosures, and reduced-motion rendering pass; no overflow or JS errors.
- Desktop, mobile, mode, example, install, and disclosure screenshots were
  inspected. Final anchor offsets were tightened after review.
- The connected CUA browser was unavailable; a separate installed Chromium test
  process rendered the local page without adding project dependencies.

[Desktop preview](desktop.png) · [Mobile preview](mobile.png)
