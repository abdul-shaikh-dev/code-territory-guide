---
name: Code Territory Guide
description: A visual field instrument for evidence-led code work
colors:
  signal: "oklch(0.58 0.2 357)"
  signal-deep: "oklch(0.34 0.135 357)"
  signal-soft: "oklch(0.95 0.032 357)"
  route: "oklch(0.64 0.12 183)"
  route-deep: "oklch(0.31 0.07 183)"
  ink: "oklch(0.17 0.014 252)"
  ink-soft: "oklch(0.39 0.02 252)"
  line: "oklch(0.83 0.012 252)"
  surface: "oklch(0.965 0.006 252)"
  white: "oklch(1 0 0)"
typography:
  display:
    fontFamily: "Arial Narrow, Aptos Display, Segoe UI, sans-serif"
    fontSize: "clamp(3.7rem, 7.8vw, 6rem)"
    fontWeight: 820
    lineHeight: 0.94
    letterSpacing: "-0.035em"
  body:
    fontFamily: "Segoe UI, Aptos, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
rounded:
  sm: "0.35rem"
  md: "0.75rem"
spacing:
  control: "0.75rem 1rem"
  section: "clamp(5rem, 10vw, 9rem)"
components:
  button-primary:
    backgroundColor: "{colors.signal}"
    textColor: "{colors.white}"
    rounded: "{rounded.sm}"
    padding: "{spacing.control}"
  button-secondary:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "{spacing.control}"
---

# Design System: Code Territory Guide

## 1. Overview

**Creative North Star: "The Evidence Compass"**

The explainer feels like a precise field instrument opened on a clear
workbench: curious enough to invite exploration, rigorous enough to support a
decision, and transparent about what is or is not known. Ordnance Survey map
precision shapes the relationships, NASA field-manual clarity shapes the
language, and Stripe Press technical illustration quality sets the finish bar.

The visual rhythm alternates between committed orientation surfaces and dense,
inspectable evidence. It rejects generic SaaS card grids, fantasy-expedition
cosplay, dark neon "AI terminal" styling, and editorial layouts that make an
operational sequence harder to follow.

**Key Characteristics:**

- Rose-red orientation fields and blue-green evidence signals.
- Diagrammatic relationships that remain readable without animation.
- Spacious narrative moments alternating with dense operational detail.
- Direct language and visible qualification of claims.
- Dependency-free system typography and one self-contained HTML entry.

## 2. Colors

The palette uses a committed signal color, a distinct route/evidence color, and
near-neutral working surfaces. Token values in the frontmatter are normative.

### Primary

- **Territory Signal** (`signal`): large orientation surfaces, selected states,
  and primary actions.
- **Deep Coordinate** (`signal-deep`): readable text and structural detail
  related to the primary signal.
- **Signal Wash** (`signal-soft`): delivery education and low-intensity context.

### Secondary

- **Verified Route** (`route`): focus, positive wayfinding, and evidence cues.
- **Route Depth** (`route-deep`): the evidence section's grounded field.

### Neutral

- **Instrument Ink** (`ink`): body text and decisive structural lines.
- **Working Annotation** (`ink-soft`): supporting text.
- **Survey Line** (`line`): dividers and inactive boundaries.
- **Field Surface** (`surface`): alternating explanatory sections.
- **True White** (`white`): primary canvas and text on saturated fills.

**The Committed Signal Rule.** Rose-red carries the identity across purposeful
surfaces; it is never reduced to a timid decorative accent.

**The Evidence Color Rule.** Blue-green always means route, focus, or evidence.
It cannot become a second ornamental brand fill.

## 3. Typography

**Display Font:** Arial Narrow with Aptos Display and Segoe UI fallbacks

**Body Font:** Segoe UI with Aptos and system UI fallbacks

**Character:** The condensed display stack behaves like a precise instrument
heading, while the humanist body stack stays readable across platforms without
network font dependencies.

### Hierarchy

- **Display** (820, fluid to 6rem, 0.94): hero and major orientation statements.
- **Headline** (800, fluid to 4.8rem, 0.98): section decisions and transitions.
- **Title** (700–800, 1.25–1.55rem): route stops and operational concepts.
- **Body** (400, 1rem, 1.55): explanations, capped near 60–68 characters where practical.
- **Label** (780–850, 0.78–0.9rem): real modes, controls, indices, and evidence states.

**The Instrument Label Rule.** Compact labels identify real controls, states,
or evidence; they never repeat as decorative eyebrows above every section.

## 4. Elevation

The system is flat by default. Depth comes from color fields, overlap, and
structural lines. Shadows are intentionally absent; interactive lift uses a
small two-pixel translation and state color instead of ambient decoration.

**The Flat Evidence Rule.** If a relationship needs a shadow to be understood,
the structure is not yet clear enough.

## 5. Components

### Buttons

- **Shape:** compact precision corners (`rounded.sm`).
- **Primary:** Territory Signal fill with True White text and control spacing.
- **Hover / Focus:** two-pixel lift on hover; three-pixel Verified Route focus ring.
- **Secondary:** transparent or white surface with a one-pixel semantic border.

### Chips

- **Style:** full pill only for compass mode labels; Deep Coordinate fill and
  white text.
- **State:** pills identify modes but do not impersonate buttons unless interactive.

### Cards / Containers

- **Corner Style:** medium corners only where content physically groups.
- **Background:** Field Surface or True White.
- **Shadow Strategy:** none.
- **Border:** structural one-pixel Survey Line where boundaries carry meaning.
- **Internal Padding:** fluid, based on section density rather than a repeated card recipe.

### Inputs / Fields

No text-entry fields ship in the explainer. Mode tabs and capability buttons
use native buttons with semantic selected states.

### Navigation

Navigation sits directly on the hero field with high-contrast text. Desktop
shows learning anchors and repository access; narrow layouts preserve the brand
and repository action while the page itself supplies the learning sequence.

### Evidence Compass

The circular four-mode compass is the signature image. It communicates one
main uncertainty surrounded by Survey, Track, Prove, and Expedition without
pretending that the modes are a maturity ladder.

## 6. Do's and Don'ts

### Do:

- **Do** make modes, gates, and evidence relationships directly interactive.
- **Do** preserve readable fallback content without animation or JavaScript.
- **Do** use asymmetric composition when it clarifies hierarchy.
- **Do** provide visible focus and a complete reduced-motion alternative.
- **Do** use exact canonical vocabulary from the skill and README.

### Don't:

- **Don't** use generic SaaS landing pages built from repetitive feature-card grids.
- **Don't** use fantasy-expedition cosplay.
- **Don't** use dark neon "AI terminal" styling.
- **Don't** use editorial-magazine layouts that obscure sequence or evidence.
- **Don't** use gradient text, decorative glassmorphism, side-stripe accents, or wide ghost-card shadows.
- **Don't** imply that deterministic validation is fresh behavioral evidence.
