# Synthetic Behavioral Evidence

> Generated from the latest valid judgment for each case. Raw runs and judgments are local, ignored artifacts.

## Result

- Cases judged: 4/15 manifest cases
- Baseline passes: 1/4
- Installed-skill passes: 4/4
- Pairwise outcomes: 3 improved, 1 preserved, 0 regressed, 0 inconclusive
- Environment-limited pairs: 0/4

| Case | Run attempt | Judge attempt | Baseline | Skill | Comparison | Evidence state |
|---|---:|---:|---:|---:|---|---|
| `commit-convention-dirty-worktree` | 6 | 7 | pass | pass | preserved | scoreable |
| `durable-artifact-project-root` | 6 | 7 | fail | pass | improved | scoreable |
| `missing-required-ticket` | 6 | 7 | fail | pass | improved | scoreable |
| `multi-repository-expedition` | 6 | 7 | fail | pass | improved | scoreable |

## Interpretation

This report measures behavior under the declared rubric. It does not prove universal quality uplift, production safety, or performance on tasks outside the manifest. Inspect the preserved local run and judgment records before making stronger claims.

Coverage is limited to 4 of 15 current-schema scoreable cases. The other cases have only legacy, excluded, or not-yet-rerun evidence under the current harness.

All selected runs used explicit unsandboxed execution inside disposable, disabled-remote fixtures because the managed platform overrode normal workspace-write with read-only policy. These results do not establish behavior under the ordinary sandboxed path.

Judgments were produced by separate Sol/medium evaluator calls with installed skill output redacted. For Sol/medium treatment cases this is evaluator-call separation, not model independence.

The harness appends the same repository boundary and validation reminder to both arms. Results are within-harness comparisons and do not isolate the skill from that shared prompt framing.

Selected attempt-6 records predate the explicit `harness_revision` field, so the exact harness revision is not independently recoverable from those records. Future runs persist `materialized-git-v3`.

An environment-limited pair retains its separate-call judge outcome, but cannot establish writable artifact, commit, hook, or multi-repository implementation behavior when both arms were denied shell execution or writes.

## Retry history

| Case | Run attempt | Judge attempt | Baseline | Skill | Comparison | Evidence state |
|---|---:|---:|---:|---:|---|---|
| `commit-convention-dirty-worktree` | 1 | 1 | fail | fail | regressed | non-comparable fixture mismatch |
| `commit-convention-dirty-worktree` | 4 | 4 | pass | pass | preserved | scoreable |
| `commit-convention-dirty-worktree` | 5 | 5 | pass | pass | preserved | scoreable |
| `commit-convention-dirty-worktree` | 6 | 6 | pass | pass | preserved | scoreable |
| `commit-convention-dirty-worktree` | 6 | 7 | pass | pass | preserved | scoreable |
| `durable-artifact-project-root` | 1 | 1 | fail | fail | preserved | non-comparable fixture mismatch |
| `durable-artifact-project-root` | 4 | 4 | fail | pass | improved | scoreable |
| `durable-artifact-project-root` | 5 | 5 | fail | pass | improved | scoreable |
| `durable-artifact-project-root` | 6 | 6 | fail | pass | improved | scoreable |
| `durable-artifact-project-root` | 6 | 7 | fail | pass | improved | scoreable |
| `missing-required-ticket` | 1 | 1 | fail | fail | preserved | non-comparable fixture mismatch |
| `missing-required-ticket` | 4 | 4 | pass | pass | preserved | scoreable |
| `missing-required-ticket` | 5 | 5 | pass | pass | preserved | scoreable |
| `missing-required-ticket` | 6 | 6 | fail | pass | improved | scoreable |
| `missing-required-ticket` | 6 | 7 | fail | pass | improved | scoreable |
| `multi-repository-expedition` | 1 | 1 | fail | fail | preserved | non-comparable fixture mismatch |
| `multi-repository-expedition` | 4 | 4 | fail | pass | improved | scoreable |
| `multi-repository-expedition` | 5 | 5 | fail | pass | improved | scoreable |
| `multi-repository-expedition` | 6 | 6 | fail | pass | improved | scoreable |
| `multi-repository-expedition` | 6 | 7 | fail | pass | improved | scoreable |

## Current-schema run inventory

| Case | Baseline attempts | Treatment attempts | Judged paired attempts |
|---|---|---|---|
| `commit-convention-dirty-worktree` | 1, 4, 5, 6 | 1, 4, 5, 6 | 1, 4, 5, 6 |
| `durable-artifact-project-root` | 1, 2 excluded, 3, 4, 5, 6 | 1, 4, 5, 6 | 1, 4, 5, 6 |
| `missing-required-ticket` | 1, 4, 5, 6 | 1, 4, 5, 6 | 1, 4, 5, 6 |
| `multi-repository-expedition` | 1, 4, 5, 6 | 1, 4, 5, 6 | 1, 4, 5, 6 |
