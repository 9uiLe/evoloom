import tempfile
import unittest
from pathlib import Path

from compare_host_images import compare, record
from PIL import Image


class HostedImageComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.baseline = self.root / "baseline.png"
        self.rendered = self.root / "rendered"
        self.rendered.mkdir()
        self.actual = self.rendered / "components.collection-light.png"
        self.differences = self.root / "diffs"
        self.report = self.root / "report.json"
        self.cases = {"collection-light": self.baseline}
        self.image(self.baseline, (10, 20, 30, 255))
        self.image(self.actual, (10, 20, 30, 255))

    @staticmethod
    def image(path, color, size=(2, 2)):
        Image.new("RGBA", size, color).save(path)

    def compare(self):
        return compare(
            self.cases,
            self.rendered,
            self.differences,
            self.report,
            {self.actual.name},
        )

    def test_matching_rgba_pixels_pass_even_if_png_encoding_differs(self):
        Image.new("RGB", (2, 2), (10, 20, 30)).save(self.actual)
        self.assertTrue(self.compare()["passed"])

    def test_pixel_difference_writes_three_images_without_changing_baseline(self):
        before = self.baseline.read_bytes()
        self.image(self.actual, (11, 20, 30, 255))
        result = self.compare()
        self.assertFalse(result["passed"])
        self.assertEqual(result["cases"][0]["status"], "pixel_mismatch")
        for name in ("expected", "actual", "diff"):
            self.assertTrue(
                (self.differences / "collection-light" / f"{name}.png").is_file()
            )
        self.assertEqual(self.baseline.read_bytes(), before)

    def test_dimension_difference_is_a_failure(self):
        self.image(self.actual, (10, 20, 30, 255), (3, 2))
        self.assertEqual(self.compare()["cases"][0]["status"], "dimension_mismatch")

    def test_missing_or_invalid_images_and_extra_case_fail(self):
        self.actual.unlink()
        self.assertEqual(self.compare()["cases"][0]["status"], "missing_actual")
        self.actual.write_bytes(b"not a png")
        self.assertEqual(self.compare()["cases"][0]["status"], "invalid_image")
        self.image(self.actual, (10, 20, 30, 255))
        self.baseline.unlink()
        self.assertEqual(self.compare()["cases"][0]["status"], "missing_baseline")
        self.image(self.baseline, (10, 20, 30, 255))
        self.image(self.rendered / "components.unknown.png", (1, 2, 3, 255))
        self.assertEqual(self.compare()["cases"][-1]["status"], "unexpected_actual")

    def test_record_requires_all_actuals_and_is_explicit(self):
        self.actual.unlink()
        with self.assertRaisesRegex(RuntimeError, "missing hosted images"):
            record(self.cases, self.rendered)
        self.image(self.actual, (11, 20, 30, 255))
        record(self.cases, self.rendered)
        self.assertTrue(self.compare()["passed"])


if __name__ == "__main__":
    unittest.main()
