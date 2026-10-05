"""Require a measured viewport before treating a sim-use tree as a screen."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sim_use_session import SimUseSession


class FakeReview(SimUseSession):
    def __init__(self, directory, screens):
        super().__init__("fixed-test-device", directory)
        self.screens = iter(screens)

    def sim(self, command, *args):
        if command != "ui" or args:
            raise AssertionError(f"Unexpected command: {command} {args}")
        return {"screen": next(self.screens), "entries": []}


class ViewportReadinessTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_waits_for_nonzero_screen_and_keeps_both_observations(self):
        review = FakeReview(
            self.root / "ready",
            [{"width": 0, "height": 0}, {"width": 402, "height": 874}],
        )
        self.assertEqual(review.ui("launch")["screen"]["width"], 402)
        self.assertEqual(len(list(review.directory.glob("*.ui.json"))), 2)

    def test_zero_viewport_fails_with_bounded_wait(self):
        review = FakeReview(self.root / "unready", [{"width": 0, "height": 0}])
        with self.assertRaisesRegex(AssertionError, "viewport did not become ready"):
            review.ui("launch", seconds=0)
        self.assertEqual(len(list(review.directory.glob("*.ui.json"))), 1)

    def test_slow_first_zero_viewport_gets_its_own_readiness_window(self):
        review = FakeReview(self.root / "slow-first", [])
        clock = [0.0]
        observations = iter(
            [
                (12.0, {"screen": {"width": 0, "height": 0}, "entries": []}),
                (13.0, {"screen": {"width": 402, "height": 874}, "entries": []}),
            ]
        )

        def observe(command):
            self.assertEqual(command, "ui")
            clock[0], data = next(observations)
            return data

        with (
            patch.object(review, "sim", side_effect=observe),
            patch("sim_use_session.time.monotonic", side_effect=lambda: clock[0]),
            patch("sim_use_session.time.sleep"),
        ):
            self.assertEqual(review.ui("launch")["screen"]["width"], 402)
        self.assertEqual(len(list(review.directory.glob("*.ui.json"))), 2)

    def test_zero_viewport_still_fails_after_observed_window(self):
        review = FakeReview(self.root / "slow-unready", [])
        clock = [0.0]
        observations = iter([12.0, 21.0])

        def observe(command):
            self.assertEqual(command, "ui")
            clock[0] = next(observations)
            return {"screen": {"width": 0, "height": 0}, "entries": []}

        with (
            patch.object(review, "sim", side_effect=observe),
            patch("sim_use_session.time.monotonic", side_effect=lambda: clock[0]),
            patch("sim_use_session.time.sleep"),
            self.assertRaisesRegex(AssertionError, "viewport did not become ready"),
        ):
            review.ui("launch")
        self.assertEqual(len(list(review.directory.glob("*.ui.json"))), 2)


if __name__ == "__main__":
    unittest.main()
