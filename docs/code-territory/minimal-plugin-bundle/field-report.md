# Field Report: Minimal plugin bundle

## Completion

Complete

## Outcome

Repository marketplaces now install from a generated minimal plugin root at
`plugins/code-territory-guide/` instead of treating the development repository
root as the plugin. The bundle contains only adapter manifests, the complete
runtime skill, and the intentionally distributed portable `AGENTS.md`.

The canonical skill remains under `skills/code-territory-guide/`.
`scripts/sync_plugin_bundle.py` generates the installable copy and rejects
missing, changed, stale, or unexpected bundle files. Codex installation
guidance now uses sparse marketplace checkout to avoid fetching repository-only
docs, evaluations, site sources, and development configuration.

## Reviewer evidence

## Owned delta

- `.agents/plugins/marketplace.json` — points Codex at the minimal plugin root.
- `.claude-plugin/marketplace.json` — points Claude at the minimal plugin root.
- `plugins/code-territory-guide/` — generated installable plugin bundle.
- `scripts/sync_plugin_bundle.py` — deterministic generation and drift check.
- `portable/AGENTS.md` — standalone workplace-oriented workflow edition.
- `README.md` — sparse install guidance and package-layout documentation.
- `evals/validate_package.py` — marketplace and bundle contract validation.
- `docs/code-territory/minimal-plugin-bundle/` — durable route and verified
  report.

## Validation

- `python scripts/sync_plugin_bundle.py --check` — passed; 25 exact files.
- `python <plugin-creator>/scripts/validate_plugin.py plugins/code-territory-guide`
  — passed.
- `python evals/validate_package.py` — passed; manifests aligned at `0.3.1`.
- `python -m unittest discover -s evals/tests -v` — passed; 36 tests.
- `git diff --check` — passed; line-ending normalization warnings only.
- Failure classification: the first generation copied an ignored Python cache
  file; this task-caused packaging defect was removed and the generator now
  excludes common development caches.
- Not run: live marketplace reinstall, because the request did not authorize
  changing user-level plugin state or publishing a new version.

## Risks and gaps

- Existing Codex marketplace registrations made without sparse paths can retain
  a full repository snapshot until removed and re-added.
- Other Git-backed harnesses may still retain their marketplace source checkout
  even though the installed plugin root is now minimal.
- The manifest version is `0.3.1`; a release is still needed before existing
  installations can receive the new version.
- Canonical skill changes must be followed by
  `python scripts/sync_plugin_bundle.py --write`; deterministic validation
  prevents an out-of-sync bundle from passing CI.

## Delivery

- State: draft pull request authorized; final commit and PR identifiers are
  reported in the PR and completion handoff because this file is committed
  before the PR exists.
- Commit or link: reported in the completion handoff
- Commit convention: Conventional Commit-style `feat:` subject from repository
  history
- Intentionally uncommitted: none planned

## Review and recovery

- User review: confirm that distributing the portable `AGENTS.md` inside the
  minimal bundle is intentional.
- Rollback guidance: restore both marketplace sources to `./`, remove the
  generated bundle and synchronizer, and revert the package-validation and
  installation-documentation changes.

## Durable learning

Saved in this report: repository marketplace source paths control the installed
plugin root, while Codex sparse marketplace checkout controls which repository
paths are retained in the marketplace snapshot.
