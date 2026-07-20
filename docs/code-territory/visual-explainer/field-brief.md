# Field Brief: Visual explainer and GitHub Pages

## Decisions most likely to change

- The production direction will be selected from a spacious narrative field
  instrument and a denser route-led reference surface.
- GitHub Pages will publish only `site/` through a dedicated Actions workflow;
  internal `docs/` artifacts will not be exposed.

## Objective

Create an accessible, responsive visual explainer that helps prospective and
existing users understand the skill, choose a mode, inspect its safety and
progressive-loading model, and reach installation or source details. Validate
the production page deterministically and render it in Chrome before delivery.

## Territory

- Owning files or hunks: `PRODUCT.md`, `DESIGN.md`, `site/`, the visual
  prototype under this directory, README links, deterministic site validation,
  tests, and the Pages workflow.
- Relevant behavior and patterns: the canonical vocabulary and claims in
  `README.md` and `skills/code-territory-guide/`.
- Worktree baseline: clean `main` at `65f58dd`, isolated on
  `feature/visual-explainer-pages` before edits.

## Route

1. Compare two materially different directions in a self-contained prototype.
2. Promote the user-selected Field Instrument direction; rendered browser
   validation remains pending because the available browser backends could not
   establish a supported control connection.
3. Add deterministic site checks, production deployment workflow, and README entry.
4. Run package, evaluation, unit, accessibility-oriented structural, and browser checks.

## Preserve

- The README remains the canonical detailed documentation.
- Existing deterministic CI and evaluation claims remain unchanged.
- The production site does not expose internal workflow artifacts or imply new
  behavioral evidence.

## Non-goals and scope gates

- No framework, package dependency, analytics, custom domain, or backend.
- Enabling Pages and Git delivery remain separate delivery capabilities.

## Validation

- Prototype static validation passed before Direction A was selected and the
  disposable file was removed.
- `python evals/validate_site.py` — production structure, links, assets, and accessibility contracts.
- `python -m unittest discover -s evals/tests -v` — deterministic regression suite.
- Chrome desktop and narrow rendering — visual and interaction review.

## Delivery authorization

Implementation and local validation are authorized. Commit, push, pull request,
merge, and Pages enablement require delivery confirmation after review.

- Commit convention: Conventional Commits, confirmed by recent history.
- Ticket or issue identifier: not required.
