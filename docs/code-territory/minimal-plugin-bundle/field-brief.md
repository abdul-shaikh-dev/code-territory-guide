# Field Brief: Minimal plugin bundle

## Decisions most likely to change

- Keep `skills/code-territory-guide/` as the canonical editable source and
  generate the installable plugin bundle instead of maintaining a second skill
  by hand.
- Point repository marketplaces at `plugins/code-territory-guide/` and use
  sparse checkout for Codex marketplace installation.

## Objective

Install only the runtime plugin files rather than caching repository-only
documentation, evaluations, site sources, and development configuration as the
plugin. Preserve all existing skill behavior and supported adapter metadata.

Acceptance criteria:

- `plugins/code-territory-guide/` contains only plugin manifests, the canonical
  skill copy, and the intentionally distributed portable `AGENTS.md`.
- A deterministic command synchronizes the bundle from canonical sources and
  detects missing, stale, changed, or unexpected files.
- Codex and Claude marketplace entries resolve to the minimal plugin root.
- Codex installation documentation uses sparse marketplace checkout.
- Existing package and evaluation validation remains green.

## Territory

- Owning files or hunks: marketplace manifests, package validator, installation
  documentation, bundle synchronizer, generated plugin bundle, and this brief.
- Relevant behavior and patterns: plugin manifests activate `./skills/`;
  repository marketplaces currently use the repository root as plugin source.
- Worktree baseline: `feat/portable-agents-guide` at `e55d65d`; the untracked
  `portable/AGENTS.md` is task-owned work from the preceding request.

## Route

1. Add a deterministic bundle synchronizer with an exact file allowlist.
2. Generate the minimal plugin root from canonical sources.
3. Point marketplace entries at the minimal root.
4. Document sparse Codex installation and the generated bundle boundary.
5. Extend deterministic package validation and run plugin/package/tests.

## Preserve

- Canonical skill content and progressive-loading paths.
- Root manifests used by existing non-Codex adapters.
- Manual skill installation and evaluation source paths.
- Repository-only docs, evals, site, and development files outside the bundle.

## Non-goals and scope gates

- Do not publish, release, reinstall, or modify user-level plugin state.
- Do not change skill behavior or marketplace policy values.
- Do not redesign adapters whose installers necessarily fetch a full Git
  repository; document the verified Codex boundary without overstating others.

## Validation

- `python scripts/sync_plugin_bundle.py --check` — exact bundle parity and
  allowlist.
- `python evals/validate_package.py` — manifest alignment and repository package
  contract.
- `python <plugin-creator>/scripts/validate_plugin.py plugins/code-territory-guide`
  — official local plugin structure.
- `python -m unittest discover -s evals/tests -v` — deterministic regression
  suite.
- `git diff --check` — patch hygiene.

## Delivery authorization

Leave the completed and validated delta uncommitted.

- Commit convention: not needed without commit authorization.
- Ticket or issue identifier: not required.
