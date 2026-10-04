"""Exercise PR image links against real commit trees, independent of the worktree."""

import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pr_images


class PRImageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "PR Image Tests")

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.root), *args], text=True
        ).strip()

    def image_paths(self):
        return [
            self.root / pr_images.snapshot_path(name)
            for _, light, dark in pr_images.PAIRS
            for name in (light, dark)
        ]

    def commit_images(self, count=10):
        for path in self.image_paths()[:count]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"PNG in commit")
        self.git("add", ".")
        self.git("commit", "-qm", "record images")
        return self.git("rev-parse", "HEAD")

    def test_requires_full_sha(self):
        with self.assertRaisesRegex(ValueError, "full 40-character"):
            pr_images.markdown("master", root=self.root)

    def test_links_are_pinned_to_commit_and_labelled_as_baselines(self):
        sha = self.commit_images()
        body = pr_images.markdown(
            sha, "https://github.com/example/actions/runs/1", root=self.root
        )
        self.assertEqual(body.count(f"/evoloom/{sha}/"), 10)
        self.assertIn("committed baseline PNGs", body)
        self.assertIn("image commit as head", body)
        self.assertIn("synthetic merge commit", body)

    def test_worktree_image_does_not_substitute_for_missing_commit_blob(self):
        sha = self.commit_images(count=9)
        missing = self.image_paths()[-1]
        missing.write_bytes(b"uncommitted image")
        with self.assertRaisesRegex(FileNotFoundError, missing.name):
            pr_images.markdown(sha, root=self.root)

    def test_committed_image_is_valid_when_worktree_is_changed_or_deleted(self):
        sha = self.commit_images()
        self.image_paths()[0].unlink()
        self.image_paths()[1].write_bytes(b"different working tree image")
        self.assertEqual(
            pr_images.markdown(sha, root=self.root).count(f"/evoloom/{sha}/"), 10
        )

    def test_unavailable_commit_explains_exact_sha_and_fetch(self):
        missing_sha = "a" * 40
        with self.assertRaisesRegex(
            ValueError, f"{missing_sha}.*fetch that exact commit"
        ):
            pr_images.markdown(missing_sha, root=self.root)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch.object(pr_images, "ROOT", self.root),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
            self.assertRaises(SystemExit) as exit_status,
            patch("sys.argv", ["pr_images.py", "--sha", missing_sha]),
        ):
            pr_images.main()
        self.assertEqual(exit_status.exception.code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn(missing_sha, stderr.getvalue())
        self.assertIn("fetch that exact commit", stderr.getvalue())

    def test_sha_must_identify_a_commit_object(self):
        sha = self.commit_images()
        blob_sha = self.git(
            "rev-parse", f"{sha}:{pr_images.snapshot_path('collection-light')}"
        )
        with self.assertRaisesRegex(ValueError, "not a commit object"):
            pr_images.markdown(blob_sha, root=self.root)

    def test_missing_image_rejects_all_links_before_stdout(self):
        sha = self.commit_images(count=9)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch.object(pr_images, "ROOT", self.root),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
            self.assertRaises(SystemExit) as exit_status,
            patch("sys.argv", ["pr_images.py", "--sha", sha]),
        ):
            pr_images.main()
        self.assertEqual(exit_status.exception.code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn(sha, stderr.getvalue())
        self.assertIn(self.image_paths()[-1].name, stderr.getvalue())

    def test_extra_case_checks_commit_blob_even_if_worktree_has_image(self):
        sha = self.commit_images()
        path = self.root / pr_images.snapshot_path("review-settings-error")
        path.write_bytes(b"not committed")
        with self.assertRaisesRegex(FileNotFoundError, path.name):
            pr_images.markdown(
                sha, root=self.root, extra_cases=["review-settings-error"]
            )

    def test_extra_case_link_is_pinned_and_survives_worktree_deletion(self):
        self.commit_images()
        path = self.root / pr_images.snapshot_path("review-settings-error")
        path.write_bytes(b"committed PNG")
        self.git("add", ".")
        self.git("commit", "-qm", "record error state")
        sha = self.git("rev-parse", "HEAD")
        path.unlink()
        body = pr_images.markdown(
            sha, root=self.root, extra_cases=["review-settings-error"]
        )
        self.assertIn(
            f"/evoloom/{sha}/{pr_images.snapshot_path('review-settings-error')}", body
        )
        self.assertIn("Settings · validation error baseline", body)


if __name__ == "__main__":
    unittest.main()
