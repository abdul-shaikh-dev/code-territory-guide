from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "code-territory-guide"
BUNDLE_ROOT = ROOT / "plugins" / PLUGIN_NAME

FILE_SOURCES = {
    Path(".codex-plugin/plugin.json"): ROOT / ".codex-plugin" / "plugin.json",
    Path(".claude-plugin/plugin.json"): ROOT / ".claude-plugin" / "plugin.json",
    Path(".cursor-plugin/plugin.json"): ROOT / ".cursor-plugin" / "plugin.json",
    Path(".kimi-plugin/plugin.json"): ROOT / ".kimi-plugin" / "plugin.json",
    Path("portable/AGENTS.md"): ROOT / "portable" / "AGENTS.md",
}

IGNORED_SOURCE_PARTS = {
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
IGNORED_SOURCE_NAMES = {
    ".DS_Store",
    "Thumbs.db",
}
IGNORED_SOURCE_SUFFIXES = {
    ".pyc",
    ".pyo",
}


def is_runtime_source(path: Path) -> bool:
    relative = path.relative_to(ROOT / "skills" / PLUGIN_NAME)
    return (
        path.is_file()
        and not any(part in IGNORED_SOURCE_PARTS for part in relative.parts)
        and path.name not in IGNORED_SOURCE_NAMES
        and path.suffix not in IGNORED_SOURCE_SUFFIXES
    )


def expected_sources() -> dict[Path, Path]:
    sources = dict(FILE_SOURCES)
    skill_root = ROOT / "skills" / PLUGIN_NAME
    for source in sorted(path for path in skill_root.rglob("*") if is_runtime_source(path)):
        relative = source.relative_to(skill_root)
        sources[Path("skills") / PLUGIN_NAME / relative] = source
    return sources


def actual_files() -> set[Path]:
    if not BUNDLE_ROOT.is_dir():
        return set()
    return {
        path.relative_to(BUNDLE_ROOT)
        for path in BUNDLE_ROOT.rglob("*")
        if path.is_file()
    }


def sync_bundle(sources: dict[Path, Path]) -> None:
    for relative, source in sources.items():
        if not source.is_file():
            raise ValueError(f"missing canonical bundle source: {source.relative_to(ROOT)}")
        destination = BUNDLE_ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    unexpected = actual_files() - set(sources)
    if unexpected:
        listed = "\n- ".join(str(path) for path in sorted(unexpected))
        raise ValueError(
            "bundle contains unexpected files; remove them explicitly before syncing:\n"
            f"- {listed}"
        )


def validate_bundle(sources: dict[Path, Path]) -> None:
    expected = set(sources)
    actual = actual_files()
    missing = expected - actual
    unexpected = actual - expected
    changed = {
        relative
        for relative, source in sources.items()
        if relative in actual
        and (BUNDLE_ROOT / relative).read_bytes() != source.read_bytes()
    }

    problems: list[str] = []
    if missing:
        problems.append("missing:\n- " + "\n- ".join(str(path) for path in sorted(missing)))
    if unexpected:
        problems.append(
            "unexpected:\n- " + "\n- ".join(str(path) for path in sorted(unexpected))
        )
    if changed:
        problems.append("out of sync:\n- " + "\n- ".join(str(path) for path in sorted(changed)))
    if problems:
        raise ValueError("invalid generated plugin bundle:\n" + "\n".join(problems))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synchronize or validate the minimal Code Territory Guide plugin bundle."
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true", help="Copy canonical files into the bundle.")
    action.add_argument("--check", action="store_true", help="Verify exact bundle parity.")
    args = parser.parse_args()

    sources = expected_sources()
    if args.write:
        sync_bundle(sources)
        print(f"Synchronized minimal plugin bundle ({len(sources)} files).")
    else:
        validate_bundle(sources)
        print(f"Validated minimal plugin bundle ({len(sources)} files).")


if __name__ == "__main__":
    main()
