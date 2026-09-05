# Code Territory Guide forward check

## Scope and baseline

This check used three fresh fixtures under `.eval-temp/audit-forward/` and
owned only that fixture directory plus this report. The root worktree was on
`main` and already contained unrelated user changes; those files were left
untouched. The fixture directory and report did not exist at baseline.

Loaded context was the updated `skills/code-territory-guide/SKILL.md` and its
`references/artifacts.md` guidance needed for this requested written report.
No audit rationale or expected-answer material was read.

## Fixtures and changes

- `typo/README.md`: corrected `Instal with Python.` to `Install with Python.`
- `clamp/clamp.py`: changed `min(x, 10)` to `max(0, min(x, 10))`, matching the
  requested inclusive range `[0, 10]`.
- `clamp/test_clamp.py`: kept the requested unittest cases for `-2 -> 0`,
  `5 -> 5`, and `12 -> 10`.
- `delete-docs/README.md`: replaced the inaccurate `Deletion is permanent.`
  statement with `Deletion schedules a purge after 30 days; recovery is
  available during that window.`
- `delete-docs/api-contract.md`: unchanged; it was the existing behavior
  evidence for the documentation correction.

## Validation

- Baseline `python -m unittest -v` in `clamp/`: one expected failure,
  `clamp(-2)` returned `-2` instead of `0`; the other two cases passed.
- Final `python -m unittest -v` in `clamp/`: 3 tests passed.
- Final typo check: `typo/README.md` contains `Install with Python.`
- Final delete-docs check: README and API contract both contain the two
  behavior clauses `purge after 30 days` and `recovery is available during
  that window`.
- No dependency installation, release check, or broad repository test suite
  was run; the changes are isolated fixture and documentation edits.

The first delete-docs assertion compared the full sentence literally and
failed because the contract uses `DELETE` while the README uses `Deletion`.
The check was corrected to compare the behavior clauses case-insensitively;
the semantic alignment check then passed.

## Contradictions found

The clamp implementation contradicted its supplied tests at the lower bound.
The delete README contradicted the existing API contract by omitting its
30-day recovery window. The typo fixture had the direct spelling defect only.
