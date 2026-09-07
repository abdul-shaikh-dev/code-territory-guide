# Complex Expeditions

Use this reference for coupled contracts, substantial coordination, or complex
implementation. The routine SKILL.md route is enough for ordinary changes.
Load safety-and-scope.md when a consequential authorization or ownership
boundary needs its detailed policy.

## Establish the route

When documentation or a plan conflicts with tested behavior, name both sides.
Do not erase a compatibility test merely to make newer prose pass. Preserve
coexisting behavior where possible; a breaking request can authorize a changed
contract, but an ambiguous plan cannot silently do so. Ask only for unresolved
user intent that changes the contract, risk, or authorized scope.

Use unknowns-lifecycle.md for material tacit criteria or unresolved product
choices, not as an automatic preliminary phase. Keep a concise route containing
acceptance criteria, owned boundaries, preserved behavior, and verification.
Routine choices and factual corrections within that route proceed autonomously.

## Coordinate only as needed

Use [model-routing.md](model-routing.md) for worker selection and handoffs, and
[artifacts.md](artifacts.md) for durable records or cross-repository coordination.
For coupled changes, establish dependency order and verify both sides of each
shared contract before treating any dependent slice as complete.

On resumption, compare open records against the present worktree and source.
Reuse verified work; do not repeat a step just because an old checklist is open.
Revalidate when relevant inputs changed and record material drift when useful.

## Implement and verify

Use the highest changed boundary to select sufficient evidence:

| Changed boundary | Evidence |
| --- | --- |
| Prose or metadata | Focused inspection and relevant parser/link checks |
| Local behavior | Focused tests of changed and preserved behavior |
| Module, process, or service contract | Narrow integration/contract checks |
| Public API or persisted format | New and preserved consumer compatibility |
| Data, migration, authentication, or security | Positive/negative cases, failure paths, and recovery where relevant |
| Material UI behavior | Behavioral checks and focused visual inspection when available |

Honor repository-required checks. Broaden validation when risk or failures
justify it; do not repeat passing checks without a changed input or concern.
Classify failures as task-caused, pre-existing, or environmental. Fix task-caused
failures before claiming completion; disclose other failures and missing checks.

## Review the coupled result

Review interactions across owned slices as well as individual diffs. Check that
local fixes preserve shared contracts and that material artifacts describe the
verified result. Overall completion requires every requested repository slice
and shared check; a passing check in one repository cannot establish another's
compatibility.
