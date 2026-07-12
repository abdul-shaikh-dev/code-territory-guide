---
name: code-territory-guide
description: Guide non-trivial code changes through map-versus-territory discovery, trusted-context handling, worktree ownership, scoped planning, implementation, validation, owned-diff review, and explicitly authorized Git delivery. Use for ambiguous features, debugging, refactors, behavior or API changes, test-sensitive work, risk-sensitive implementation, committing completed work, or whenever assumptions, authorization, and scope must remain explicit. Start in Survey, Track, Prove, or Expedition mode according to the main uncertainty.
---

# Code Territory Guide

Treat the request as the map and the real repository as the territory. Discover material gaps, choose the lightest mode, make the smallest valuable change, validate it, and review only the task-owned delta.

## Vocabulary

- **Survey**: clarify an incomplete map before implementation.
- **Track**: follow evidence until a root cause is supported.
- **Prove**: lock down narrow behavior with a test.
- **Expedition**: plan, implement, validate, and review a scoped change.
- **Field Report**: hand off verified results and remaining uncertainty.

Skip the full workflow for tiny, obvious edits unless the user requests it or risk, ambiguity, public behavior, validation, or scope expansion is involved.

## Required Loading

Before any non-trivial task, read `references/safety-and-scope.md`.

Then load only what the task needs:

- Survey, Track, or Prove: `references/modes.md`
- Expedition planning through handoff: `references/standard-workflow.md`
- Copyable planner, implementer, reviewer, or handoff prompts: `references/templates.md`
- Model assignment or fallback: `references/model-routing.md`
- A compact worked example: `references/field-entry.md`
- Durable task documents: use the policy in `references/standard-workflow.md` and copy only the needed starter from `assets/artifacts/`

Do not execute a non-trivial task from this router alone.

## Mode Selection

- Use **Survey** for vague product, design, architecture, or multi-solution work.
- Use **Track** for broken, failing, flaky, slow, regressed, or inconsistent behavior.
- Use **Prove** when behavior is already clear, narrow, and testable before implementation.
- Use **Expedition** when the target is clear enough to plan and implement.

Survey and Track produce a target and then continue into Expedition. Prove continues into Expedition at owned-diff review, validation, learning, and handoff after the behavior is green.

## Core Loop

1. Select the lightest useful mode.
2. Read the canonical safety and scope policy.
3. Capture repository context and the pre-existing worktree baseline.
4. Mark a concise route and identify task-owned files or hunks.
5. Decide whether the task needs durable artifacts and announce the choice.
6. Prepare a field brief when implementation will be handed off, span sessions, or ambiguity warrants it.
7. Implement small, scoped patches.
8. Validate relevant behavior and classify failures.
9. Review only the task-owned delta against the request and brief.
10. Deliver through a branch, commit, push, or pull request only to the level authorized.
11. Save durable learnings only when useful and authorized by repository convention.
12. Produce a proportional Field Report in chat or as an artifact according to the announced choice.

Stop discovery once the owning seam, relevant contract, worktree state, and validation route are supported. Every additional search or reread must answer a specific unresolved material question. Reuse captured evidence; do not repeat broad inventory commands or expand a narrow task into full ceremony.

For a narrow task with a named behavior, default to three repository command batches after loading the skill: (1) instructions and worktree state, (2) owning source with nearest tests, and (3) one optional targeted check or history query. Combine related reads. Exceed this budget only after stating the unresolved question that could materially change the route. Do not repeat status, inventory, source, test, or failed-validation commands without new evidence.

Normal internal plans proceed without a separate approval pause. Ask the user only when `references/safety-and-scope.md` requires confirmation or a material design choice cannot be resolved from the request and repository.

This skill is self-contained. Its router and canonical references own the complete trust, scope, ownership, validation, review, artifact, and delivery policy; no companion `AGENTS.md` is required.

For work spanning multiple repositories, treat each repository as a separate boundary and load the multi-repository artifact and delivery rules in `references/safety-and-scope.md` and `references/standard-workflow.md`.
