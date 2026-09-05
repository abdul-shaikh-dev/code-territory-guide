# Model Routing

Use this reference when delegation, escalation, or fallback is actually needed.
Keep the current capable primary agent by default; do not hand off merely to
satisfy a model table. These are worker-selection defaults, not universal task
phases. User-selected models and reasoning preferences take precedence.

## Roles

- **Astra primary:** when already running GPT-6 Astra, keep task judgment,
  integration, and final accountability there. Delegate only independent work
  whose coordination cost is lower than doing it locally.
- **Sol judgment:** ambiguous planning, architecture, consequential decisions,
  difficult debugging, product taste, security/data contracts, and final review
  when a separate judgment worker materially improves confidence.
- **Terra exploration and execution:** repository mapping, supporting-document
  review, explicit multi-step implementation, edge cases, and substantive review.
- **Luna narrow execution:** repeatable localized implementation, focused tests,
  deterministic checks, formatting, and bounded evidence collection.

## Codex defaults

This table is the single authoritative model/effort mapping for this skill.
Other instruction files should reference it rather than repeat the mapping.

| Worker role | Callable model | Effort |
| --- | --- | --- |
| Judgment with unresolved requirements or consequential review | `gpt-5.6-sol` | `medium` |
| Judgment requiring deeper investigation or route-changing decisions | `gpt-5.6-sol` | `high` |
| Read-heavy exploration, explicit implementation, or substantive routine review | `gpt-5.6-terra` | `high` |
| Rare difficult work with fully specified scope and expected quality gain | `gpt-5.6-terra` | `xhigh` |
| Narrow repeatable implementation, focused tests, and mechanical checks | `gpt-5.6-luna` | `high` |

Use the identifiers actually offered by the host. Some hosts name Sol `gpt-5.6`;
that alias is not permission to pass an unavailable identifier to a tool. For
Astra keep the current user/session effort unless there is a reason to change it.
Do not encode prices or assert that a particular model is universally cheapest.

## Escalation and fallback

Move Luna work to Terra when it becomes exploratory or edge-heavy. Use deeper
Terra reasoning only while requirements remain explicit. Route unresolved
architecture, ownership, consequences, or repeated unexplained failures back to
the primary or a Sol judgment worker. Do not keep rerunning a failing configuration
when a stronger review is likely to resolve the issue.

When an exact model is unavailable, preserve its role with the closest callable
model. Use Terra for unavailable Luna; use a judgment-capable model for demanding
work when Terra or Sol is unavailable. Luna remains suitable only for narrow
explicit work. Report the actual fallback when material; never claim a model ran
when it did not. A capable single agent is a valid fallback.

## Handoffs and review

Avoid simultaneous writers on the same files. A bounded handoff includes the
original request, applicable instructions, baseline/user-owned changes, owned
boundaries, acceptance criteria, validation route, and unresolved decisions.
Keep narrow handoffs in chat. Use a durable brief for complex or multi-session
coordination when it prevents loss of context.

An independent reviewer is useful when risk warrants it. Otherwise start a fresh
pass from the original request, owned diff, and verification evidence, looking
for missed behavior, scope creep, compatibility changes, and false completion
claims. Independence is not a reason to delegate a tiny change.
