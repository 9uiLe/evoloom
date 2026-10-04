import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("ci_changes.sh")
FLAGS = (
    "run_checks",
    "quality",
    "cli",
    "prepare",
    "ios",
    "unit",
    "copy",
    "snapshot",
    "full",
)


def git(directory, *arguments):
    return subprocess.run(
        ["git", *arguments], cwd=directory, check=True, capture_output=True, text=True
    ).stdout.strip()


class CIChangesTests(unittest.TestCase):
    def test_changed_path_matrix(self):
        cases = {
            "docs/TESTING.md": set(),
            ".github/pull_request_template.md": set(),
            "Sources/Evoloom/Components/IOSButton.swift": set(FLAGS),
            "Testing/Tests/EvoloomSnapshotTests/DesignTokensTests.swift": {
                "run_checks",
                "quality",
                "prepare",
                "ios",
                "unit",
            },
            "Testing/Tests/EvoloomSnapshotTests/Example.swift": {
                "run_checks",
                "quality",
                "prepare",
                "ios",
                "unit",
                "snapshot",
            },
            "Testing/Tests/EvoloomSnapshotTests/ComponentSnapshots.swift": {
                "run_checks",
                "quality",
                "prepare",
                "ios",
                "snapshot",
            },
            "Testing/Sources/EvoloomReviewFixtures/ReviewScreens.swift": {
                "run_checks",
                "quality",
                "prepare",
                "ios",
                "snapshot",
            },
            "Testing/Tests/EvoloomSnapshotTests/__Snapshots__/example.png": {
                "run_checks",
                "prepare",
                "ios",
                "snapshot",
            },
            "Testing/Host/project.json": set(FLAGS),
            "Testing/Host/App/EvoloomReviewHostApp.swift": {
                "run_checks",
                "quality",
                "prepare",
                "ios",
                "snapshot",
            },
            "Testing/Host/Tests/HostedCollectionTests.swift": {
                "run_checks",
                "quality",
                "prepare",
                "ios",
                "snapshot",
            },
            "Testing/Host/Tests/__Snapshots__/HostedCollectionTests/components.collection-light.png": {
                "run_checks",
                "prepare",
                "ios",
                "snapshot",
            },
            "tools/registry.json": {"run_checks", "quality", "cli", "ios", "copy"},
            "tools/test_cli.py": {"run_checks", "quality", "cli"},
            "tools/pr_images.py": {"run_checks", "quality", "cli"},
            "Package.swift": set(FLAGS),
            "flake.lock": set(FLAGS),
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
                {"run_checks", "quality", "cli", "prepare", "ios", "unit"},
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

    def test_cancelled_code_run_is_included_in_next_documentation_push(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.init_repo(root)
            verified = git(root, "rev-parse", "HEAD")
            source = root / "Sources/Example.swift"
            source.parent.mkdir()
            source.write_text("code\n")
            git(root, "add", ".")
            git(root, "commit", "-qm", "code")
            code_head = git(root, "rev-parse", "HEAD")
            (root / "README.md").write_text("documentation\n")
            git(root, "add", ".")
            git(root, "commit", "-qm", "docs")
            latest = git(root, "rev-parse", "HEAD")
            self.assertEqual(
                {
                    key
                    for key, value in self.run_detector(root, verified, latest).items()
                    if value
                },
                set(FLAGS),
            )
            self.assertEqual(
                {
                    key
                    for key, value in self.run_detector(root, code_head, latest).items()
                    if value
                },
                set(),
            )

    def test_non_ancestor_verified_base_falls_back_to_full(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.init_repo(root)
            base = git(root, "rev-parse", "HEAD")
            git(root, "checkout", "-qb", "other")
            (root / "README.md").write_text("other branch\n")
            git(root, "add", ".")
            git(root, "commit", "-qm", "other")
            other = git(root, "rev-parse", "HEAD")
            git(root, "checkout", "-q", "master")
            (root / "README.md").write_text("docs only\n")
            git(root, "add", ".")
            git(root, "commit", "-qm", "docs")
            self.assertNotEqual(base, other)
            latest = git(root, "rev-parse", "HEAD")
            self.assertEqual(
                {
                    key
                    for key, value in self.run_detector(root, other, latest).items()
                    if value
                },
                set(FLAGS),
            )

    def test_pull_request_uses_merge_base_not_last_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.init_repo(root)
            base = git(root, "rev-parse", "HEAD")
            git(root, "checkout", "-qb", "feature")
            source = root / "Sources/Example.swift"
            source.parent.mkdir()
            source.write_text("code\n")
            git(root, "add", ".")
            git(root, "commit", "-qm", "code")
            (root / "README.md").write_text("docs\n")
            git(root, "add", ".")
            git(root, "commit", "-qm", "docs")
            actual = self.run_detector(
                root, base, git(root, "rev-parse", "HEAD"), event="pull_request"
            )
            self.assertEqual(
                {key for key, value in actual.items() if value}, set(FLAGS)
            )

    def test_source_deletion_keeps_full_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.init_repo(root)
            source = root / "Sources/Example.swift"
            source.parent.mkdir()
            source.write_text("code\n")
            git(root, "add", ".")
            git(root, "commit", "-qm", "code")
            verified = git(root, "rev-parse", "HEAD")
            git(root, "rm", "Sources/Example.swift")
            git(root, "commit", "-qm", "delete")
            actual = self.run_detector(root, verified, git(root, "rev-parse", "HEAD"))
            self.assertEqual(
                {key for key, value in actual.items() if value}, set(FLAGS)
            )

    @staticmethod
    def init_repo(root):
        git(root, "init", "-q")
        git(root, "branch", "-M", "master")
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
            CI_VERIFIED_BASE_SHA=base,
            CI_HEAD_SHA=head,
            GITHUB_OUTPUT=str(output),
        )
        subprocess.run(
            ["bash", str(SCRIPT)], cwd=root, env=env, check=True, capture_output=True
        )
        values = dict(line.split("=", 1) for line in output.read_text().splitlines())
        return {key: values[key] == "true" for key in FLAGS}


if __name__ == "__main__":
    unittest.main()
