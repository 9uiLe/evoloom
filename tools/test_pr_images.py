"""Check that PR image markup stays pinned and refuses missing images."""

import unittest
from unittest.mock import patch

import pr_images


class PRImageTests(unittest.TestCase):
    def test_requires_full_sha(self):
        with self.assertRaisesRegex(ValueError, "full 40-character"):
            pr_images.markdown("master")

    def test_links_use_only_the_requested_commit(self):
        sha = "a" * 40
        with patch.object(pr_images.Path, "is_file", return_value=True):
            body = pr_images.markdown(sha)
        self.assertEqual(body.count(f"/evoloom/{sha}/"), 10)
        self.assertIn("committed baseline PNGs", body)
        self.assertIn("CI comparison: pending", body)

    def test_ci_link_distinguishes_head_from_merge_checkout(self):
        with patch.object(pr_images.Path, "is_file", return_value=True):
            body = pr_images.markdown(
                "a" * 40, "https://github.com/example/actions/runs/1"
            )
        self.assertIn("image commit as head", body)
        self.assertIn("synthetic merge commit", body)


if __name__ == "__main__":
    unittest.main()
