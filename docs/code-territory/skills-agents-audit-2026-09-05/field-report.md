# Skills and AGENTS remediation — 5 September 2026

The Code Territory Guide and global-guidance changes are installed. CogVest
PR [264](https://github.com/abdul-shaikh-dev/CogVest/pull/264) is merged.
All 22 personal and 13 vendor skill patches are applied and verified. This report supersedes the original audit's
implementation status without rewriting its historical observations.

## Audit disposition

| Finding | Result |
| --- | --- |
| 1. Conflicting model routing | One mapping in Code Territory Guide; global guidance points to it. Keep the capable current primary, including Astra. |
| 2–3. Impeccable pauses and helper paths | Applied: optional supervised exploration, authorized implementation continues, helpers resolve from the loaded skill. |
| 4. Controlled coding | Applied: explicit supervised activation, reuse exact authorization, create a canonical plan with scaffolding when authorized. |
| 5–6. Code Territory Guide overhead and approval wording | Implemented: self-sufficient routine entrypoint, conditional references, evidence-based discovery, factual corrections and internal choices proceed. |
| 7. Broad descriptions | Code Territory Guide narrowed; personal and Figma refinements applied. |
| 8. Invocation guidance | Applied: host-specific metadata with required descriptions preserved. |
| 9. Portable manual | Compact self-contained default plus optional `portable/full/AGENTS.md`. |
| 10. CogVest | Merged: existing approved issues/requests qualify as contracts; new-task synchronization is distinguished from resumed work. Historical copies retained. |
| 11. Missing tools | Applied capability-aware routes; no claim that editing instructions creates missing browser or connector access. |
| 12. Figma component/library scope | Applied focused existing-library route; full-library process remains available. |
| Remaining observations | Applied proportional image/capture/rendering defaults and conditional reusable gotchas. Unaffected skills and archived evidence retained. |

## Installed and delivered

- Canonical Code Territory Guide, generated package, compact/full portable
  guidance, README, and package-version validation are included in the Code Territory Guide delivery change. The source worktree began clean except the audit artifacts.
- Codex's local marketplace registration points to this source checkout.
  The refreshed installed version is `0.3.7+codex.20260905132506`; the shared
  release remains `0.3.7`. The version validator accepts the official Codex
  cachebuster while rejecting base-release drift and malformed suffixes.
- Global `C:/Users/abdul/.codex/AGENTS.md` is updated. Backup receipt:
  `C:/Users/abdul/AppData/Local/Temp/skills-audit-backup-9eyke3c7/files/receipt.json`.
- CogVest's isolated documentation branch committed `ea0ab391abcc78b30a81d95a74399537bfd40df`.
  GitHub reports PR 264 merged at `2026-09-05T13:36:48Z`, merge commit
  `b8eac69fa602a85583b8048460c7e607e3664e5b`. The unrelated feature checkout
  was not switched or synchronized.

## Verification and practical limits

- Code Territory Guide skill metadata, package validation, bundle synchronization,
  eight package tests, local Markdown links, source/installed parity, and
  `git diff --check` passed.
- [Three isolated task probes](forward-check.md) completed: typo correction,
  a bounded clamp fix with three passing tests, and misleading deletion copy
  corrected from an existing recovery contract without an extra approval.
  These are smoke checks, not a comparative performance or release evaluation.
- The patch installer checks every source hash before writing, backs up existing
  files, records new files, verifies writes, rolls back task-owned writes after
  failure, and rejects source drift. Isolated checks covered existing/new files,
  simulated write failure, rollback, idempotence, and allowlist enforcement.
- Vendor patches are version-specific reviewable records. A future vendor update
  can replace them; review and reapply against that version rather than forcing
  a stale patch. No automatic update hook or maintained vendor fork is implied.
- Start a new Codex thread to reload the installed skills and guidance. Historical
  marketplace/evaluation snapshots remain unchanged. Live Figma/browser behavior
  has not been verified when its required capability is unavailable.

## External patch completion

Automatic approval review initially rejected the personal batch because it
persistently changes approval and invocation rules across installed skills
and adjacent projects. The user explicitly approved the concrete reviewed
22-file scope, after which application succeeded. Both patch sets match
installed bytes and their idempotent dry-runs report no outstanding changes.

- Personal backup receipt: `C:/Users/abdul/AppData/Local/Temp/skills-audit-backup-g6rbiuff/files/receipt.json`
- Vendor backup receipt: `C:/Users/abdul/AppData/Local/Temp/skills-audit-backup-1mhw2m07/files/receipt.json`
- Figma link correction receipt: `C:/Users/abdul/AppData/Local/Temp/skills-audit-backup-tobmx_7d/files/receipt.json`

[Personal changes](personal-fixes.md) and [vendor changes](vendor-patches/ledger.md)
record exact scope and manifest links. Metadata parses, 125 relative file links
resolve, and all 34 documented Impeccable helper paths exist. Its installed
context helper ran from an unrelated directory with an explicit project target.
The generic skill validator's existing rejection of Impeccable's `version`
frontmatter field remains; that installation metadata was deliberately preserved.

## Superseded skills

The user identified controlled-coding-plan and copilot-ghost-implementer as
superseded by Code Territory Guide and authorized removing them from the skills
directory. Neither has an installed entry in the inspected active skills
directories or Codex configuration. They were already inactive in the original
audit. Only source projects were found, which were preserved; there was no
installed entry to remove. No historical copy was rewritten to simulate removal.

Remediation is complete within the audited boundary. The unavailable live
browser/Figma capabilities remain environmental limitations, not unfinished
instruction edits. No application code was changed. CogVest PR 264 is merged. The controlled-coding source changes are committed
and published in [PR 6](https://github.com/abdul-shaikh-dev/controlled-coding-workflow-plugin/pull/6)
(`24ace31dceed99979878bbfcc8ae08bf2fde7979`). Code Territory Guide source changes
and the focused external patch records are delivered together in this change.
The controlled-coding original checkout retains its working copy; its PR was
created from a separate clean worktree to preserve that branch.

## Delivery and simplified validation

At the user's request, model-based runners, judges, fixtures, schemas, frozen
locks, and their harness tests were removed. The package/site validators and
32 ordinary tests now live under `scripts/` and `tests/`. Normal CI runs those
checks without model calls, API keys, benchmark records, or lock maintenance.
The two historical evidence summaries are preserved in `docs/archive/evaluations/`;
ignored local run records were not touched. No old result validates the new skill.

Automatic review initially rejected bulk removal as broader than runner removal.
After reviewing the exact 52-file scope, the user explicitly approved it and the
two-report archive move. All removal targets were hash-checked and backed up at
`C:/Users/abdul/AppData/Local/Temp/ctg-eval-removal-6462cce6f9854443b0e9d94372d75b1d`.
The earlier prospective-lock refresh was superseded by removal of the framework.

Six focused external patches cover 36 files, including global guidance. Their
isolated application round-trips to the exact intended text. Complete installed
vendor files, local replacement manifests, and the machine-specific installer
are excluded from Git; their focused changes remain reviewable in this PR.
