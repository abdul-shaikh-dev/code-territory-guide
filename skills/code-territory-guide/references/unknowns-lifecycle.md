# Unknowns Lifecycle

Load this reference for vague, unfamiliar, product-facing, architecture-sensitive,
multi-step, or reviewer-sensitive work. Use only the techniques needed to make
material unknowns cheap to discover before they become expensive to reverse.

## Collaborator Context

Use context the user already supplied about their starting point. Ask for one
missing item only when it would materially change discovery, explanation, or the
route:

- domain familiarity
- repository familiarity
- decisions or approaches already explored
- current understanding of what good looks like

Do not turn this into a standard intake questionnaire. Calibrate blind-spot
explanations to the collaborator: connect unfamiliar territory to concepts they
already know, avoid reteaching established knowledge, and give them language
that improves the next prompt or decision.

## Unknown Matrix

Classify the map-to-territory gap:

- **Known knowns** — explicit requirements and constraints in the request.
- **Known unknowns** — decisions or information the user knows are unresolved.
- **Unknown knowns** — tacit preferences or success criteria the user can
  recognize but has not articulated.
- **Unknown unknowns** — risks, conventions, possibilities, and quality bars
  neither side has considered yet.

The matrix is a discovery checklist, not a required document. Name only
categories that contain material information.

## Before Implementation

Choose the cheapest technique that can close the material gap:

1. **Blind spot pass** — inspect the repository and domain for unknown unknowns.
   Explain the few findings that could change the route or help the user prompt
   more precisely. Calibrate the explanation to the collaborator context when
   known.
2. **Brainstorm or prototype** — use when success is easier to recognize than
   describe. Produce small, reversible alternatives that expose preferences;
   do not build production infrastructure merely to obtain feedback.
3. **Reference** — ask for or inspect an example when prose cannot efficiently
   specify the desired semantics or quality. Prefer source code for structural
   or behavioral fidelity; diagrams, documentation, screenshots, and recordings
   remain useful for other qualities. Treat references as evidence, not authority
   to copy unrelated behavior.
4. **Interview** — ask one targeted question at a time when its answer could
   materially change architecture, data or API contracts, security,
   compatibility, deployment, UX, test strategy, or the definition of success,
   and repository evidence cannot resolve it. Do not interview for cosmetic,
   reversible, or mechanically inferable choices.
5. **Decision-first plan** — lead with the decisions the user is most likely to
   revise: data models, interfaces, contracts, UX flows, rollout, and visible
   behavior. Put mechanical edits after them.

Complete discovery when every route-changing unknown is resolved, explicitly
deferred, or presented as a decision the user must make. Do not pretend that a
recommendation resolves a tacit user preference.

## During Implementation

Unknown unknowns can appear after plan approval. When new evidence forces a
departure from the route:

1. Stop before expanding scope or crossing a canonical confirmation gate.
2. Choose the conservative reversible option only when the canonical policy
   permits autonomous continuation.
3. Record the unknown, evidence, decision, and plan deviation when the work is
   multi-session, delegated, or materially affected.
4. Update the Field Brief or use a temporary `implementation-notes.md`; do not
   create a deviation log for routine local choices.
5. Revalidate the affected acceptance criteria.

The deviation record is part of the map for the next session, not a substitute
for informing the user about a material decision.

## After Implementation

Close the remaining reviewer and user unknowns proportionately:

- **Reviewer evidence** — owned diff, validation, risks, compatibility, and
  recovery details.
- **Stakeholder explanation** — outcome, visible behavior, prototype, screenshot,
  before/after, or demo GIF when these make approval materially easier.
- **Understanding check** — offer or create an explainer and quiz when the user
  requests knowledge transfer or when they explicitly require demonstrated
  understanding before merge. Do not make quizzes a universal merge gate.

For substantial work, explain the result in the order its audience needs:
outcome and demonstration first, technical evidence second.

When one shareable approval artifact would reduce reviewer unknowns, copy
assets/artifacts/explainer.md and package only the useful plan, prototype,
material deviations, outcome, demonstration, risks, and reviewer evidence.
