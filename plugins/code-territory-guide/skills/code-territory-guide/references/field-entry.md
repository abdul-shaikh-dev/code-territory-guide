# Field Entry: Safer Workspace Deletion

Use this compact example to understand how the guide collaborates with a user
before, during, and after implementation. It is illustrative, not a required
template.

## Starting Map

User request:

> Add a safer workspace deletion flow. I know the right confirmation when I
> see it, but I am unfamiliar with this part of the app.

That starting context matters. It identifies a tacit UX preference, admits a
repository blind spot, and leaves the implementation open to evidence.

## Survey

Inspect the current settings flow, deletion contract, adjacent confirmation
dialogs, accessibility conventions, and focused UI tests. The repository shows
that deletion is consequential, but it does not settle which confirmation
interaction best fits the product.

Create three disposable, fake-data directions: a standard confirmation, a
typed workspace-name confirmation, and a staged warning that first explains
impact. The user selects the typed confirmation because it feels deliberate
without adding unnecessary steps.

## Expedition Route

Reuse the existing dialog and form patterns. Require the exact workspace name,
preserve the current API contract, keep keyboard and screen-reader behavior,
and add focused tests for mismatch, success, cancellation, and pending state.
Do not redesign the settings page or change deletion semantics.

The route is short enough to keep in chat. The prototype remains a decision
probe, not evidence that production behavior is complete.

## Route-Changing Evidence

During implementation, the API contract reveals that deletion is recoverable
for 30 days. The planned “permanently delete” copy is therefore inaccurate.
This is not a cosmetic wording choice: it changes the promise made to users.

Correct the copy to describe the verified recovery window while preserving the
requested deletion behavior. Explain the evidence and revalidate the UI and
tests. Ask only if the user intended to change deletion semantics or the
recovery contract remains uncertain; factual copy corrections need no separate
approval. Record the deviation when a durable brief already exists.

## Field Report

Lead with the outcome: workspace deletion now requires typing the workspace
name and accurately explains the 30-day recovery window. Then report the owned
files, focused tests, accessibility check, deviation from the original copy,
remaining risk, and actual delivery state.

## Other Useful Entries

- “Do a blind-spot pass on this authentication module. I am new to this
  subsystem; explain only the unknowns that could change the route.”
- “Prototype three toolbar layouts with fake data before wiring state. I can
  recognize the right density more easily than I can specify it.”
- “Interview me one question at a time about the import contract. Prioritize
  answers that would change compatibility or data integrity.”

Specific instructions are valuable when they describe real constraints. Do
not let them prevent a pivot when repository evidence proves that the planned
route or user-facing promise is wrong.
