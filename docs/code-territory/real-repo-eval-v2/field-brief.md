# Field Brief: Writable real-repository evaluation v2

## Decisions most likely to change

- Preserve the historical read-only evaluation and add a separate writable evidence path.
- Require ordinary workspace-write; do not add or recommend danger-full-access.
- Use one disposable local clone per case, arm, and attempt, with a required local commit as observable completion evidence.

## Objective

Produce a deterministic harness that can later establish writable behavior on CogStash, CogVest, and Copilot Credit Simulator while preventing remote delivery and preserving matched baseline/treatment conditions.

## Territory

- Owning files: new writable manifest, runner, schema, judge, report builder, validator, tests, evals/README.md, and evaluation lock
- Historical files and evidence remain readable but unchanged
- Worktree baseline: clean eval/attempt-20-release-evidence

## Route

1. Freeze repository tasks, base commits, routing, rubrics, and validation.
2. Materialize matched disposable local clones and isolated model homes.
3. Record commits, diffs, commands, validation evidence, exclusions, and lock provenance.
4. Blind and sanitize judging, generate a qualified report, and validate all relationships.
5. Add external-terminal canary and resume instructions.

## Preserve

- Existing synthetic and historical read-only evidence.
- Original and seed repository worktrees.
- Disabled remote delivery and no dependency installation.

## Non-goals and scope gates

- Do not execute model sessions while building the harness.
- Do not push, merge, release, or modify the three seed repositories.
- Do not claim OS-enforced network isolation.

## Validation

- python -m unittest discover -s evals/tests -v
- python -m compileall -q evals
- git diff --check

## Delivery authorization

Implementation and validation only; leave the task-owned delta uncommitted until explicitly requested.

- Commit convention: concise imperative fallback
- Ticket or issue identifier: not required
