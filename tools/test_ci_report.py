import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import ci_report


class CIReportComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "tools").mkdir()
        (self.root / "tools/snapshots.json").write_text(json.dumps(["baseline.png"]))
        self.results = self.root / "TestResults"
        self.results.mkdir()

    def report(self):
        with (
            patch.object(ci_report, "ROOT", self.root),
            patch.object(ci_report, "RESULTS", self.results),
            patch.dict("os.environ", {"EVOLOOM_SNAPSHOT_SELECTED": "true"}),
        ):
            ci_report.report()
        return json.loads((self.results / "ci-report.json").read_text())

    def test_capture_success_and_image_failure_are_separate(self):
        (self.results / "metrics.jsonl").write_text(
            json.dumps(
                {
                    "phase": "xcode",
                    "scheme": "EvoloomReviewHost",
                    "action": "test",
                    "result": "passed",
                    "seconds": 20,
                }
            )
            + "\n"
        )
        (self.results / "host-image-comparison.json").write_text(
            json.dumps(
                {
                    "passed": False,
                    "cases": [{"case": "collection-light", "status": "pixel_mismatch"}],
                }
            )
        )
        report = self.report()
        self.assertEqual(report["host_capture_xcode"], "passed")
        self.assertFalse(report["host_image_comparison"]["passed"])

    def test_missing_comparison_report_is_not_success(self):
        report = self.report()
        self.assertIn("error", report["host_image_comparison"])


if __name__ == "__main__":
    unittest.main()
