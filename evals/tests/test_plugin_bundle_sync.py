from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import sync_plugin_bundle


class PluginBundleSyncTests(unittest.TestCase):
    def make_repository(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        files = {
            ".codex-plugin/plugin.json": "{}\n",
            ".claude-plugin/plugin.json": "{}\n",
            "skills/code-territory-guide/SKILL.md": "# Skill\n",
        }
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

        subprocess.run(["git", "init", "--quiet", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        return temporary, root

    def test_expected_sources_use_only_git_tracked_skill_files(self) -> None:
        temporary, root = self.make_repository()
        self.addCleanup(temporary.cleanup)

        sources = sync_plugin_bundle.expected_sources(root)

        self.assertIn(Path("skills/code-territory-guide/SKILL.md"), sources)
        self.assertNotIn(Path("assets/portable/AGENTS.md"), sources)
        self.assertNotIn(Path(".cursor-plugin/plugin.json"), sources)
        self.assertNotIn(Path(".kimi-plugin/plugin.json"), sources)

    def test_nonignored_untracked_skill_file_blocks_packaging(self) -> None:
        temporary, root = self.make_repository()
        self.addCleanup(temporary.cleanup)
        unexpected = root / "skills/code-territory-guide/secret.txt"
        unexpected.write_text("do not package\n", encoding="utf-8")

        with self.assertRaisesRegex(
            ValueError,
            "(?s)non-ignored untracked files.*secret.txt",
        ):
            sync_plugin_bundle.expected_sources(root)

    def test_ignored_skill_cache_is_not_packaged(self) -> None:
        temporary, root = self.make_repository()
        self.addCleanup(temporary.cleanup)
        gitignore = root / ".gitignore"
        gitignore.write_text("__pycache__/\n*.pyc\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(root), "add", ".gitignore"],
            check=True,
        )
        cache = root / "skills/code-territory-guide/__pycache__/helper.pyc"
        cache.parent.mkdir(parents=True)
        cache.write_bytes(b"cache")

        sources = sync_plugin_bundle.expected_sources(root)

        self.assertNotIn(
            Path("skills/code-territory-guide/__pycache__/helper.pyc"),
            sources,
        )

    def test_untracked_static_source_blocks_packaging(self) -> None:
        temporary, root = self.make_repository()
        self.addCleanup(temporary.cleanup)
        subprocess.run(
            ["git", "-C", str(root), "rm", "--cached", ".codex-plugin/plugin.json"],
            check=True,
            capture_output=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            "(?s)static sources must be Git-tracked.*\\.codex-plugin/plugin.json",
        ):
            sync_plugin_bundle.expected_sources(root)

    def test_bundle_policy_rejects_repository_only_and_adapter_paths(self) -> None:
        rejected = (
            Path("docs/guide.md"),
            Path("evals/result.json"),
            Path("scripts/helper.py"),
            Path("assets/portable/AGENTS.md"),
            Path(".cursor-plugin/plugin.json"),
            Path(".kimi-plugin/plugin.json"),
            Path("skills/code-territory-guide/__pycache__/helper.pyc"),
        )

        for relative in rejected:
            with self.subTest(relative=relative):
                with self.assertRaises(ValueError):
                    sync_plugin_bundle.validate_destination(relative)


if __name__ == "__main__":
    unittest.main()
