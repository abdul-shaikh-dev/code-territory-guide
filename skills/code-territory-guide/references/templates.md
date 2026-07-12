# Code Territory Guide Templates

Use these templates only when a copyable handoff or structured output adds value. Load `safety-and-scope.md` and the relevant workflow reference first. Do not use templates as a substitute for repository inspection.

For durable repository artifacts, copy the corresponding starter from `assets/artifacts/`. The prompt templates below remain useful for chat and model handoffs.

## Contents

- Mode Selection
- Survey
- Track
- Prove
- Field Brief
- Implementation Handoff
- Fresh Review
- Delivery Handoff
- Field Report

## Mode Selection

```text
Choose the lightest Code Territory Guide mode for this task.

Task:
<task>

Return:
1. Survey, Track, Prove, or Expedition
2. The main uncertainty this mode reduces
3. The repository evidence to inspect first
4. Whether a material user decision is required under the canonical policy
```

## Survey

```text
Use Survey for this task. Inspect relevant repository context first. Restate the outcome, identify only material choices, recommend the smallest valuable direction, and apply the canonical plan-approval rules. Do not implement.

Task:
<task>

Return: intent, territory inspected, material choices, recommendation, and readiness for Expedition.
```

## Track

```text
Use Track for this failure. Reproduce or characterize it, inspect complete evidence, test one falsifiable hypothesis at a time, classify related failures, and identify a supported root cause before recommending a fix. Do not present speculation as confirmation.

Failure:
<task, error, logs, or observed behavior>

Return: observed versus expected, evidence, hypotheses tested, root cause status, and minimal fix direction.
```

## Prove

```text
Use Prove only if this behavior is clear, narrow, and testable. Define one behavioral test, verify the expected failure, implement the smallest passing change, run surrounding checks, and preserve green behavior during refactoring.

Task:
<task>

Return: target behavior, test and expected failure, implementation scope, validation, and owned delta.
```

## Field Brief

```text
Create a field brief from the inspected repository and approved internal route.

Task:
<task>

Include:
- objective and acceptance criteria
- task-owned files or hunks
- existing patterns and behavior to preserve
- implementation tasks
- tests and validation commands
- constraints and non-goals
- relevant compatibility, migration, security, observability, accessibility, or rollback needs
- applicable scope-expansion boundaries from the canonical policy

Do not write implementation code.
```

## Implementation Handoff

```text
Implement this field brief within the supplied canonical safety-and-scope policy.

Field brief:
<brief>

Worktree baseline and user-owned changes:
<baseline>

Rules:
- own only the listed files or hunks
- preserve pre-existing changes
- use the smallest safe diff and existing patterns
- stop when the canonical scope gate requires confirmation
- run listed validation and classify failures
- do not report Complete while required task-caused checks fail

Return: owned files, summary, validation, deviations, failure classifications, and completion state.
```

## Fresh Review

```text
Review only the task-owned delta against the original request, field brief, canonical policy, and validation evidence.

Original request:
<task>

Field brief:
<brief>

Worktree baseline:
<baseline>

Validation:
<results>

Return:
- pass or fail
- must-fix and should-fix findings
- unrequested behavior or ownership violations
- missing or weak validation
- relevant compatibility, security, data, observability, accessibility, and rollback gaps
- accurate completion state
```

## Delivery Handoff

```text
Deliver the reviewed task-owned delta only to the explicitly authorized level.

Authorized operation:
<none, branch, commit, push, pull request, tag, or release>

Owned delta:
<files or hunks>

Validation and completion state:
<results>

Rules:
- recheck branch, status, staged state, and exact owned diff
- preserve unrelated and pre-existing staged changes
- stage explicit owned paths or hunks
- resolve the commit convention from trusted instructions, configuration, and a narrow history sample
- never invent a ticket, Jira, issue, component, or team prefix
- do not bypass commit hooks or amend existing history without authorization
- do not commit secrets, generated local artifacts, or raw evidence
- do not infer authorization for the next delivery operation
- verify and report the resulting commit hash, branch, remote action, or link
```

## Field Report

```text
Create a proportional Field Report for this task.

Include:
- Complete, Incomplete, or Blocked
- what changed and why
- task-owned files
- validation run, failures classified, and checks not run
- material risks, assumptions, gaps, or pending decisions
- rollback guidance when relevant
- what the user should review
- delivery state and commit hash or link, when applicable
- durable learning saved, if any

Add visual evidence only for material visual behavior. Add quiz questions only when teaching or knowledge transfer was requested.
```
