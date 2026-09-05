# Real-Repository Behavioral Evidence

## Verdict

Code Territory Guide was exercised against isolated local clones of Copilot Credit Simulator and CogStash. The read-only matched comparisons preserved the defined safety rubric, while separate writable runs produced two focused, owner-local implementations that passed independent controlled-coding review.

This supports use on narrow repository work. It does not establish universal quality uplift, broad-refactor performance, or production-system safety.

The recorded runs are historical evidence for the frozen treatment hash in
`real-repo-manifest.json`. The skill has evolved since those runs; the current
`v0.2.1` artifact, delivery, multi-repository, commit-convention, resume,
validation-depth, and visual-prototype behavior has not yet received fresh
model-backed real-repository evaluation.

## Read-only comparisons

- Both final baseline and installed-skill arms passed the case rubrics.
- Repository HEAD, branch, status, remote configuration, and treatment hashes were preserved in the selected records.
- Push URLs were disabled.
- No quality uplift was detected under the binary rubric; the outcome was preservation.
- The development sequence was adaptive, so command-count and runtime differences are observations rather than causal effects.

## Writable implementations

### Copilot Credit Simulator

- Allowed monthly capacity to be zero below one scenario cost.
- Owned files: `src/lib/capacityModel.js` and its focused test.
- Targeted tests: 2/2 passed; full tests: 5/5 passed; diff check passed.
- Build remained environmentally unverified because dependencies and Vite were absent; no install was attempted.
- Independent review: approve.

### CogStash

- Made non-string JSON values for `theme` and `window_size` fall back safely.
- Owned files: `src/cogstash/core/config.py` and its focused tests.
- Focused tests: 45 passed; Ruff, Mypy, and diff check passed.
- Full suite: 342 passed and 3 unrelated UI/settings failures were disclosed.
- Independent review: approve.

## Boundaries

The clones remained on local evaluation branches with push URLs disabled. No commits, pushes, or remote source changes were made. Broader refactors, migrations, security-sensitive changes, database work, and deployment behavior still need dedicated cases.
