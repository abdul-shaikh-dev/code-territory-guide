# Field Report: Writable real-repository evaluation v2

## Outcome

The preregistered harness is implemented for three bounded implementation tasks. It materializes matched disposable clones, disables fetch and push URLs, runs baseline and installed-skill arms independently under ordinary workspace-write, and records diffs, commits, commands, validation, timing, treatment hashes, dependency hashes, lock provenance, and exclusions.

## What changed

- Added a three-repository writable manifest with pinned commits, fixed model routing, task rubrics, validation commands, and commit conventions.
- Added a fail-closed runner with isolated homes, per-arm clones, resume support, read-only downgrade detection, remote checks, and required local-commit evidence.
- Added sanitized blinded judging, qualified report generation, structural validation, adversarial audit support, and deterministic unit tests.
- Added a normal-PowerShell runbook that does not use danger-full-access.

## Validation

- Python compilation: passed.
- Deterministic unit suite: passed before the final lock refresh.
- Manifest, historical-record, real-repository, writable-harness, and diff checks are rerun after the final lock refresh.

## Remaining unknowns

- Actual writable model behavior is intentionally untested in the managed session.
- Network prohibition is evidence-enforced, not independently OS-enforced.
- The cohort establishes behavior only for its frozen tasks, repositories, models, and attempts.

## Next gate

Merge the harness, prepare local dependency copies, run the paired simulator canary from a normal PowerShell terminal, inspect actual file and commit evidence, then resume the remaining cohort and judging.
