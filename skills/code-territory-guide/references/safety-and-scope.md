# Consequential Scope and Ownership

Use this reference when the routine [SKILL.md](../SKILL.md) rules leave a
material authorization or ownership question. Shared trust, validation, and
completion rules remain in that entrypoint.

## Overlapping user changes

A non-overlapping edit leaves user-owned lines and their semantics untouched.
Appending logic to one of those lines, reformatting it, or absorbing it into a
replacement block still counts as overlap. Adjacent additions can also change
the behavior of a user's edit even when the textual hunks are separate.

When the request authorizes overlap, preserve the unrelated intent and review
the combined behavior. If ownership or intended behavior remains unresolved,
ask about that specific conflict; continue independent work in the meantime.

## Consequential scope decisions

Check whether the existing request covers the proposed action when discovery
reveals a need to change:

- dependencies, public APIs, compatibility, or persisted data contracts
- migrations, authentication, authorization, or security behavior
- infrastructure, deployment, or operational data
- unrelated modules through a broad refactor
- public files, routes, functions, or configuration through deletion or renaming
- data or history through destructive or bulk operations

These categories warrant a scope check, not automatic reapproval. An authorized
migration or API change can proceed within its agreed boundary. A local,
reversible implementation choice does not expand scope merely because another
approach is possible.

When an action falls outside current authority, explain the necessary expansion
and its concrete consequence before asking. If the answer is unavailable, keep
that portion pending and report the remaining decision.

## Unclear intent versus missing evidence

Inspect code and tests to resolve factual uncertainty. When a plan conflicts
with established behavior, identify the conflicting contracts before changing
either. Use [unknowns-lifecycle.md](unknowns-lifecycle.md) if materially different
product outcomes remain and evidence cannot establish which the user intends.
A question about one contract does not turn the entire execution plan into an
approval gate.

For authority specific to Git publication, use [delivery.md](delivery.md).
