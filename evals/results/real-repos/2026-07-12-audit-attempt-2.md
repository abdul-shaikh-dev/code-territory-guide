# Verdict: QUALIFIED

The selected final comparison is internally consistent and supports a narrow preservation/safety result, but the evaluation is not a clean independent quality-uplift test.

## Verified counts

| Measure | Result |
|---|---:|
| Cases | 2 |
| Run artifacts | 9 |
| Excluded runs | 0 |
| Report-selected runs | 4 |
| Final judgments | 2 |
| Positive criteria | 20/20 passed |
| Forbidden checks | 0/14 occurred |
| Overall arm passes | 4/4 |
| Outcomes | 2 preserved, 0 improved, 0 regressed |

The two named judgments are rubric-complete and internally consistent: IDs, descriptions, ordering, run IDs, prompt hashes, and pass-field calculations all validate. No expected criterion IDs/descriptions or forbidden strings were found in the runner prompts or recorded responses. The rubric itself is defined in the [manifest](G:/Projects/2026/cool_projects/code-territory-guide/evals/real-repo-manifest.json:16) and enforced by the [judge validator](G:/Projects/2026/cool_projects/code-territory-guide/evals/judge_real_repo_eval.py:63).

## Findings

1. **High — adaptive treatment selection creates selection bias.**

   The report selects only baseline attempt 1/2 and treatment attempt 3 via hard-coded mappings in [build_real_repo_report.py](G:/Projects/2026/cool_projects/code-territory-guide/evals/build_real_repo_report.py:24), despite 9 non-excluded run artifacts. Installed-skill hashes changed on every retry:

   `11fee5…` → `806bfd…` → `18625f…`.

   Therefore, the final treatment is a changing intervention, not a single preregistered treatment. The report’s claim that attempt 3 “retained the same judged behavior” is not verifiable from the permitted judgment files because earlier attempts have no included judgments.

2. **Medium — safety evidence is strong but not complete repository isolation.**

   All 9 runs report unchanged HEAD, branch, status, remote URLs, `DISABLED` push URLs, and treatment hashes; no file-change events or network-like commands were observed. However, the runner compares only Git metadata/status plus the treatment tree hash ([run script](G:/Projects/2026/cool_projects/code-territory-guide/evals/run_real_repo_eval.py:96)); ignored-file changes, transient changes restored before measurement, and actual network access are not fully ruled out. “No-network” is enforced primarily through prompt text.

3. **Medium — the report builder does not audit its inputs.**

   It does not verify selected runs are non-excluded, state-clean, hash-stable, correctly routed, or judgment-consistent before emitting headlines. It also labels the four selected records “all four valid runs,” although all 9 run artifacts are marked non-excluded. See [report generation](G:/Projects/2026/cool_projects/code-territory-guide/evals/build_real_repo_report.py:42).

4. **Low — quality conclusions exceed the measurement design.**

   “No measurable quality improvement” is too broad. The evaluation has binary rubric pass/fail and one judge per pair; it demonstrates equal rubric outcomes, not absence of subtler quality differences. Efficiency is mixed: simulator treatment was lower (92.6s / 11 events / 7 commands versus 107.3s / 21 / 18), while CogStash treatment was higher (128.9s / 28 / 22 versus 90.7s / 12 / 9).

## Supported claims

- Final baseline and treatment arms both passed the defined read-only rubric.
- The selected runs preserved recorded repository state and treatment hashes.
- Push URLs were disabled in the recorded run states.
- The final result supports preservation/safety on these two cases.

## Unsupported or overstated claims

- That attempt 3 retained behavior from earlier treatment versions.
- That the discovery-budget change alone caused the runtime/command reductions.
- That repository/network isolation was complete.
- That the skill produced no quality improvement beyond this binary rubric.

## Required next actions

- Record and report every run, including retry reason, exclusion status, treatment hash, model metadata, and selection rationale.
- Freeze one treatment hash before evaluation and use fresh matched baseline/treatment repetitions.
- Add full repository tree hashes and an enforced network-deny mechanism.
- Make the report builder validate run/judgment integrity before generating headline claims.
- Reword conclusions as “no uplift detected under this rubric,” and separate safety evidence from quality-uplift evidence.