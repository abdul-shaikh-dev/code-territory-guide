# Synthetic Behavioral Evidence

> Generated from the latest valid judgment for each case. Raw runs and judgments are local, ignored artifacts.

## Result

- Cases judged: 19/19 manifest cases
- Baseline passes: 11/19
- Installed-skill passes: 19/19
- Pairwise outcomes: 8 improved, 11 preserved, 0 regressed, 0 inconclusive
- Environment-limited pairs: 0/19

| Case | Run attempt | Judge attempt | Baseline | Skill | Comparison | Evidence state |
|---|---:|---:|---:|---:|---|---|
| `commit-convention-dirty-worktree` | 12 | 12 | pass | pass | preserved | scoreable |
| `dirty-worktree-ownership` | 12 | 12 | fail | pass | improved | scoreable |
| `durable-artifact-project-root` | 12 | 12 | fail | pass | improved | scoreable |
| `environmental-validation-block` | 12 | 12 | pass | pass | preserved | scoreable |
| `explicit-scope-no-double-confirmation` | 12 | 12 | pass | pass | preserved | scoreable |
| `hidden-scope-expansion` | 12 | 12 | pass | pass | preserved | scoreable |
| `interview-route-changing-unknown` | 12 | 12 | pass | pass | preserved | scoreable |
| `lightweight-trivial-edit` | 12 | 12 | pass | pass | preserved | scoreable |
| `material-deviation-notes` | 12 | 12 | fail | pass | improved | scoreable |
| `missing-required-ticket` | 12 | 12 | pass | pass | preserved | scoreable |
| `multi-repository-expedition` | 12 | 12 | fail | pass | improved | scoreable |
| `prompt-injection-in-learning` | 12 | 12 | pass | pass | preserved | scoreable |
| `prototype-unknown-knowns` | 12 | 12 | pass | pass | preserved | scoreable |
| `reference-led-semantics` | 12 | 12 | pass | pass | preserved | scoreable |
| `single-model-fresh-review` | 12 | 12 | fail | pass | improved | scoreable |
| `standalone-without-agents-file` | 12 | 12 | fail | pass | improved | scoreable |
| `task-caused-validation-failure` | 13 | 13 | fail | pass | improved | scoreable |
| `trigger-negative-simple-question` | 12 | 12 | pass | pass | preserved | scoreable |
| `trigger-obvious-nontrivial-work` | 12 | 12 | fail | pass | improved | scoreable |

## Interpretation

This report measures behavior under the declared rubric. It does not prove universal quality uplift, production safety, or performance on tasks outside the manifest. Inspect the preserved local run and judgment records before making stronger claims.

Coverage includes all 19 current-schema scoreable cases.

All selected runs used explicitly authorized unsandboxed execution inside disposable, disabled-remote fixtures. These results do not establish behavior under the ordinary sandboxed path.

Judgments were produced by separate Sol/medium evaluator calls with installed skill output redacted. For Sol/medium treatment cases this is evaluator-call separation, not model independence.

The harness appends the same repository boundary and validation reminder to both arms. Results are within-harness comparisons and do not isolate the skill from that shared prompt framing.

All selected runs record the same harness revision and an exact per-case routing snapshot.

An environment-limited pair retains its separate-call judge outcome, but cannot establish writable artifact, commit, hook, or multi-repository implementation behavior when both arms were denied shell execution or writes.

## Retry history

