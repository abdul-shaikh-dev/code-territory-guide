# Model Routing

Use this reference when choosing which model should plan, implement, review, or rerun work.

## Principle

Match model capability to the outcome required at each stage of the workflow.
Use the cheapest model that can meet the quality bar, but escalate without
hesitation when the output affects shipped behavior, architecture, security,
user experience, data integrity, public contracts, or review quality.

Cost is a tie-breaker only after quality, correctness, and risk are satisfied.
One task may use different models as uncertainty falls: a strong model can
resolve the route, then a lower-cost model can execute a sufficiently explicit
brief.

## Default Routing

- **Sol role**: use for ambiguous requirements, architecture, difficult
  debugging, risk and scope decisions, security/data/API/deployment changes,
  implementation briefs, taste-sensitive work, and consequential final review.
- **Luna execution role**: use for read-heavy exploration, repository mapping,
  supporting-document review, well-specified implementation, bounded
  multi-step tool workflows, mechanical edits, tests, evaluations, routine
  review, and routine documentation.

In Codex, use these exact defaults when the models are available:

| Work | Model | Reasoning effort |
| --- | --- | --- |
| Deterministic test/build execution, formatting, and evidence collection | `gpt-5.6-luna` | `low` |
| Normal exploration, well-specified implementation, and test authoring | `gpt-5.6-luna` | `medium` |
| Complex but well-specified implementation or routine review | `gpt-5.6-luna` | `high` |
| Rare, difficult, fully specified work with an expected quality gain | `gpt-5.6-luna` | `xhigh` |
| Ambiguous or consequential decisions and consequential final review | GPT-5.6 Sol (`gpt-5.6`) | `high` |

Move up the Luna ladder while the route remains explicit. Switch to GPT-5.6
Sol (`gpt-5.6`) at `high` when the work requires route-changing judgment or
crosses a consequential risk boundary.

## Escalation Rules

Escalate reasoning effort or route to Sol without hesitation when:

- the cheaper model produces vague, incorrect, incomplete, or overbroad work
- the task involves unknown architecture, unclear ownership, or hidden coupling
- the change can materially affect users, data, security, reliability,
  performance, compatibility, or deployment
- the implementation starts drifting from the brief
- tests fail for reasons the current model cannot explain cleanly
- review finds missed requirements, weak tests, avoidable complexity, or scope creep

Use Luna `medium` when semantic judgment or file changes begin. Use Luna `high`
for complex logic, edge cases, or routine review. Use Luna `xhigh` only when the
work remains fully specified and deeper reasoning is expected to improve the
result. Route to Sol `high` when requirements, architecture, ownership, hidden
coupling, consequences, or expected behavior require judgment rather than more
execution effort.

Do not continue polishing mediocre work with the same configuration when a
stronger review or rerun would be cheaper than shipping risk.

## Taste-Sensitive Work

For user-facing work, select a model with strong judgment, not just raw implementation ability.

Taste-sensitive work includes:

- UI/UX behavior and visual design
- copy, naming, empty/error/loading states
- API ergonomics and developer experience
- public documentation
- accessibility and interaction details

For these tasks, prioritize judgment and review quality over cost.

## Well-Specified Execution

Lower-cost models are appropriate for more than single mechanical steps when:

- the brief is explicit
- the change is localized
- expected behavior is already clear
- tool access and intermediate checkpoints are defined
- tests or checks provide fast feedback
- failures have an unambiguous escalation path
- the work may be multi-step but does not require route-changing judgment

This can include implementing a clear brief, using tools, running and updating
narrow tests, evaluating results, and completing routine follow-through. Even
for well-specified work, escalate if the output violates scope, misses edge
cases, encounters unexplained failures, or requires repeated correction.

## Review Independence

When practical, use a different agent or model configuration for review than
the one used for implementation. Luna `high` is sufficient for routine owned-
diff review; use Sol `high` for consequential review.

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

The explicit model identifiers above are the default Codex mapping. Do not
encode prices in the workflow because they change independently of the routing
contract.

When those models are unavailable, preserve the two-role strategy: map the Sol
role to the environment's strongest reasoning model and the Luna role to its
fastest lower-cost model that can reliably complete the explicit brief. If no
safe lower-cost option exists, keep the work on the stronger model.
