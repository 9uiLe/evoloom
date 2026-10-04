import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("ci_changes.sh")
FLAGS = ("run_checks", "quality", "cli", "prepare", "build", "unit", "copy", "snapshot")


def git(directory, *arguments):
    return subprocess.run(
        ["git", *arguments], cwd=directory, check=True, capture_output=True, text=True
    ).stdout.strip()


class CIChangesTests(unittest.TestCase):
    def test_changed_path_matrix(self):
        cases = {
            "docs/TESTING.md": set(),
            "Sources/Evoloom/Components/IOSButton.swift": set(FLAGS),
            "Tests/EvoloomTests/DesignTokensTests.swift": {
                "run_checks",
                "quality",
                "prepare",
                "unit",
            },
            "Testing/Tests/EvoloomSnapshotTests/Example.swift": {
                "run_checks",
                "quality",
                "prepare",
                "snapshot",
            },
            "Testing/Tests/EvoloomSnapshotTests/__Snapshots__/example.png": {
                "run_checks",
                "prepare",
                "snapshot",
            },
            "tools/registry.json": {"run_checks", "quality", "cli", "prepare", "copy"},
            "tools/test_cli.py": {"run_checks", "quality", "cli"},
            ".github/workflows/ci.yml": set(FLAGS),
            "unexpected.file": set(FLAGS),
        }
        for path, expected in cases.items():
            with self.subTest(path=path), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                self.init_repo(root)
                before = git(root, "rev-parse", "HEAD")
                changed = root / path
                changed.parent.mkdir(parents=True, exist_ok=True)
                changed.write_text("change\n")
                git(root, "add", ".")
                git(root, "commit", "-qm", "change")
                actual = self.run_detector(root, before, git(root, "rev-parse", "HEAD"))
                self.assertEqual(
                    {key for key, value in actual.items() if value}, expected
                )

    def test_manual_run_checks_everything(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.init_repo(root)
            actual = self.run_detector(root, "", "", event="workflow_dispatch")
            self.assertEqual(
                {key for key, value in actual.items() if value}, set(FLAGS)
            )

    def test_unavailable_git_base_checks_everything(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.init_repo(root)
            actual = self.run_detector(root, "0" * 40, git(root, "rev-parse", "HEAD"))
            self.assertEqual(
                {key for key, value in actual.items() if value}, set(FLAGS)
            )

    def test_combined_changes_run_the_union(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.init_repo(root)
            before = git(root, "rev-parse", "HEAD")
            (root / "tools").mkdir()
            (root / "tools/test_cli.py").write_text("change\n")
            (root / "Tests").mkdir()
            (root / "Tests/Example.swift").write_text("change\n")
            git(root, "add", ".")
            git(root, "commit", "-qm", "combined")
            actual = self.run_detector(root, before, git(root, "rev-parse", "HEAD"))
            self.assertEqual(
                {key for key, value in actual.items() if value},
                {"run_checks", "quality", "cli", "prepare", "unit"},
            )

    def test_source_renamed_into_docs_still_runs_full_suite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.init_repo(root)
            (root / "Sources").mkdir()
            (root / "Sources/Example.swift").write_text("source\n")
            git(root, "add", ".")
            git(root, "commit", "-qm", "source")
            before = git(root, "rev-parse", "HEAD")
            (root / "docs").mkdir()
            git(root, "mv", "Sources/Example.swift", "docs/Example.md")
            git(root, "commit", "-qm", "rename")
            actual = self.run_detector(root, before, git(root, "rev-parse", "HEAD"))
            self.assertEqual(
                {key for key, value in actual.items() if value}, set(FLAGS)
            )

    @staticmethod
    def init_repo(root):
        git(root, "init", "-q")
        git(root, "config", "user.name", "CI test")
        git(root, "config", "user.email", "ci@example.invalid")
        (root / "README.md").write_text("initial\n")
        git(root, "add", ".")
        git(root, "commit", "-qm", "initial")

    @staticmethod
    def run_detector(root, base, head, event="push"):
        output = root / "github-output"
        env = os.environ.copy()
        env.update(
            GITHUB_EVENT_NAME=event,
            CI_BASE_SHA=base,
            CI_HEAD_SHA=head,
            GITHUB_OUTPUT=str(output),
        )
        subprocess.run(
            ["bash", str(SCRIPT)], cwd=root, env=env, check=True, capture_output=True
        )
        return {
            key: value == "true"
            for key, value in (
                line.split("=", 1) for line in output.read_text().splitlines()
            )
        }


if __name__ == "__main__":
    unittest.main()
