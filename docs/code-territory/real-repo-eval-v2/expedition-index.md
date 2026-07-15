# Expedition Index: Writable real-repository evaluation v2

## Outcome

Create a preregistered, reproducible evaluation that compares baseline and Code Territory Guide behavior on three bounded implementation tasks without modifying source worktrees or remotes.

## Coordination

- Coordination repository: code-territory-guide
- Artifact location: docs/code-territory/real-repo-eval-v2/
- Dependency order: harness and manifest, deterministic validation, merge, external-terminal canary, paired runs, blinded judging, report and audit

## Repository slices

| Repository | Owned behavior | Commit convention | Validation | Completion | Delivery |
|---|---|---|---|---|---|
| code-territory-guide | Writable runner, manifest, judge, report, validation, instructions | Concise imperative fallback | Deterministic harness tests | Harness complete | Uncommitted |
| CogStash | Case-insensitive parsed and filtered note tags | fix: | Focused pytest and Ruff | Seed frozen | Local disposable commits only |
| CogVest | Non-finite percentage fallback | Concise fix: | Focused Jest and TypeScript | Seed frozen | Local disposable commits only |
| copilot-credit-simulator | Zero monthly capacity below scenario cost | fix: | Node test suite | Seed frozen | Local disposable commits only |

## Cross-repository contracts

- Each arm starts from the exact manifest commit in a separate disposable local clone.
- Fetch and push URLs are DISABLED before a model session starts.
- Model sessions use ordinary workspace-write through the registered native elevated Windows sandbox, approval policy never, isolated homes, and no network commands.
- A run is excluded on seed mismatch, treatment mutation, boundary escape evidence, remote mutation, read-only downgrade, timeout, missing response, missing task delta, or missing required local commit.
- Raw evidence remains ignored; only qualified summaries are tracked.

## Integration and rollout

1. Merge the deterministic harness without running model sessions in the managed environment.
2. From a normal terminal, run one paired canary and confirm actual file and commit evidence.
3. Resume the remaining cases at the same attempt, then run blinded judges, report generation, validation, and audit.

## Aggregate validation

- python -m unittest discover -s evals/tests -v — deterministic harness behavior
- python evals/validate_manifest.py — synthetic manifest remains valid
- python evals/validate_records.py — historical and schema-3 synthetic evidence remains valid
- python evals/validate_real_repo_writable_eval.py — v2 manifest, run, judgment, and report integrity

## Risks and recovery

- A managed host or missing native Windows backend may silently downgrade nested sessions to read-only; the runner explicitly requests the elevated backend and the exclusion rules stop the cohort.
- Network prohibition is prompt- and evidence-enforced because Codex itself requires API access; observed network tool use excludes a run.
- Disposable workspaces can be deleted after evidence is recorded; seed clones and original repositories remain unchanged.

## Aggregate status

Harness implementation is complete and deterministically validated. Merge and external-terminal execution remain pending; no writable behavioral claim exists until that cohort succeeds.
