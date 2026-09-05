# Personal skill remediation

## Status

**Applied and verified.** After automatic review rejected the original batch,
the user explicitly approved the concrete 22-file scope. All entries in
the local `personal-fixes.json` manifest (published as [focused patches](patches/README.md)) were applied with source-hash checks
and backups, and the installed bytes match the manifest. A second dry-run
reports no outstanding changes.

Backup receipt:
`C:/Users/abdul/AppData/Local/Temp/skills-audit-backup-g6rbiuff/files/receipt.json`.

## Applied changes

| Root | Files | Intended correction |
| --- | --- | --- |
| `C:/Users/abdul/.agents/skills/impeccable` | `SKILL.md`, `reference/{craft,codex,shape,critique,hooks,init,live,polish}.md` | Concise trigger; resolve every documented helper call from the loaded skill root and actual project; allow clear authorized UI work to continue; retain optional supervised visual exploration and final QA. |
| `C:/Users/abdul/.agents/skills/find-skills` | `SKILL.md` | Trigger only for explicit skill discovery, installation, listing, updates, or capability extension. |
| `C:/Users/abdul/.agents/skills/writing-great-skills` | `SKILL.md`, `GLOSSARY.md`, `agents/openai.yaml` | Preserve the description; describe host-specific invocation; move explicit-only policy to Codex `agents/openai.yaml`. |
| `G:/Projects/2026/cool_projects/controlled-coding-workflow-plugin` | four `SKILL.md` files and new `agents/openai.yaml` files | Explicit opt-in supervised mode; policy disables implicit invocation; permit authorized plan-plus-scaffold work; avoid a redundant confirmation for an exact authorized slice. |
| `G:/Projects/2026/cool_projects/copilot-ghost-implementer` | `references/evaluation.md` | Persist a gotcha only when verified reusable, not already covered, and authorized. |

## Baseline evidence

- `controlled-coding-workflow-plugin`: clean at `615fd9a fix: simplify ghost prompt wording`.
- `copilot-ghost-implementer`: no `.git` directory observed.
- The Code Territory Guide worktree contained pre-existing user-owned changes;
  only this untracked audit record was added here.

## Validation ready after an approved write

1. Back up every external target to a timestamped `TEMP` directory and retain
   a manifest plus the fresh baseline.
2. Run `skill-creator/scripts/quick_validate.py` for each changed skill.
3. Parse every new or changed `agents/openai.yaml`, check all direct Markdown
   links, and search the affected Impeccable/controlled references for
   contradictory mandatory gate text.
4. From an unrelated temporary project directory, invoke Impeccable helpers
   by the loaded skill-root path and pass the actual project target.

## Isolated proposal validation

The proposed files were copied into an isolated `TEMP` workspace and checked
without changing any source target.

- `quick_validate.py` passed for find-skills, writing-great-skills, and all
  four controlled-coding skills. Impeccable reports its existing `version`
  frontmatter field as unsupported by this generic validator; the proposal
  preserves that field rather than deleting installation metadata.
- All six staged `openai.yaml` files parse. The writing and four controlled
  policies set `allow_implicit_invocation: false`.
- Relative Markdown links resolve in the staged roots. All 34 documented
  Impeccable helper calls have a closed, quoted `$SKILL_ROOT/scripts/...`
  path. Searches of the directly involved Impeccable and controlled-coding
  references found no surviving contradictory mandatory gate language.
- Every `after_text` value in the 22-entry manifest is LF-normalized; none
  contains carriage returns. The controlled normal flow now reuses exact
  authorization unless supervision was requested, while dry-run and
  integration confirmations remain for requested or unresolved scope. Its
  dry-run template asks “Confirm scaffold?” only on that confirmation branch;
  an exact authorized slice instead records that it is proceeding.
- The staged Impeccable `context.mjs` ran from `C:/Windows/Temp` against an
  unrelated temporary target. It resolved that target correctly. Its legacy
  `NO_PRODUCT_MD` message remains helper output; the revised skill entrypoint
  explicitly treats it as non-blocking for clear authorized work.

## Authorization history

The automated reviewer rejected the initial batch and required informed explicit
approval. The user subsequently approved the exact staged scope; the approved
batch succeeded without bypassing the review.

## Final verification and superseded skills

All 22 installed files match the reviewed patches and parse as applicable.
The installed Impeccable context helper ran successfully from an unrelated
working directory with an explicit target; all 34 documented helper paths resolve.

The user subsequently identified controlled-coding-plan and
copilot-ghost-implementer as superseded by Code Territory Guide and authorized
removing their installed skill entries. Neither is present in the inspected
active skills directories or Codex configuration. Only source projects were
found; those projects were preserved. No removal was necessary.
