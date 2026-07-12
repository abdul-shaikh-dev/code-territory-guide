# Adversarial Audit — 2026-07-12 Recorded Matrix

## Verdict

**FAIL.** The headline counts are reproducible, but material provenance, isolation, routing, schema, and judge-evidence defects prevent the report’s behavioral claims from being supported.

## Findings

### Critical

1. **Treatment contamination invalidates the task-failure improvement claim.**  
   `task-caused-validation-failure--installed-skill--seed-1` records file changes to the user-level `plugin-creator` skill, not the requested slug normalizer. Its agent messages explicitly report editing `C:\Users\abdul\.codex\skills\.system\plugin-creator`. The structured run fields remain empty for worktree state, diff, and validation. See `evals/results/runs/task-caused-validation-failure--installed-skill--seed-1.json`, `evals/run_matrix.py:53-64,100-109`, and `evals/results/judgments/task-caused-validation-failure.attempt-2.json`.

   The judge omits `file_change` events and actual command output (`evals/judge_matrix.py:47-65`), so the report’s “task-caused-failure improved” claim is based largely on self-report. This is a harness-isolation failure, not reliable evidence of skill success or failure.

2. **The harness cannot exercise most claimed repository behaviors.**  
   It injects fixtures as prompt prose, launches agents in empty temporary directories, uses read-only mode, and explicitly says “Do not modify files” (`evals/run_matrix.py:38-50,56-64`). This affects nine manifest cases. The report acknowledges the limitation, but its policy-selection, ownership, validation, and completion claims remain weaker than stated.

3. **Treatment provenance is incomplete.**  
   Run records store only a home-directory `skill_path`; `policy_payload` is always `null` (`evals/run_matrix.py:100-103`). No skill/source hash or immutable treatment snapshot is recorded. Exact installed treatment provenance therefore cannot be verified from the package.

4. **Recorded models do not match current routing.**  
   `evals/model-routing.json` routes five cases to `gpt-5.6-luna`, but all ten valid `seed-2` records for those cases use `gpt-5.6-sol`: `environmental-validation-block`, `explicit-scope-no-double-confirmation`, `hidden-scope-expansion`, `lightweight-trivial-edit`, and `trigger-negative-simple-question`, for both arms. The mismatch is unexplained and confounds the comparisons.

5. **`run-record.schema.json` is invalid JSON.**  
   It fails parsing at EOF and has unbalanced braces. Therefore the package cannot establish run-record schema compliance, despite `evals/README.md:70-72` claiming schema validation.

### High

6. **Seeds are labels, not controlled seeds.**  
   `run_matrix.py` accepts `seed` but only uses it in filenames and `run_id`; it never passes a seed to the model or harness (`evals/run_matrix.py:53-64`). `seed-1` versus `seed-2` is not evidence of independent seeded reruns.

7. **Judge independence and evidence completeness are overstated.**  
   The judge uses `gpt-5.6-sol`, also used by six treatment cases (`evals/model-routing.json:7-13,16`). It receives only agent messages and command metadata, omitting file changes, command output, validation, stderr, and diffs (`evals/judge_matrix.py:47-65`). The structured judgments do preserve all rubric criteria and have internally consistent pass fields, but their substantive correctness is not independently established.

8. **Fixture hashes are only internally consistent.**  
   Records contain stable 64-character hashes and expected context paths, but the fixture bytes are not part of the audited package. Actual hash provenance cannot be verified from the permitted paths.

9. **The report’s “seven” count is wrong.**  
   The manifest has nine fixture-backed cases, and eight of those have failing treatment judgments. The report says “seven fixture-backed failures” and “seven repository-action cases” (`evals/results/2026-07-12-recorded-matrix.md:41,56`).

### Medium

10. **The first-judge-attempt explanation is overgeneralized.**  
    Most excluded attempts have stderr `The command line is too long`, but `lightweight-trivial-edit.json` and `trigger-negative-simple-question.json` exited zero and returned empty/wrong `case_id` judgments. The report attributes all first attempts to Windows command-line rejection (`evals/results/2026-07-12-recorded-matrix.md:43`).

## Verified counts

- Manifest cases: **11** — 9 fixture-backed, 2 trigger controls.
- Raw run records: **32** — 16 baseline, 16 installed-skill.
- Valid runs: **22**; excluded runs: **10**.
- Valid attempt-2 judgments: **11**.
- Excluded first judge attempts: **11**.
- Baseline pass: **1/11**.
- Treatment pass: **3/11**.
- Outcomes: **4 improved, 7 preserved, 0 regressed, 0 inconclusive**.
- Treatment forbidden behaviors recorded: **0**.
- Selected judgment runs: seed 2 for five cases; seed 1 for six cases.

## Claims supported

- The headline counts and result table match the 11 valid structured judgments.
- Criterion completeness and pass-field consistency are internally correct.
- Raw run and judge artifacts, including excluded attempts, are preserved.
- The arithmetic negative-trigger behavior is directly evidenced by `trigger-negative-simple-question--installed-skill--seed-2`.
- Positive triggering is evidenced by `trigger-obvious-nontrivial-work--installed-skill--seed-1`.

## Claims not supported

- End-to-end repository behavior or successful repository edits.
- The task-caused-failure improvement claim.
- General standalone-policy efficacy from an empty workspace.
- Exact treatment payload/version provenance.
- Valid seeded rerun or model-routing provenance.
- Independent correctness of the judge’s substantive scores.
- The report’s seven-case repository-action count.

## Required next actions

1. Repair and validate `evals/run-record.schema.json`; add deterministic schema validation.
2. Rerun with isolated, materialized Git fixtures and writable per-run workspaces.
3. Capture worktree-before/after, diffs, file changes, command output, and validation results.
4. Isolate home directories and prevent writes outside each run workspace.
5. Record treatment/source hashes, routing snapshot hashes, full harness configuration, and real model seeds.
6. Reconcile routing before rerunning the ten mismatched records.
7. Expand judge evidence to include sanitized file changes, outputs, diffs, and validation; use an independently routed judge.
8. Recompute the report from corrected records and replace the unsupported seven-case claims.