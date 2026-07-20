from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
EXPECTED_NAME = "code-territory-guide"
REQUIRED_SKILL_FILES = (
    "references/safety-and-scope.md",
    "references/artifacts.md",
    "references/delivery.md",
    "references/modes.md",
    "references/unknowns-lifecycle.md",
    "references/standard-workflow.md",
    "references/templates.md",
    "references/model-routing.md",
    "references/field-entry.md",
    "agents/openai.yaml",
    "scripts/validate_visual_prototype.py",
    "assets/artifacts/survey.md",
    "assets/artifacts/track-report.md",
    "assets/artifacts/field-brief.md",
    "assets/artifacts/implementation-notes.md",
    "assets/artifacts/field-report.md",
    "assets/artifacts/expedition-index.md",
    "assets/artifacts/explainer.md",
    "assets/artifacts/visual-prototype.html",
)
JSON_FILES = (
    "package.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    ".kimi-plugin/plugin.json",
    "evals/manifest.json",
    "evals/real-repo-manifest.json",
    "evals/model-routing.json",
    "evals/evaluation-lock.json",
    "evals/run-record.schema.json",
    "evals/judge-output.schema.json",
    "evals/judge-blind-output.schema.json",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_json(relative: str) -> dict:
    path = ROOT / relative
    require(path.is_file(), f"missing JSON file: {relative}")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{relative} must contain a JSON object")
    return data


def parse_skill_frontmatter() -> dict[str, str]:
    skill_path = ROOT / "skills" / EXPECTED_NAME / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    require(text.startswith("---\n"), "SKILL.md must start with YAML frontmatter")
    parts = text.split("---\n", 2)
    require(len(parts) == 3, "SKILL.md frontmatter must have a closing delimiter")

    metadata: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        require(bool(separator), f"invalid SKILL.md frontmatter line: {line}")
        metadata[key.strip()] = value.strip()
    return metadata


def validate() -> None:
    parsed = {relative: load_json(relative) for relative in JSON_FILES}
    package = parsed["package.json"]
    plugin = parsed[".claude-plugin/plugin.json"]
    marketplace = parsed[".claude-plugin/marketplace.json"]

    require(package.get("name") == EXPECTED_NAME, "package.json has an unexpected name")
    require(plugin.get("name") == EXPECTED_NAME, "plugin.json has an unexpected name")
    require(marketplace.get("name") == EXPECTED_NAME, "marketplace.json has an unexpected name")

    plugins = marketplace.get("plugins")
    require(isinstance(plugins, list) and len(plugins) == 1, "marketplace.json must declare one plugin")
    marketplace_plugin = plugins[0]
    require(isinstance(marketplace_plugin, dict), "marketplace plugin entry must be an object")
    require(marketplace_plugin.get("name") == EXPECTED_NAME, "marketplace plugin has an unexpected name")

    versions = {
        "package.json": package.get("version"),
        ".claude-plugin/plugin.json": plugin.get("version"),
        ".claude-plugin/marketplace.json": marketplace_plugin.get("version"),
        ".codex-plugin/plugin.json": parsed[".codex-plugin/plugin.json"].get("version"),
        ".cursor-plugin/plugin.json": parsed[".cursor-plugin/plugin.json"].get("version"),
        ".kimi-plugin/plugin.json": parsed[".kimi-plugin/plugin.json"].get("version"),
    }
    require(all(isinstance(value, str) for value in versions.values()), "all manifests must declare a version")
    require(len(set(versions.values())) == 1, f"manifest versions do not match: {versions}")
    version = next(iter(versions.values()))
    require(SEMVER_PATTERN.fullmatch(version) is not None, f"invalid semantic version: {version}")

    main_path = package.get("main")
    require(isinstance(main_path, str) and (ROOT / main_path).is_file(), "package.json main file is missing")
    pi_skills = package.get("pi", {}).get("skills")
    require(isinstance(pi_skills, list) and pi_skills, "package.json must declare Pi skill paths")
    for relative in pi_skills:
        require(isinstance(relative, str) and (ROOT / relative).is_dir(), f"missing Pi skill path: {relative}")

    metadata = parse_skill_frontmatter()
    require(metadata.get("name") == EXPECTED_NAME, "SKILL.md frontmatter has an unexpected name")
    require(bool(metadata.get("description")), "SKILL.md frontmatter requires a description")

    skill_root = ROOT / "skills" / EXPECTED_NAME
    skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    for reference in ("references/artifacts.md", "references/delivery.md"):
        require(reference in skill_text, f"SKILL.md must directly route to {reference}")

    agents_path = ROOT / "AGENTS.md"
    require(agents_path.is_file(), "missing repository AGENTS.md bootstrap")
    require(
        "skills/code-territory-guide/SKILL.md" in agents_path.read_text(encoding="utf-8"),
        "AGENTS.md must point to the canonical skill router",
    )
    for relative in REQUIRED_SKILL_FILES:
        require((skill_root / relative).is_file(), f"missing required skill file: {relative}")

    for relative in ("site/index.html", "site/.nojekyll", ".github/workflows/pages.yml"):
        require((ROOT / relative).is_file(), f"missing visual explainer delivery file: {relative}")

    print(f"Validated package structure and aligned manifest version {version}.")


if __name__ == "__main__":
    validate()
