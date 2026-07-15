from __future__ import annotations

import re
from pathlib import Path
from typing import Any


REDACTED_TEXT = "<redacted treatment-derived text>"
REDACTED_COMMAND = "<redacted skill-read command>"
REDACTED_OUTPUT = "<skill contents omitted from derived evidence>"


def skill_fragments(skill_root: Path) -> tuple[str, ...]:
    fragments: set[str] = set()
    for path in sorted(skill_root.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line in text.splitlines():
            value = line.strip()
            if len(value) >= 60:
                fragments.add(value)
    return tuple(sorted(fragments, key=len, reverse=True))


def path_variants(path: Path) -> tuple[str, ...]:
    value = str(path)
    return tuple({value, value.replace("\\", "/"), value.replace("/", "\\")})


def replace_paths(text: str, sensitive_paths: tuple[Path, ...]) -> str:
    result = text
    for path in sensitive_paths:
        for variant in path_variants(path):
            result = re.sub(re.escape(variant), "<redacted-path>", result, flags=re.IGNORECASE)
    return result


def contains_skill_path(text: str) -> bool:
    normalized = text.replace("/", "\\").lower()
    return (
        "code-territory-guide\\skill.md" in normalized
        or "\\.codex\\skills\\code-territory-guide" in normalized
        or "\\.agents\\skills\\code-territory-guide" in normalized
        or "\\plugins\\cache\\code-territory-guide" in normalized
    )


def sanitize_text(
    text: str,
    sensitive_paths: tuple[Path, ...],
    fragments: tuple[str, ...],
) -> str:
    lowered = text.lower()
    if any(fragment.lower() in lowered for fragment in fragments):
        return REDACTED_TEXT
    return replace_paths(text, sensitive_paths)


def sanitize_value(
    value: Any,
    sensitive_paths: tuple[Path, ...],
    fragments: tuple[str, ...],
) -> Any:
    if isinstance(value, str):
        return sanitize_text(value, sensitive_paths, fragments)
    if isinstance(value, list):
        return [sanitize_value(item, sensitive_paths, fragments) for item in value]
    if isinstance(value, dict):
        return {
            key: sanitize_value(item, sensitive_paths, fragments)
            for key, item in value.items()
        }
    return value


def sanitize_event(
    event: dict,
    sensitive_paths: tuple[Path, ...],
    fragments: tuple[str, ...],
) -> dict:
    kind = event.get("type")
    if kind == "command_execution":
        command = event.get("command", "")
        if contains_skill_path(command) or any(
            variant.lower() in command.lower()
            for path in sensitive_paths
            for variant in path_variants(path)
        ):
            return {
                "type": kind,
                "command": REDACTED_COMMAND,
                "output": REDACTED_OUTPUT,
                "exit_code": event.get("exit_code"),
                "status": event.get("status"),
            }
    return sanitize_value(event, sensitive_paths, fragments)


def evidence_view(record: dict, skill_root: Path) -> list[dict]:
    treatment_path = record.get("treatment", {}).get("path")
    sensitive = [Path.home()]
    if treatment_path:
        treatment = Path(treatment_path)
        sensitive.extend((treatment, treatment.parent, treatment.parent.parent))
    sensitive_paths = tuple(dict.fromkeys(sensitive))
    metadata_fragments = tuple(
        str(record[key])
        for key in ("run_id", "arm", "model")
        if record.get(key)
    )
    fragments = skill_fragments(skill_root) + metadata_fragments
    evidence = [
        sanitize_event(event, sensitive_paths, fragments)
        for event in record.get("tool_events", [])
        if event.get("type") in {"agent_message", "command_execution"}
    ]
    evidence.append({
        "type": "repository_changes",
        "changes": sanitize_value(
            record.get("changed_files", []),
            sensitive_paths,
            fragments,
        ),
    })
    evidence.append({
        "type": "worktree_diff",
        "text": sanitize_text(record.get("diff", ""), sensitive_paths, fragments),
    })
    evidence.append({
        "type": "repository_before",
        "state": sanitize_value(
            record.get("repository_before", {}),
            sensitive_paths,
            fragments,
        ),
    })
    evidence.append({
        "type": "repository_after",
        "state": sanitize_value(
            record.get("repository_after", {}),
            sensitive_paths,
            fragments,
        ),
    })
    return evidence
