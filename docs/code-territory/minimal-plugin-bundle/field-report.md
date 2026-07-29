# Field Report: Minimal plugin bundle

## Completion

Complete

## Outcome

Repository marketplaces now install from a generated minimal plugin root at
`plugins/code-territory-guide/` instead of treating the development repository
root as the plugin. The bundle contains only Codex and Claude manifests, the
Git-tracked runtime skill, and the intentionally distributed portable
`AGENTS.md` under `assets/portable/`.

The canonical skill remains under `skills/code-territory-guide/`.
`scripts/sync_plugin_bundle.py` generates the installable copy from Git-tracked
skill files and rejects missing, changed, stale, unexpected, forbidden, or
non-ignored untracked files. Codex installation
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

- `python scripts/sync_plugin_bundle.py --check` — passed; 23 exact files.
- `python <plugin-creator>/scripts/validate_plugin.py plugins/code-territory-guide`
  — passed.
- `python evals/validate_package.py` — passed; manifests aligned at `0.3.1`.
- `python -m unittest discover -s evals/tests -v` — passed; 41 tests.
- `git diff --check` — passed; line-ending normalization warnings only.
- Failure classification: the earlier generator discovered files by walking the
  working tree, so ignored caches needed a growing exclusion list and
  non-ignored untracked files could enter the bundle. This task-caused
  packaging weakness is resolved by deriving skill membership from Git's index
  and rejecting non-ignored untracked skill files.
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
  `git add` and `python scripts/sync_plugin_bundle.py --write`; untracked
  canonical files intentionally block generation, and deterministic validation
  prevents an out-of-sync bundle from passing CI.

## Delivery

- State: pull request updated and ready for review.
- Commit or link:
  <https://github.com/abdul-shaikh-dev/code-territory-guide/pull/18>
- Commit convention: Conventional Commit-style subject from repository history
- Intentionally uncommitted: none planned

## Review and recovery

- User review: confirm that exposing the portable `AGENTS.md` as a copyable
  plugin asset matches the intended workplace workflow.
- Rollback guidance: restore both marketplace sources to `./`, remove the
  generated bundle and synchronizer, and revert the package-validation and
  installation-documentation changes.

## Durable learning

Saved in this report: repository marketplace source paths control the installed
plugin root, while Codex sparse marketplace checkout controls which repository
paths are retained in the marketplace snapshot.
