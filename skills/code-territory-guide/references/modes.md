# Code Territory Guide Modes

Read `safety-and-scope.md` before using a mode. Choose the lightest mode that reduces the main uncertainty; do not run every mode.

## Survey

Use Survey when the request is vague, product-oriented, architectural, or has multiple materially different solutions.

Goal: improve the map before implementation.

1. Inspect relevant repository context before asking design questions.
2. Restate the intended outcome and constraints.
3. Identify the decisions that materially affect behavior, architecture, data, security, compatibility, or scope.
4. Present two or three viable approaches only when genuine alternatives exist.
5. Recommend one direction with its principal tradeoff.
6. Apply the plan-approval rules in `safety-and-scope.md`.
7. Continue into Expedition when the target is clear.

Do not implement during Survey.

Return:

```md
## Survey Result

### Intent
<target outcome>

### Territory inspected
- <relevant evidence>

### Material choices
- <choice and tradeoff, if any>

### Recommendation
<smallest valuable direction>

### Ready for Expedition
<yes, or the decision still required>
```

## Track

Use Track for broken, failing, flaky, slow, regressed, or inconsistent behavior, including task-caused validation failures.

Do not enter Track merely because the request uses words such as bug or fix. When the owning expression, expected behavior, and nearest test boundary are already clear, use Prove or Expedition directly.

Goal: support a root cause with evidence before selecting a fix.

1. Capture observed and expected behavior.
2. Reproduce or characterize the failure.
3. Read relevant errors, assertions, logs, and recent changes completely.
4. Trace bad values or state backward across the owning boundary.
5. Form one falsifiable hypothesis at a time.
6. Run the smallest check that can confirm or reject it.
7. Classify related failing checks as task-caused, pre-existing, or environmental.
8. Identify the confirmed or strongest-supported root cause.
9. Continue into Expedition with the minimal fix direction.

Do not present a speculative fix as a confirmed root cause.

Return:

```md
## Track Result

### Observed and expected
<concise comparison>

### Evidence
- <files, logs, tests, commands>

### Hypotheses tested
- <hypothesis and result>

### Root cause
<confirmed, strongest-supported, or unresolved>

### Fix direction
<minimal route>
```

## Prove

Use Prove only when behavior is clear, narrow, and testable before implementation. Good fits include validators, parsers, calculations, business rules, API regressions, pure functions, and focused service behavior.

Avoid Prove for exploratory UI, vague behavior, prototypes, brittle test infrastructure, or broad refactors.

1. Define one target behavior.
2. Add or propose one minimal failing test.
3. Verify it fails for the expected behavioral reason.
4. Correct setup failures until the test proves the intended gap.
5. Implement the smallest passing change.
6. Run the targeted test and relevant surrounding checks.
7. Refactor only while green and without adding behavior.
8. Continue into Expedition at owned-diff review, completion-state classification, learning, and Field Report.

If the test passes before implementation, explain why it does not prove the requested change and revise it or leave Prove mode.