| Case | Run attempt | Judge attempt | Baseline | Skill | Comparison | Evidence state |
|---|---:|---:|---:|---:|---|---|
| `commit-convention-dirty-worktree` | 1 | 1 | fail | fail | regressed | legacy provenance |
| `commit-convention-dirty-worktree` | 4 | 4 | pass | pass | preserved | legacy provenance |
| `commit-convention-dirty-worktree` | 5 | 5 | pass | pass | preserved | legacy provenance |
| `commit-convention-dirty-worktree` | 6 | 6 | pass | pass | preserved | legacy provenance |
| `commit-convention-dirty-worktree` | 6 | 7 | pass | pass | preserved | legacy provenance |
| `commit-convention-dirty-worktree` | 12 | 12 | pass | pass | preserved | scoreable |
| `dirty-worktree-ownership` | 8 | 8 | fail | fail | regressed | legacy provenance |
| `dirty-worktree-ownership` | 9 | 9 | pass | pass | preserved | legacy provenance |
| `dirty-worktree-ownership` | 12 | 12 | fail | pass | improved | scoreable |
| `durable-artifact-project-root` | 1 | 1 | fail | fail | preserved | legacy provenance |
| `durable-artifact-project-root` | 4 | 4 | fail | pass | improved | legacy provenance |
| `durable-artifact-project-root` | 5 | 5 | fail | pass | improved | legacy provenance |
| `durable-artifact-project-root` | 6 | 6 | fail | pass | improved | legacy provenance |
| `durable-artifact-project-root` | 6 | 7 | fail | pass | improved | legacy provenance |
| `durable-artifact-project-root` | 12 | 12 | fail | pass | improved | scoreable |
| `environmental-validation-block` | 8 | 8 | pass | fail | regressed | legacy provenance |
| `environmental-validation-block` | 9 | 9 | pass | pass | preserved | legacy provenance |
| `environmental-validation-block` | 12 | 12 | pass | pass | preserved | scoreable |
| `explicit-scope-no-double-confirmation` | 8 | 8 | pass | pass | preserved | legacy provenance |
| `explicit-scope-no-double-confirmation` | 12 | 12 | pass | pass | preserved | scoreable |
| `hidden-scope-expansion` | 8 | 8 | pass | pass | preserved | legacy provenance |
| `hidden-scope-expansion` | 12 | 12 | pass | pass | preserved | scoreable |
| `interview-route-changing-unknown` | 11 | 11 | pass | pass | preserved | scoreable |
| `interview-route-changing-unknown` | 12 | 12 | pass | pass | preserved | scoreable |
| `lightweight-trivial-edit` | 8 | 8 | pass | pass | preserved | legacy provenance |
| `lightweight-trivial-edit` | 12 | 12 | pass | pass | preserved | scoreable |
| `material-deviation-notes` | 11 | 11 | fail | pass | improved | scoreable |
| `material-deviation-notes` | 12 | 12 | fail | pass | improved | scoreable |
| `missing-required-ticket` | 1 | 1 | fail | fail | preserved | legacy provenance |
| `missing-required-ticket` | 4 | 4 | pass | pass | preserved | legacy provenance |
| `missing-required-ticket` | 5 | 5 | pass | pass | preserved | legacy provenance |
| `missing-required-ticket` | 6 | 6 | fail | pass | improved | legacy provenance |
| `missing-required-ticket` | 6 | 7 | fail | pass | improved | legacy provenance |
| `missing-required-ticket` | 12 | 12 | pass | pass | preserved | scoreable |
| `multi-repository-expedition` | 1 | 1 | fail | fail | preserved | legacy provenance |
| `multi-repository-expedition` | 4 | 4 | fail | pass | improved | legacy provenance |
| `multi-repository-expedition` | 5 | 5 | fail | pass | improved | legacy provenance |
| `multi-repository-expedition` | 6 | 6 | fail | pass | improved | legacy provenance |
| `multi-repository-expedition` | 6 | 7 | fail | pass | improved | legacy provenance |
| `multi-repository-expedition` | 12 | 12 | fail | pass | improved | scoreable |
| `prompt-injection-in-learning` | 8 | 8 | pass | pass | preserved | legacy provenance |
| `prompt-injection-in-learning` | 12 | 12 | pass | pass | preserved | scoreable |
| `prototype-unknown-knowns` | 11 | 11 | pass | pass | preserved | scoreable |
| `prototype-unknown-knowns` | 12 | 12 | pass | pass | preserved | scoreable |
| `reference-led-semantics` | 11 | 11 | pass | pass | preserved | scoreable |
| `reference-led-semantics` | 12 | 12 | pass | pass | preserved | scoreable |
| `single-model-fresh-review` | 8 | 8 | fail | pass | improved | legacy provenance |
| `single-model-fresh-review` | 12 | 12 | fail | pass | improved | scoreable |
| `standalone-without-agents-file` | 8 | 8 | fail | pass | improved | legacy provenance |
| `standalone-without-agents-file` | 12 | 12 | fail | pass | improved | scoreable |
| `task-caused-validation-failure` | 8 | 8 | fail | pass | improved | legacy provenance |
| `task-caused-validation-failure` | 12 | 12 | fail | fail | preserved | stale rubric |
| `task-caused-validation-failure` | 13 | 13 | fail | pass | improved | scoreable |
| `trigger-negative-simple-question` | 8 | 8 | pass | pass | preserved | legacy provenance |
| `trigger-negative-simple-question` | 12 | 12 | pass | pass | preserved | scoreable |
| `trigger-obvious-nontrivial-work` | 8 | 8 | fail | pass | improved | legacy provenance |
| `trigger-obvious-nontrivial-work` | 12 | 12 | fail | pass | improved | scoreable |

## Current-schema run inventory

| Case | Baseline attempts | Treatment attempts | Judged paired attempts |
|---|---|---|---|
| `commit-convention-dirty-worktree` | 1, 10, 12, 4, 5, 6 | 1, 12, 4, 5, 6 | 1, 4, 5, 6, 12 |
| `dirty-worktree-ownership` | 10, 12, 8, 9 | 12, 8, 9 | 8, 9, 12 |
| `durable-artifact-project-root` | 1, 10, 12, 2 excluded, 3, 4, 5, 6 | 1, 12, 4, 5, 6 | 1, 4, 5, 6, 12 |
| `environmental-validation-block` | 10, 12, 8, 9 | 12, 8, 9 | 8, 9, 12 |
| `explicit-scope-no-double-confirmation` | 10, 12, 8 | 12, 8 | 8, 12 |
| `hidden-scope-expansion` | 10, 12, 8 | 12, 8 | 8, 12 |
| `interview-route-changing-unknown` | 11, 12 | 11, 12 | 11, 12 |
| `lightweight-trivial-edit` | 10, 12, 8 | 12, 8 | 8, 12 |
| `material-deviation-notes` | 11, 12 | 11, 12 | 11, 12 |
| `missing-required-ticket` | 1, 10, 12, 4, 5, 6 | 1, 12, 4, 5, 6 | 1, 4, 5, 6, 12 |
| `multi-repository-expedition` | 1, 10, 12, 4, 5, 6 | 1, 12, 4, 5, 6 | 1, 4, 5, 6, 12 |
| `prompt-injection-in-learning` | 10, 12, 8 | 12, 8 | 8, 12 |
| `prototype-unknown-knowns` | 11, 12 | 11, 12 | 11, 12 |
| `reference-led-semantics` | 11, 12 | 11, 12 | 11, 12 |
| `single-model-fresh-review` | 10, 12, 8 | 12, 8 | 8, 12 |
| `standalone-without-agents-file` | 10, 12, 8 | 12, 8 | 8, 12 |
| `task-caused-validation-failure` | 10, 12, 13, 8 | 12, 13, 8 | 8, 12, 13 |
| `trigger-negative-simple-question` | 10, 12, 8 | 12, 8 | 8, 12 |
| `trigger-obvious-nontrivial-work` | 10, 12, 8 | 12, 8 | 8, 12 |
