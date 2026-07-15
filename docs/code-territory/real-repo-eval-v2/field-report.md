# Field Report: Writable real-repository evaluation v2

## Outcome

The preregistered harness is implemented for three bounded implementation tasks. It materializes matched disposable clones, disables fetch and push URLs, runs baseline and installed-skill arms independently under ordinary workspace-write, and records diffs, commits, commands, validation, timing, treatment hashes, dependency hashes, lock provenance, and exclusions.

## What changed

- Added a three-repository writable manifest with pinned commits, fixed model routing, task rubrics, validation commands, and commit conventions.
- Added a fail-closed runner with isolated homes, per-arm clones, resume support, read-only downgrade detection, remote checks, and required local-commit evidence.
- Registered the native elevated Windows sandbox explicitly so isolated homes do not lose the backend required for workspace-write.
- Added sanitized blinded judging, qualified report generation, structural validation, adversarial audit support, and deterministic unit tests.
- Added a normal-PowerShell runbook that does not use danger-full-access.

## Validation

- Python compilation: passed.
- Deterministic unit suite: passed before the final lock refresh.
- Zero-model native Windows sandbox preflight: elevated workspace profile created a disposable file successfully.
- Manifest, historical-record, real-repository, writable-harness, and diff checks are rerun after the final lock refresh.

## Remaining unknowns

- Attempts 22 and 23 correctly excluded read-only baselines before treatment; they exposed the missing explicit Windows sandbox backend and are not writable evidence.
- Network prohibition is evidence-enforced, not independently OS-enforced.
- The cohort establishes behavior only for its frozen tasks, repositories, models, and attempts.

## Next gate

Merge the harness, prepare local dependency copies, run the paired simulator canary from a normal PowerShell terminal, inspect actual file and commit evidence, then resume the remaining cohort and judging.
