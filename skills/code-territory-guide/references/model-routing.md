# Model Routing

Use this reference when choosing which model should plan, implement, review, or rerun work.

## Principle

Use the cheapest model that can meet the quality bar, but escalate without hesitation when the output affects shipped behavior, architecture, security, user experience, data integrity, public contracts, or review quality.

Cost is a tie-breaker only after quality, correctness, and risk are satisfied.

## Default Routing

- **Strong planning model**: use for ambiguous requirements, architecture, debugging strategy, risk analysis, test strategy, scope decisions, security/data/API/deployment changes, and implementation briefs.
- **Cheaper implementation model**: use for clear-spec implementation, mechanical edits, narrow tests, small documentation updates, and straightforward refactors from an approved brief.
- **Strong review model**: use for final diff review, shipped behavior, public API changes, UI/UX, security-sensitive changes, data changes, migration work, or anything where missing a defect is more expensive than rerunning the model.

## Escalation Rules

Escalate to a stronger model without hesitation when:

- the cheaper model produces vague, incorrect, incomplete, or overbroad work
- the task involves unknown architecture, unclear ownership, or hidden coupling
- the change can affect users, data, security, reliability, performance, compatibility, or deployment
- the implementation starts drifting from the brief
- tests fail for reasons the current model cannot explain cleanly
- review finds missed requirements, weak tests, avoidable complexity, or scope creep

Do not continue polishing mediocre work with the same weak model when a stronger review or rerun would be cheaper than shipping risk.

## Taste-Sensitive Work

For user-facing work, select a model with strong judgment, not just raw implementation ability.

Taste-sensitive work includes:

- UI/UX behavior and visual design
- copy, naming, empty/error/loading states
- API ergonomics and developer experience
- public documentation
- accessibility and interaction details

For these tasks, prioritize judgment and review quality over cost.

## Mechanical Work

Cheaper models are appropriate when:

- the brief is explicit
- the change is localized
- expected behavior is already clear
- tests or checks provide fast feedback
- the work is repetitive or mostly mechanical

Even for mechanical work, escalate if the output violates scope, misses edge cases, or requires repeated correction.

## Review Independence

When practical, use a different model for review than the one used for implementation.

The reviewer should inspect:

- correctness against the original request and brief
- unnecessary scope expansion
- missed tests or false validation claims
- compatibility and migration risks
- security, reliability, and data risks
- UI/accessibility gaps for user-facing work
- complexity that can be reduced

## Single-Model Fallback

When model switching or independent review is unavailable, do not weaken the quality bar. Use one model with explicit context boundaries:

1. Write the route or field brief before implementation.
2. Capture the worktree baseline and task-owned files or hunks.
3. Implement without rewriting the brief to fit the result.
4. Run and classify validation.
5. Start a fresh review pass from the original request, brief, baseline, owned delta, and validation evidence.

The review pass must look for disconfirming evidence rather than defend the implementation.

## Handoff Integrity

When work moves between models, pass the original request, canonical safety-and-scope policy, field brief, worktree baseline, owned files or hunks, validation commands, and pending decisions. Do not rely on a prose summary that omits constraints or pre-existing user changes.

## Environment-Specific Models

Do not hard-code model names, prices, or vendor-specific mechanics in this skill.

Each environment may have different model availability, pricing, limits, wrappers, or CLI access. Map the roles above to the best available models in the current environment.
