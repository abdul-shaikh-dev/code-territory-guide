# Code Territory Guide

This repository contains the `code-territory-guide` skill for controlled, evidence-led code changes.

## Installation

Install `skills/code-territory-guide/` in the custom-skills location used by your agent platform. The skill is self-contained; its canonical references include the trust, scope, ownership, validation, review, artifact, and delivery policy previously carried by a companion `AGENTS.md`.

## Structure

```text
code-territory-guide/
├── README.md
├── evals/
│   ├── README.md
│   ├── manifest.json
│   ├── validate_manifest.py
│   └── fixtures/
└── skills/
    └── code-territory-guide/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── field-entry.md
            ├── model-routing.md
            ├── modes.md
            ├── safety-and-scope.md
            ├── standard-workflow.md
            └── templates.md
```

`SKILL.md` is the lightweight router. Detailed policy and workflows use progressive disclosure through `references/`.

## Behavioral Evaluation

`evals/manifest.json` defines pressure, ownership, failure-state, and trigger cases. Run `python evals/validate_manifest.py` to validate the suite, then use clean baseline and treatment sessions as described in `evals/README.md`.
