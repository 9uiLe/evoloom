import unittest

from verified_base import is_full_validation


class VerifiedBaseTests(unittest.TestCase):
    def test_legacy_documentation_run_is_not_a_full_validation(self):
        jobs = [
            {
                "name": "ios",
                "conclusion": "success",
                "steps": [{"name": "Compare iOS snapshots", "conclusion": "skipped"}],
            }
        ]
        self.assertFalse(is_full_validation(jobs))

    def test_legacy_full_run_requires_each_test_step(self):
        steps = [
            {"name": name, "conclusion": "success"}
            for name in (
                "Run Package unit tests",
                "Verify copied source Package",
                "Compare iOS snapshots",
            )
        ]
        self.assertTrue(
            is_full_validation(
                [{"name": "ios", "conclusion": "success", "steps": steps}]
            )
        )
        steps[-1]["conclusion"] = "skipped"
        self.assertFalse(
            is_full_validation(
                [{"name": "ios", "conclusion": "success", "steps": steps}]
            )
        )

    def test_new_full_marker_requires_success(self):
        full = {
            "name": "validation",
            "conclusion": "success",
            "steps": [{"name": "Mark full validation", "conclusion": "success"}],
        }
        self.assertTrue(is_full_validation([full]))
        full["conclusion"] = "cancelled"
        self.assertFalse(is_full_validation([full]))
        full["conclusion"] = "success"
        full["steps"][0]["conclusion"] = "skipped"
        self.assertFalse(is_full_validation([full]))


if __name__ == "__main__":
    unittest.main()
