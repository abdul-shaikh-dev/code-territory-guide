from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL_ROOT))

from run_real_repo_writable_eval import (  # noqa: E402
    exclusion_reasons,
    git,
    materialize_repository,
    resolved_child,
    validation_results,
)
from validate_real_repo_writable_eval import validate_manifest  # noqa: E402


class WritableRealRepoTests(unittest.TestCase):
    def test_resolved_child_rejects_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "inside").mkdir()
            self.assertEqual(resolved_child(root, "inside"), (root / "inside").resolve())
            with self.assertRaisesRegex(ValueError, "escapes"):
                resolved_child(root, Path("..") / "outside", must_exist=False)

    def test_exclusion_rules_accept_complete_local_commit(self) -> None:
        before = {
            "branch": "eval/case/baseline/attempt-22",
        }
        after = {
            "branch": before["branch"],
            "fetch_url": "DISABLED",
            "push_url": "DISABLED",
            "commits_from_base": 1,
            "commit_subject": "fix: handle boundary",
            "status": "",
        }
        reasons = exclusion_reasons(
            raw="agent completed the task",
            events=[{"type": "agent_message", "text": "done"}],
            before=before,
            after=after,
            treatment_before="skill",
            treatment_after="skill",
            provisioned_before={"deps": "same"},
            provisioned_after={"deps": "same"},
            timed_out=False,
            exit_status=0,
            changed=[{"status": "M", "path": "src/example.py"}],
            validation_observed={"python -m pytest": True},
            commit_subject_pattern="^fix:",
        )
        self.assertEqual(reasons, [])

    def test_exclusion_rules_detect_downgrade_network_and_missing_commit(self) -> None:
        reasons = exclusion_reasons(
            raw="workspace is read-only",
            events=[
                {"type": "agent_message", "text": "blocked"},
                {"type": "command_execution", "command": "git push origin main"},
            ],
            before={"branch": "eval/case/baseline/attempt-22"},
            after={
                "branch": "eval/case/baseline/attempt-22",
                "fetch_url": "DISABLED",
                "push_url": "DISABLED",
                "commits_from_base": 0,
                "commit_subject": "seed",
                "status": "",
            },
            treatment_before=None,
            treatment_after=None,
            provisioned_before={},
            provisioned_after={},
            timed_out=False,
            exit_status=1,
            changed=[],
            validation_observed={"npm test": False},
            commit_subject_pattern="^fix:",
        )
        self.assertIn("workspace-write downgraded to read-only", reasons)
        self.assertIn("model process exited unsuccessfully", reasons)
        self.assertIn("network-capable command observed", reasons)
        self.assertIn("expected exactly one local commit", reasons)
        self.assertIn("no committed task delta", reasons)
        self.assertIn("required validation command not observed", reasons)

    def test_validation_requires_a_successful_matching_command(self) -> None:
        required = ["npm test"]
        self.assertEqual(
            validation_results(
                [
                    {
                        "type": "command_execution",
                        "command": "npm test",
                        "exit_code": 1,
                    }
                ],
                required,
            ),
            {"npm test": False},
        )
        self.assertEqual(
            validation_results(
                [
                    {
                        "type": "command_execution",
                        "command": "npm test",
                        "exit_code": 0,
                    }
                ],
                required,
            ),
            {"npm test": True},
        )

    def test_materialized_arms_start_from_same_commit_with_disabled_remotes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_root = root / "seeds"
            session_root = root / "sessions"
            seed = seed_root / "sample"
            seed.mkdir(parents=True)
            session_root.mkdir()
            subprocess.run(["git", "init", str(seed)], check=True, capture_output=True)
            git(seed, "config", "user.email", "eval@example.invalid")
            git(seed, "config", "user.name", "Evaluation")
            (seed / "README.md").write_text("seed\n", encoding="utf-8")
            git(seed, "add", "README.md")
            git(seed, "commit", "-m", "seed")
            base = git(seed, "rev-parse", "HEAD")
            case = {
                "id": "sample-case",
                "repo": "sample",
                "base_commit": base,
                "provisioned_paths": [],
            }
            states = []
            for arm in ("baseline", "installed-skill"):
                session = session_root / arm
                session.mkdir()
                repo, seed_state = materialize_repository(
                    case,
                    seed_root,
                    session,
                    arm,
                    22,
                )
                states.append((repo, seed_state))
                self.assertEqual(git(repo, "remote", "get-url", "origin"), "DISABLED")
                self.assertEqual(
                    git(repo, "remote", "get-url", "--push", "origin"),
                    "DISABLED",
                )
                self.assertEqual(git(repo, "rev-parse", "HEAD"), base)
            self.assertEqual(states[0][1]["tree"], states[1][1]["tree"])

    def test_writable_manifest_is_structurally_valid(self) -> None:
        import json

        manifest = json.loads(
            (EVAL_ROOT / "real-repo-writable-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        validate_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
