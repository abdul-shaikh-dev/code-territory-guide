# Skills and AGENTS.md audit — 5 September 2026

The highest-value changes are to reconcile model policy, narrow automatic activation, and make approval gates conditional. Keep project-specific constraints, real tool contracts, financial safeguards, and evidence-based completion criteria.

This is an audit, not an instruction rewrite. Only this report and `inventory.csv` were created. Audited instructions were not modified; nothing was committed or published.

## Basis and coverage

Read Eric Provencher's [Rethinking skills and prompts for GPT-6 Astra](https://x.com/pvncher/status/2095991462416490862), published 4 September 2026. X returned 403, so the article text was recovered through [FxTwitter's public response](https://api.fxtwitter.com/status/2095991462416490862). Both embedded comparison images were downloaded and inspected.

The article recommends precise descriptions, conditional reference loading, fewer prescribed steps, model-sensitive guidance, and clear completion/continuation boundaries. It does not establish that every long skill or detailed safeguard is defective.

Reviewed **53 SKILL.md files, including all 38 active session skills, and nine AGENTS.md files**. Additional files are source, packaged, supporting, archived, or temporary task copies. [inventory.csv](inventory.csv) records every reviewed root file, its status, size, and disposition. Relevant supporting references were also inspected. Active means listed in this session, not merely present on disk.

Search boundary: `G:/Projects`, `G:/tmp`, the user's `.agents`, `.codex/skills`, `.copilot`, `.gemini`, `.continue`, `.pi`, `.config`, `.local`, `.impeccable`, `source`, `Documents`, `Downloads`, and `OneDrive`; the exact current plugin roots supplied by the session; and ancestor AGENTS.md paths. Dependency trees, Git internals, old marketplace downloads, vendor imports, and `.real-eval-temp` runtime snapshots were excluded from semantic review. Initial discovery encountered inaccessible cache directories. This is a bounded local audit, not a claim to cover every disk, inaccessible location, or inactive vendor version.

## Priority findings

### 1. Model-routing policies disagree

**High priority — observed contradiction.** [Global AGENTS.md](C:/Users/abdul/.codex/AGENTS.md:8) requests Sol/medium, Terra exploration/high, and Luna mechanical/high. [Code Territory Guide](G:/Projects/2026/cool_projects/code-territory-guide/skills/code-territory-guide/references/model-routing.md:34) requests Sol/high, Terra exploration/medium, and Luna mechanical/low. The global file also defers to the skill. Portable AGENTS.md repeats routing policy again.

The routes cover Sol/Terra/Luna but do not explicitly describe the already-running Astra role. That omission is not evidence that older models are unsuitable; it leaves primary-agent versus worker selection ambiguous.

**Recommendation:** maintain one mapping and make the global file a short pointer plus user preferences. Distinguish keeping the current capable primary agent from choosing a worker. Add Astra-aware guidance based on observed task performance. Preserve bounded delegation and complete handoffs.

### 2. Impeccable imposes repeated approval pauses

**High priority — observed stopping rules.** [Craft](C:/Users/abdul/.agents/skills/impeccable/reference/craft.md:11) mandates shape, direction, palette, and mock gates and says to stop at each. [The Codex flow](C:/Users/abdul/.agents/skills/impeccable/reference/codex.md:29) requires separate direction answers, palette confirmation, and mock approval. A supplied brief can skip part of shape but does not generally remove the remaining gates.

**Recommendation:** retain this sequence for explicitly requested collaborative exploration. For authorized implementation with a supplied direction, ask only about unresolved material choices, then build, inspect, and correct through the requested completion boundary. A skill cannot override the user's standing authorization to continue.

### 3. Impeccable's mandatory helper path is broken in this workspace

**High priority — verified local path defect.** [Setup](C:/Users/abdul/.agents/skills/impeccable/SKILL.md:13) requires `node .agents/skills/impeccable/scripts/context.mjs`. That project-relative file is absent here; the global installation contains the script. Its palette command has the same assumption.

**Recommendation:** resolve helpers relative to the loaded skill, and pass the project root/target separately. Do not require duplicate installation merely to satisfy a hard-coded relative command.

### 4. Controlled-coding is unsuitable as a default autonomous workflow

**High priority if automatically enabled; otherwise an intentional supervised mode.** [The router](G:/Projects/2026/cool_projects/controlled-coding-workflow-plugin/skills/controlled-coding/SKILL.md:12) interprets implementation requests as plan-then-wait, limits execution to one approved step, and stops whenever a plan assumption changes. [Scaffold](G:/Projects/2026/cool_projects/controlled-coding-workflow-plugin/skills/controlled-coding-scaffold/SKILL.md:10) rejects chat-only plans, requires a saved canonical plan, and [requires another confirmation](G:/Projects/2026/cool_projects/controlled-coding-workflow-plugin/skills/controlled-coding-scaffold/SKILL.md:55) before editing. A direct scaffold request without that plan reaches a documented stop.

**Recommendation:** activate this family for explicit controlled-coding/approval-per-step requests. Preserve the supervised behavior for users who choose it. Provide a route to create the missing plan and scaffold together when authorized. It should not override ordinary end-to-end implementation requests.

### 5. Code Territory Guide still loads substantial general procedure

**Medium priority — static overhead, not measured latency.** [The router](G:/Projects/2026/cool_projects/code-territory-guide/skills/code-territory-guide/SKILL.md:20) has useful conditional links. Nevertheless, a multi-step Expedition loads safety, standard workflow, and unknowns; the workflow then [loads artifact policy](G:/Projects/2026/cool_projects/code-territory-guide/skills/code-territory-guide/references/standard-workflow.md:80) even to decide to stay in chat. Those five files total **4,851 whitespace-separated words**, before source code, tests, or optional model routing. This is not a token count or a claim that they reload every turn.

[A durable brief is mandated for multi-step work](G:/Projects/2026/cool_projects/code-territory-guide/skills/code-territory-guide/references/standard-workflow.md:119), despite nearby allowance for small single-model work in chat. [The three-command-batch default](G:/Projects/2026/cool_projects/code-territory-guide/skills/code-territory-guide/SKILL.md:69) also competes with the more useful evidence-based discovery stopping rule.

**Recommendation:** make the router sufficient for routine scoped changes. Disclose complex discovery, delivery, multi-session artifacts, and routing when needed. Base durable briefs on handoff/resumption complexity, not step count. Replace command counts with the existing evidence-based stopping criterion.

### 6. Two Code Territory Guide boundaries invite unnecessary questions

**Medium priority — wording risk.** [Safety policy](G:/Projects/2026/cool_projects/code-territory-guide/skills/code-territory-guide/references/safety-and-scope.md:74) pauses whenever two material product/architecture options remain viable. Multiple options alone do not show that a user decision is necessary. [The deletion example](G:/Projects/2026/cool_projects/code-territory-guide/skills/code-territory-guide/references/field-entry.md:45) asks permission to correct false permanent-deletion copy after the API proves recovery is possible.

**Recommendation:** ask when a choice changes authorized behavior, consequences, or unresolved user intent. Allow internal implementation choices and factual corrections that preserve the requested behavior. Retain confirmation for changing actual deletion semantics. Preserve the existing beyond-request scope gate and its no-repeat-approval rule.

### 7. Descriptions are broad enough to compete

**Medium priority — activation risk, not proven truncation.** Raw description-line lengths are **895 characters** for Impeccable, **518** for Code Territory Guide, and **303** for find-skills. Impeccable enumerates almost every frontend surface and improvement verb. [Find-skills](C:/Users/abdul/.agents/skills/find-skills/SKILL.md:12) also reaches generic capability/how-to requests in its body. Active Product Design audit overlaps Impeccable audit; archived frontend-design would add another collision if enabled.

**Recommendation:** define distinct activation boundaries and move branch lists inside routers. Candidate descriptions:

- Code Territory Guide: “Handle code changes with material uncertainty about behavior, compatibility, ownership, or delivery. Use for scoped discovery, debugging, implementation, and review.”
- Impeccable: “Design and refine frontend interfaces. Use for visual direction, UX critique, or the named Impeccable workflows.”
- Find-skills: “Find installable agent skills when the user asks to discover or extend agent capabilities.”

Do not count inactive cached copies as current context overhead. No runtime evidence established actual description truncation or misrouting.

### 8. Writing-great-skills contradicts Codex invocation guidance

**High priority for future skill creation — observed documentation conflict.** [The skill](C:/Users/abdul/.agents/skills/writing-great-skills/SKILL.md:15) describes `disable-model-invocation: true`; [its glossary](C:/Users/abdul/.agents/skills/writing-great-skills/GLOSSARY.md:29) recommends deleting descriptions. [The local Codex creator](C:/Users/abdul/.codex/skills/.system/skill-creator/SKILL.md:90) preserves required descriptions and uses `agents/openai.yaml` with `policy.allow_implicit_invocation: false`. The writing skill remains visible in this session's catalog despite its frontmatter flag.

**Recommendation:** document invocation mechanisms per host. Use Codex's supported policy metadata here and preserve required descriptions. Remove universal claims of zero context cost and portable description deletion. The catalog observation does not identify the responsible parser behavior. Keep the skill's useful pruning, progressive disclosure, and single-source guidance.

### 9. Portable AGENTS.md is an always-loaded manual

**Medium priority — intentional deployment tradeoff.** [Portable AGENTS.md](G:/Projects/2026/cool_projects/code-territory-guide/portable/AGENTS.md:1) is **487 lines / 3,045 words**. Self-containment puts all modes, artifacts, delivery, routing, validation, and report templates in one file. Skipping its workflow for a tiny task does not remove the loaded text.

**Recommendation:** retain it as an explicitly named standalone/full edition and offer a compact default with local constraints and conditional pointers. [This repository's 12-line AGENTS.md](G:/Projects/2026/cool_projects/code-territory-guide/AGENTS.md:1) is the better default pattern. Source/package/install duplication is not a sync defect: checks passed.

### 10. Current CogVest guidance is better than secondary copies

**Medium priority before reuse; do not blindly synchronize snapshots.** [Primary CogVest](G:/Projects/2026/cool_projects/CogVest/AGENTS.md:14) uses a relevant source set, proportional verification, and explicit branch/commit/push/PR authorization. Preserve native-currency correctness, pure calculations, persistence constraints, and release protections.

Refine [“approved behavior contract”](G:/Projects/2026/cool_projects/CogVest/AGENTS.md:65) to explicitly accept an already-approved issue or user request. Make [sync-before-edit](G:/Projects/2026/cool_projects/CogVest/AGENTS.md:87) distinguish starting new work from resuming an existing branch. PR verification remains a legitimate completion gate.

[The secondary checkout](G:/Projects/2026/cool_projects/code-territory-guide-real-repos/CogVest/AGENTS.md:44), `G:/tmp/CogVest-issue-126/AGENTS.md`, and `G:/tmp/CogVest-agents-model-routing/AGENTS.md` retain blanket Superpowers prerequisites and older issue/V1 boundaries. Treat them as historical/task-specific instructions and re-evaluate before resuming. Do not rewrite historical evidence just to match the primary checkout. Superpowers is not in this session's active catalog.

### 11. Vendor workflows assume unavailable tools

**High priority operational compatibility; fix upstream or through supported configuration.** [Computer Use](C:/Users/abdul/.codex/plugins/cache/openai-bundled/computer-use/26.901.41600/skills/computer-use/SKILL.md:10) specifies `node_repl` and `@oai/sky`; this session offers `mcp__cua_repl` and `cua`. Browser discovery returned “No browser is available.” [Spreadsheets](C:/Users/abdul/.codex/plugins/cache/openai-primary-runtime/spreadsheets/26.904.11930/skills/spreadsheets/SKILL.md:23) and [Deep Research](C:/Users/abdul/.codex/plugins/cache/openai-curated-remote/deep-research-work/0.1.14/skills/deep-research/SKILL.md:28) require an absent `update_plan`. Some Figma workflows also require tools not exposed here.

[OpenAI Docs](C:/Users/abdul/.codex/skills/.system/openai-docs/SKILL.md:12) mandates official-document retrieval before local context, conflicting with this session's higher-priority local-first product guidance. This is environment-specific, not a universal docs-first defect.

**Recommendation:** add capability-aware routes and honest fallbacks, or use a compatible connector/runtime. Do not invent missing tools or edit vendor caches as a durable fix. Detailed API precautions remain useful.

### 12. Figma's one-component trigger activates a full-library recipe

**Medium priority — overbroad branch.** [Generate-library](C:/Users/abdul/.codex/plugins/cache/openai-curated-remote/figma/2.0.21/skills/figma-generate-library/SKILL.md:3) applies even to one component, but [its workflow](C:/Users/abdul/.codex/plugins/cache/openai-curated-remote/figma/2.0.21/skills/figma-generate-library/SKILL.md:59) prescribes discovery, foundations, page skeletons, documentation, and sequential creation. That is disproportionate to a component in an established library.

**Recommendation:** provide a small path that reuses existing tokens/pages and validates the requested component. Keep the full path for a system/library request. Treat operation caps and exact image counts as defaults where risk permits.

## Remaining skill dispositions

Individual root paths are recorded in the inventory; groups below include every remaining reviewed family.

| Skills | Disposition |
|---|---|
| controlled-coding-plan, review, scaffold | Keep supervised phase boundaries; make activation explicit and clarify saved-plan handoff. |
| copilot-ghost-implementer | Keep focused real-file/autocomplete purpose. Reconsider `references/evaluation.md:353` automatically appending gotchas; persist only verified reusable lessons when authorized. |
| archived frontend-design | Keep archived unless needed. Concise body; review broad activation and universal aesthetic bans before enabling. |
| skill-creator | Strong alignment: capable-model assumption, precise descriptions, progressive disclosure. Keep. |
| skill-installer, plugin-creator | Keep specialized operational constraints. Optional shortening of branch descriptions. |
| imagegen | Keep generation/editing boundaries and asset-delivery requirements. No high-priority editorial defect established. |
| review-agent (not listed active) | Keep focused review role; no current invocation overhead attributed. |
| documents, pdf, presentations | Keep final rendering QA and format-specific mechanics. Reduce repeated rendering only where a change cannot affect layout. |
| spreadsheets, excel-live-control | Keep standalone/live-workbook separation. Fix absent tools and disclose specialized API details by task. |
| template-creator | Keep explicit reusable-template trigger and source extraction. |
| Figma code-connect, create-new-file, design-to-code | Keep specialized contracts and prerequisites; establish connector availability. |
| Figma generate-design, generate-diagram | Keep token/component discovery and diagram routing; scope full-screen procedure to composed views. |
| Figma implement-motion, swiftui, use-figjam, use-motion, use-slides | Keep specialized API guidance. Narrow SwiftUI description to SwiftUI–Figma translation rather than any Swift/iOS mention. |
| Figma use | Keep Plugin API invariants and targeted type lookup. Make universal operation budgets risk-based defaults. |
| Product Design index, audit, image-to-code | Keep explicit routing, screenshot evidence, and source fidelity; clarify overlap with Impeccable. |
| Product Design ideate, url-to-code | Relax exactly-three-image defaults. Exhaustive interaction capture is appropriate for exhaustive cloning; otherwise follow requested fidelity and important states. |
| Product Design design-qa, get-context, research, share, user-context | Installed supporting workflows, not active catalog entries. Keep conditional loading; no active overhead attributed. |
| deep-research | Keep explicit Deep Research activation; gate missing tools and tie formatted artifacts to the deliverable. |
| plugin-management | Keep plugin-specific connection/permission work; no high-priority content defect established. |
| sites-building, sites-hosting | Keep hosting contracts and publishing boundaries. Make prescribed imagegen delegation depend on actual asset need. |
| visualize | Keep inline/standalone distinction. Tune proactive description if routing evaluations show unnecessary invocation. |
| Product Design prototype/mobile template AGENTS.md | Govern generated project copies. Keep runtime contracts and explicit mobile publishing boundary. Project-specific feedback storage is not proof of vendor-cache mutation. |

## Preserve and validate

Keep user-work preservation, currency correctness, migration/recovery cases, secret exclusion, authorized delivery boundaries, tool API invariants, and final visual QA. Keep precise acceptance criteria and task-caused-failure correction. The article argues against unnecessary scaffolding, not against knowing what done means.

Recommended sequence: reconcile model/invocation policy; fix Impeccable paths and supervision gates; slim the default Code Territory Guide route; separate frontend triggers; then address vendor/runtime compatibility. Evaluate representative tasks before pruning more: typo, narrow bug, multi-step feature, specified UI implementation, existing-library component, and explicitly supervised scaffold. Compare completion, unnecessary questions, context use, and actual defects. Word counts alone do not demonstrate performance gains.

## Validation and limitations

- Read all 38 active skill roots, additional discovered roots, and nine AGENTS.md files within the boundary. Two Terra/high workers handled bounded vendor and personal reads; the primary agent rechecked consequential findings and discarded unsupported claims.
- `python scripts/sync_plugin_bundle.py --check`: passed, 22 packaged files.
- Source, packaged, and installed Code Territory Guide entrypoint hashes match. Installed Markdown/YAML comparisons found no differences.
- Checked cited local paths, description sizes, helper existence, and current tool availability. Personal-skill Markdown link checks passed.
- No model-backed behavior experiment, application test suite, build, or publishing operation ran. Activation/latency concerns are static hypotheses, not measured regressions.
- Secondary CogVest Git inspection initially failed on sandbox ownership; a command-scoped `safe.directory` override enabled a read-only commit check. No global Git settings changed.
- Historical marketplace/cache/evaluation copies were classified rather than treated as independent active instructions. Locations outside the search boundary remain unaudited.

Audit complete within the recorded boundary. Recommendation implementation is a separate task.
