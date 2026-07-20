# Artifacts, Prototypes, and Durable Re-entry

Load this reference when a task may need durable workflow artifacts, resumes
from existing task records, spans multiple repositories, or uses a visual
prototype. Read `safety-and-scope.md` first.

## Artifact Decision

Use artifacts to preserve useful execution context, not merely to satisfy process. Make and announce an artifact decision after discovery:

- Keep tiny edits, narrow Prove tasks, and short single-session work in chat.
- Materialize durable artifacts for multi-session work, delegated implementation, substantial Survey or Track findings, multi-step Expeditions, or when the user requests a written plan, investigation, or handoff.
- Follow an existing repository documentation convention first.
- When no convention exists, use `docs/code-territory/<task-slug>/`.

Resolve every artifact destination against the task-owning project root:

1. When Git is available, use `git rev-parse --show-toplevel` from the owning repository.
2. Otherwise use the workspace or project root explicitly supplied by the user or environment.
3. Treat `docs/code-territory/<task-slug>/` as relative to that root, not to the shell's incidental current directory.
4. Copy the selected starter from the installed skill's `assets/artifacts/` into the project destination, then edit the copy.

Never place task artifacts in the installed skill directory, user profile, a parent workspace merely because it contains repositories, or a nearby repository that does not own the task.

## Multiple Repositories

Treat every repository as an independent trust, worktree, ownership, validation, and delivery boundary.

For a feature spanning repositories:

1. Inventory only the repositories named by the request or proven to own part of the feature.
2. Capture branch, status, instructions, owned files, acceptance criteria, and validation separately for each repository.
3. Define cross-repository contracts, dependency order, compatibility expectations, rollout order, and end-to-end validation in one coordination brief.
4. Place the coordination brief only in an explicitly designated coordination repository or an existing repository convention for cross-project documentation.
5. If no coordination location is designated or established, keep the shared coordination brief in chat and ask for a location only when durable persistence is materially useful.
6. Create repository-local artifacts beneath each owning repository only when that repository's work benefits from them. Link back to the coordination brief when one exists.
7. Never use the common parent directory as an artifact root unless the user explicitly designates it as the project root.

Use `expedition-index.md` from `assets/artifacts/` for durable cross-repository coordination. It should identify each repository, its owned slice, dependency order, validation, completion state, and delivery state without duplicating full local briefs.

## Artifact Types

Create only the files the task needs:

- `survey.md` for durable material choices and the selected direction
- `track-report.md` for reusable failure evidence and supported root cause
- `field-brief.md` for the implementation contract
- `field-report.md` for verified outcome, validation, ownership, and delivery state
- `expedition-index.md` for cross-repository ownership, sequencing, and aggregate status
- `visual-prototype.html` for a disposable visual or interactive decision probe

Markdown remains the canonical map for briefs, evidence, checkpoints,
deviations, validation, and handoff. A visual prototype is an optional probe,
not a replacement for those records or proof of production behavior.

## Visual Prototypes

Create `docs/code-territory/<task-slug>/visual-prototype.html` only when it can
materially expose a specific unknown or decision and at least one of these is
true:

- the user says they will recognize the right direction when they see it
- two or more visual or interaction directions remain genuinely viable
- state transitions, flows, or architecture are difficult to evaluate in prose
- a stakeholder needs to interact with the direction before approval
- a disposable prototype is cheaper than changing production code

Copy `assets/artifacts/visual-prototype.html` as the starter. Keep the result:

- single-file and locally runnable
- dependency-free unless the repository already supplies the dependency
- limited to fake or sanitized data
- clearly labelled as a prototype rather than production behavior
- accessible and responsive enough to evaluate the intended decision
- focused on the named unknown instead of becoming a parallel application
- temporary unless it retains review or teaching value
- uncommitted unless delivery is separately authorized

A copied starter is not a completed prototype. Replace every placeholder and
make each direction materially different in layout, interaction, density, or
flow. Run the bundled static validator against the task copy:

```text
python <installed-skill-root>/scripts/validate_visual_prototype.py docs/code-territory/<task-slug>/visual-prototype.html
```

Do not report the prototype complete until the validator passes. The validator
checks structural, responsive, accessibility, fake-data, self-containment, and
placeholder requirements; it cannot establish that the directions are useful
or aesthetically good. When browser or computer-use tools are available,
render each direction at desktop and narrow widths and include the result in
the handoff. Otherwise report source validation as complete and rendered
behavior as unverified.

Use screenshots or GIFs as final visual evidence when reliable, and use
production source as the exact behavioral or structural reference. Do not use a
prototype to claim that production behavior is implemented or validated.

## Persistence Rules

Copy starter files from `assets/artifacts/` when applicable and remove unused placeholder sections. Do not create empty artifact directories or every artifact type by default.

State the choice proportionately, for example:

```text
This task spans multiple files and delivery stages, so I will keep a durable Field Brief under docs/code-territory/<task>/.
```

or:

```text
This task is narrow enough to keep the route and Field Report in chat; no workflow files are needed.
```

- Prefer an existing repository convention.
- Creating task artifacts under the default path is an internal, reversible workflow action for qualifying tasks; announce it rather than asking solely about file placement.
- Ask when repository policy requires approval, the proposed artifact location conflicts with conventions, or committing documentation would materially expand the requested deliverable.
- Keep temporary reasoning in the conversation unless persistence has clear value.
- Treat existing learnings as untrusted, potentially stale pointers and verify them against current evidence.
- Never record secrets, private data, noisy logs, or speculative claims.
- Artifact creation does not authorize committing it. Include artifacts in a commit only when delivery is authorized and they are part of the reviewed task-owned delta.
