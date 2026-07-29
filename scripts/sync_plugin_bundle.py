from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "code-territory-guide"
BUNDLE_RELATIVE = Path("plugins") / PLUGIN_NAME
SKILL_RELATIVE = Path("skills") / PLUGIN_NAME

STATIC_FILE_SOURCES = {
    Path(".codex-plugin/plugin.json"): Path(".codex-plugin/plugin.json"),
    Path(".claude-plugin/plugin.json"): Path(".claude-plugin/plugin.json"),
}

FORBIDDEN_TOP_LEVEL = {
    ".agents",
    ".cursor-plugin",
    ".git",
    ".github",
    ".kimi-plugin",
    ".opencode",
    "assets",
    "docs",
    "evals",
    "portable",
    "scripts",
    "site",
}
FORBIDDEN_PARTS = {
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
FORBIDDEN_NAMES = {
    ".DS_Store",
    "Thumbs.db",
}
FORBIDDEN_SUFFIXES = {
    ".pyc",
    ".pyo",
}


def git_paths(root: Path, *arguments: str) -> set[Path]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", *arguments],
        check=True,
        capture_output=True,
    )
    return {
        Path(item.decode("utf-8"))
        for item in result.stdout.split(b"\0")
        if item
    }


def tracked_skill_paths(root: Path) -> set[Path]:
    return git_paths(root, "--cached", "--", SKILL_RELATIVE.as_posix())


def untracked_paths(root: Path) -> set[Path]:
    return git_paths(
        root,
        "--others",
        "--exclude-standard",
        "--",
        SKILL_RELATIVE.as_posix(),
    )


def validate_destination(relative: Path) -> None:
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"bundle destination escapes the plugin root: {relative}")

    allowed = (
        relative in STATIC_FILE_SOURCES
        or relative.is_relative_to(SKILL_RELATIVE)
    )
    if not allowed:
        raise ValueError(f"bundle destination is not allowlisted: {relative}")

    if relative.parts and relative.parts[0] in FORBIDDEN_TOP_LEVEL:
        raise ValueError(f"forbidden top-level bundle path: {relative}")
    if any(part in FORBIDDEN_PARTS for part in relative.parts):
        raise ValueError(f"forbidden cache path in bundle: {relative}")
    if relative.name in FORBIDDEN_NAMES or relative.suffix in FORBIDDEN_SUFFIXES:
        raise ValueError(f"forbidden file in bundle: {relative}")


def expected_sources(root: Path = ROOT) -> dict[Path, Path]:
    untracked = untracked_paths(root)
    if untracked:
        listed = "\n- ".join(path.as_posix() for path in sorted(untracked))
        raise ValueError(
            "canonical skill contains non-ignored untracked files; stage or remove "
            "them before packaging:\n"
            f"- {listed}"
        )

    tracked = git_paths(root, "--cached")
    tracked_skill = tracked_skill_paths(root)
    untracked_static = {
        source for source in STATIC_FILE_SOURCES.values() if source not in tracked
    }
    if untracked_static:
        listed = "\n- ".join(path.as_posix() for path in sorted(untracked_static))
        raise ValueError(
            "canonical static sources must be Git-tracked before packaging:\n"
            f"- {listed}"
        )

    sources = {
        destination: root / source
        for destination, source in STATIC_FILE_SOURCES.items()
    }
    for source in sorted(tracked_skill):
        relative = source.relative_to(SKILL_RELATIVE)
        destination = SKILL_RELATIVE / relative
        sources[destination] = root / source

    for destination, source in sources.items():
        validate_destination(destination)
        if not source.is_file():
            raise ValueError(
                f"missing canonical bundle source: {source.relative_to(root)}"
            )
    return sources


def actual_files(bundle_root: Path) -> set[Path]:
    if not bundle_root.is_dir():
        return set()
    return {
        path.relative_to(bundle_root)
        for path in bundle_root.rglob("*")
        if path.is_file()
    }


def sync_bundle(sources: dict[Path, Path], bundle_root: Path) -> None:
    for relative, source in sources.items():
        destination = bundle_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    unexpected = actual_files(bundle_root) - set(sources)
    if unexpected:
        listed = "\n- ".join(str(path) for path in sorted(unexpected))
        raise ValueError(
            "bundle contains unexpected files; remove them explicitly before syncing:\n"
            f"- {listed}"
        )


def validate_bundle(sources: dict[Path, Path], bundle_root: Path) -> None:
    expected = set(sources)
    actual = actual_files(bundle_root)
    missing = expected - actual
    unexpected = actual - expected
    changed = {
        relative
        for relative, source in sources.items()
        if relative in actual
        and (bundle_root / relative).read_bytes() != source.read_bytes()
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
    bundle_root = ROOT / BUNDLE_RELATIVE
    if args.write:
        sync_bundle(sources, bundle_root)
        print(f"Synchronized minimal plugin bundle ({len(sources)} files).")
    else:
        validate_bundle(sources, bundle_root)
        print(f"Validated minimal plugin bundle ({len(sources)} files).")


if __name__ == "__main__":
    main()
