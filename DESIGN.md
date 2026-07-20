---
name: Code Territory Guide
description: A visual field instrument for evidence-led code work
colors:
  signal: "oklch(0.39 0.07 350)"
  signal-deep: "oklch(0.27 0.055 350)"
  signal-soft: "oklch(0.95 0.015 350)"
  route: "oklch(0.57 0.08 188)"
  route-deep: "oklch(0.3 0.045 188)"
  ink: "oklch(0.16 0.02 342)"
  ink-soft: "oklch(0.39 0.025 342)"
  line: "oklch(0.84 0.012 342)"
  surface: "oklch(0.975 0.008 350)"
  white: "oklch(1 0 0)"
typography:
  display:
    fontFamily: "Bahnschrift, DIN Alternate, Arial Narrow, sans-serif"
    fontSize: "clamp(3.7rem, 7.8vw, 6rem)"
    fontWeight: 720
    lineHeight: 0.94
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Atkinson Hyperlegible, Trebuchet MS, Segoe UI, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.62
rounded:
  sm: "0.35rem"
  md: "0.75rem"
spacing:
  control: "0.75rem 1rem"
  section: "clamp(3.5rem, 7vh, 5rem) for primary desktop chapters"
components:
  button-primary:
    backgroundColor: "{colors.white}"
    textColor: "{colors.signal-deep}"
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

**Creative North Star: "The Evidence Map"**

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

- Muted berry orientation, restrained teal wayfinding, and neutral-dominant working surfaces.
- Diagrammatic relationships that remain readable without animation.
- A short decision journey followed by optional operational depth.
- Direct language and visible qualification of claims.
- Dependency-free local-first typography and one self-contained HTML entry.

## 2. Colors

The palette uses a muted identity color, a restrained route/evidence color,
and near-neutral working surfaces. Token values in the frontmatter are
normative. Neutral surfaces do most of the work; color marks orientation or
state instead of dividing every concept into a new visual world.

### Primary

- **Territory Signal** (`signal`): the hero, selected states, and a small number
  of primary actions.
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

**The Quiet Signal Rule.** Muted berry anchors the hero and selected states.
Supporting sections return to neutral surfaces instead of repeating saturated
fields.

**The Evidence Color Rule.** Blue-green always means route, focus, or evidence.
It cannot become a second ornamental brand fill.

## 3. Typography

**Display Font:** Bahnschrift with DIN Alternate and Arial Narrow fallbacks

**Body Font:** Atkinson Hyperlegible with Trebuchet MS and Segoe UI fallbacks

**Data Font:** Cascadia Code with SFMono-Regular and Consolas fallbacks

**Character:** The condensed display stack behaves like a precise instrument
heading, while the humanist body stack stays readable across platforms. The
monospace data face is reserved for indices, contracts, and route coordinates.
All stacks remain useful without a network font dependency.

### Hierarchy

- **Display** (720, fluid to 5.4rem, 0.94): hero and major orientation statements.
- **Headline** (800, fluid to 4.8rem, 0.98): section decisions and transitions.
- **Title** (700–800, 1.25–1.55rem): route stops and operational concepts.
- **Body** (400, 1.0625rem, 1.62): explanations, capped near 60–68 characters where practical.
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
- **Primary:** True White with Deep Coordinate text on the hero; Territory
  Signal with white text on neutral installation surfaces.
- **Hover / Focus:** two-pixel lift on hover; three-pixel Verified Route focus ring.
- **Secondary:** transparent or white surface with a one-pixel semantic border.

### Chips

- **Style:** compact pills are reserved for genuine state labels, not the mode
  diagram.
- **State:** pills identify state but do not impersonate buttons unless interactive.

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

### Main-Unknown Decision Map

The hero's signature diagram begins with one explicit question: "What is the
main unknown?" Four visible spokes pair a recognizable task condition with
Survey, Track, Prove, or Expedition. The map is not a maturity ladder and does
not require visitors to infer meaning from position or decoration. Each route
is a keyboard-accessible link that selects the matching mode explanation and
retains useful anchor navigation when JavaScript is unavailable.

### One-Viewport Chapters

On desktop viewports at least 650 pixels tall, the hero, mode chooser, worked
example, operating promises, and installation each occupy one screen.
Viewport-relative vertical padding keeps the full chapter visible while
scrolling remains natural; page-level snapping is avoided because it can fight
wheel and trackpad input. Mobile content also remains naturally scrollable
where forcing a single-screen height would clip text or controls.

### Progressive Disclosure

The primary journey contains only the promise, mode choice, worked example,
three operating promises, and installation. Detailed taxonomy, guardrails,
execution, delivery, loading, and evaluation policy use native `details`
elements beneath a clearly labelled operating-model boundary.

**The Essentials-End Rule.** A visitor can understand and install the skill
without opening the operating-model disclosures. Expanded policy remains
available for verification and existing-user reference.

## 6. Do's and Don'ts

### Do:

- **Do** make modes, gates, and evidence relationships directly interactive.
- **Do** preserve readable fallback content without animation or JavaScript.
- **Do** use asymmetric composition when it clarifies hierarchy.
- **Do** provide visible focus and a complete reduced-motion alternative.
- **Do** use exact canonical vocabulary from the skill and README.
- **Do** demonstrate the workflow with one concrete request before exposing
  the complete policy model.

### Don't:

- **Don't** use generic SaaS landing pages built from repetitive feature-card grids.
- **Don't** use fantasy-expedition cosplay.
- **Don't** use dark neon "AI terminal" styling.
- **Don't** use editorial-magazine layouts that obscure sequence or evidence.
- **Don't** use gradient text, decorative glassmorphism, side-stripe accents, or wide ghost-card shadows.
- **Don't** imply that deterministic validation is fresh behavioral evidence.
- **Don't** make optional reference depth part of the required reading path.
