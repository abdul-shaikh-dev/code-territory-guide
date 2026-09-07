# Model Routing

Use this reference when choosing a worker, escalating, or handling an unavailable
model. Keep the current capable primary agent by default. Delegate only bounded,
independent work whose benefit exceeds coordination cost. User-selected models
and reasoning preferences take precedence.

## Select by role

This is the skill's canonical routing policy. Resolve model identifiers and
supported reasoning settings from the current host when delegation is needed;
reuse that inventory during the task. No release-number lookup is required.

| Role | Work boundary | Selection criterion |
| --- | --- | --- |
| Primary | Task judgment, integration, and final accountability | Keep the capable current agent |
| Judgment | Unresolved architecture, consequential contracts, difficult diagnosis | A host-described model suited to complex reasoning |
| Exploration and execution | Repository mapping, explicit multi-step implementation, substantive review | A capable coding model with enough context for the owned slice |
| Narrow execution | Localized repeatable edits, focused tests, mechanical evidence collection | A lighter coding model when the scope and acceptance criteria are explicit |

If the host offers Astra, Sol, Terra, and Luna, the familiar preferences are
Astra as the existing primary, Sol for judgment, Terra for exploration and
execution, and Luna for narrow execution. These family preferences do not pin a
release or imply a ranking for models the host has not described. On other
hosts, apply the role criteria directly. If capability information is insufficient,
keep the primary rather than guessing an identifier or delegating blindly.

Preserve the session's reasoning preference when applicable; otherwise use the
selected model's host default. Increase supported effort only for a concrete
unresolved reasoning problem. Mechanical work does not require high effort by
policy. Do not infer relative price or speed from model names.

## Escalation and fallback

Reassign narrow work when it becomes exploratory or edge-heavy. Return unresolved
architecture, ownership, or consequential decisions to the primary or a judgment
worker. After an unexplained failure, inspect its cause before deciding whether
a stronger worker would help; repeated blind retries are not an escalation route.

If a chosen model is unavailable, select another callable model meeting the same
role criteria or complete the slice with the primary. Report a material fallback
and its actual validation limits. Revisit routing when host availability changes
or observed work exposes a capability mismatch; no scheduled benchmarks or
model-backed evaluation suite are required.

## Handoffs

Avoid simultaneous writers on the same files. A handoff includes the original
request, applicable constraints, baseline/user-owned changes, owned boundaries,
acceptance criteria, validation route, and unresolved decisions. Keep narrow
handoffs in chat; use [artifacts.md](artifacts.md) when durable coordination helps.

Use a separate reviewer when an independent perspective materially improves
confidence in a consequential change. Otherwise review locally against the
original request and verification evidence.
