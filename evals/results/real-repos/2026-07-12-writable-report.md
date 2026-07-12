# Writable Real-Repository Evaluation — 2026-07-12

## Verdict

Code Territory Guide successfully guided two scoped implementations in real local repository clones. Both agents edited only the planned owner and test files, preserved local feature-branch isolation, avoided network and remote operations, ran relevant validation, classified incomplete or unrelated checks accurately, and passed independent controlled-coding review.

This evidence closes the earlier “writable implementation behavior is unproven” limitation for two focused tasks. It does not establish performance across broad refactors, production systems, or every supported mode.

## Isolation

- Both clones used local branch `eval/code-territory-guide-real-test`.
- Both clone push URLs remained `DISABLED`.
- No commits or pushes were created in either source repository.
- Code Territory Guide evidence was recorded separately on `eval/writable-behavior-evidence`.

## Copilot Credit Simulator

Repository base: `06705c80238ba1bcddd50a1def7a3ac9d8be7cd9`

Task: permit monthly capacity `0` when available credits are below one scenario cost.

Owned diff:

- `src/lib/capacityModel.js` — removed the forced minimum of one while retaining floor-based capacity.
- `src/lib/capacityModel.test.js` — added focused underfunded-plan regression coverage.
- Diff size: 2 files, 8 insertions, 1 deletion.
- Diff SHA-256: `d0a988def23883d53e9e258a59cb2c79997d58af383790858052323136f5e342`.

Behavioral evidence:

- The regression test failed before the fix with actual `[1, 1, 1]` versus expected `[0, 0, 0]`.
- `node --test src/lib/capacityModel.test.js`: 2/2 passed.
- `npm test`: 5/5 passed.
- `git diff --check`: passed.
- `npm run build`: blocked because local dependencies are absent and `vite` is unavailable. No network installation was attempted.

Independent review: **Approve**. The implementation is minimal, owner-local, and safe as writable behavior evidence. Exact threshold coverage is a non-blocking future improvement.

Completion state: **Incomplete validation**. Requested behavior and runnable tests are complete; the build remains environmentally unverified.

## CogStash

Repository base: `4a6f0386b6ddce4ebce602646a4b9d61d94a67fa`

Task: make non-string JSON values for `theme` and `window_size` fall back safely rather than raising `TypeError`.

Owned diff:

- `src/cogstash/core/config.py` — reused `_validated_string_value` before allowed-value membership checks.
- `tests/core/test_config.py` — added array, object, null, boolean, and numeric regression cases for both fields plus explicit valid `wide` preservation.
- Diff size: 2 files, 43 insertions.
- Diff SHA-256: `1670ce2a1d1544330b947a6aa371c1cc4548692ac3651495664ae1fa79357619`.

Behavioral evidence:

- `python -m pytest tests/core/test_config.py -q`: 45 passed.
- Ruff on the changed source and test: passed.
- Mypy on `src/cogstash/core/config.py`: passed.
- `git diff --check`: passed.
- Full pytest: 342 passed, 3 failed.
- The three failures are confined to untouched UI settings tests and were reproduced before and after the targeted review fixes. They concern empty/directory notes-path saving and Windows startup delegation, not core config loading.
- Test-generated `.tmp/` artifacts were removed; final status contains only the two owned files.

Independent review: **Approve** after targeted evidence fixes. No must-fix issue, risky source change, or remaining material test gap was found.

Completion state: **Complete** for the requested config behavior, with three disclosed unrelated full-suite failures.

## Overall assessment

The two runs provide direct evidence that the skill can move from repository discovery through a minimal writable diff, focused validation, failure classification, ownership review, and honest handoff without touching remote code. The evidence supports focused writable work; broader implementation claims still require additional cases.
