"""Check reachability decisions without starting a Simulator for every case."""

import tempfile
import unittest
from pathlib import Path

from sim_use_detail_button import (
    dismiss_keyboard_if_visible,
    reach_save,
    save_reachable,
)
from sim_use_session import APP_ID


def screen_with_save(frame=None, disabled=False):
    entries = [
        {
            "role": "TextArea",
            "label": "Notes",
            "frame": {"x": 20, "y": 463, "width": 362, "height": 105},
        }
    ]
    if frame is not None:
        entries.append(
            {
                "role": "Button",
                "label": "Save project",
                "frame": frame,
                "states": ["disabled"] if disabled else [],
            }
        )
    return {"screen": {"x": 0, "y": 0, "width": 402, "height": 874}, "entries": entries}


VISIBLE = {"x": 16, "y": 618, "width": 126, "height": 44}


class FakeReview:
    prefix = "detail"

    def __init__(self, directory, subsequent=(), hit_label="Save project"):
        self.directory = directory
        self.subsequent = iter(subsequent)
        self.hit_label = hit_label
        self.swipes = 0

    def entry(self, data, role, label):
        return next(
            item
            for item in data["entries"]
            if item["role"] == role and item["label"] == label
        )

    def sim(self, command, *args):
        if command == "swipe":
            self.swipes += 1
            return {}
        self.assert_point(args)
        return {
            "appPackage": APP_ID,
            "entries": [{"role": "Button", "label": self.hit_label}],
        }

    @staticmethod
    def assert_point(args):
        if args[0] != "--point":
            raise AssertionError(f"Unexpected sim-use command: {args}")

    def ui(self, _name):
        return next(self.subsequent)


class SaveReachabilityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def test_initially_visible_button_needs_no_scroll(self):
        review = FakeReview(self.directory)
        initial = screen_with_save(VISIBLE)
        self.assertIs(reach_save(review, initial, "initial"), initial)
        self.assertEqual(review.swipes, 0)
        self.assertTrue((self.directory / "detail-initial-0-hit.ui.json").is_file())

    def test_button_outside_viewport_becomes_reachable_after_outer_scroll(self):
        review = FakeReview(self.directory, subsequent=[screen_with_save(VISIBLE)])
        reached = reach_save(
            review,
            screen_with_save({**VISIBLE, "y": 830}),
            "after-keyboard",
        )
        self.assertEqual(reached["entries"][-1]["frame"], VISIBLE)
        self.assertEqual(review.swipes, 1)

    def test_top_left_and_right_overflow_are_not_reachable(self):
        review = FakeReview(self.directory)
        for frame in (
            {**VISIBLE, "y": -1},
            {**VISIBLE, "x": -1},
            {**VISIBLE, "x": 300},
        ):
            with self.subTest(frame=frame):
                self.assertFalse(
                    save_reachable(review, screen_with_save(frame), "edge")
                )

    def test_obscured_or_missing_button_fails_after_bounded_scroll(self):
        review = FakeReview(
            self.directory,
            subsequent=[screen_with_save(VISIBLE), screen_with_save(VISIBLE)],
            hit_label="Keyboard",
        )
        with self.assertRaisesRegex(AssertionError, "outside the screen or obscured"):
            reach_save(review, screen_with_save(VISIBLE), "obscured")
        self.assertEqual(review.swipes, 2)

    def test_disabled_button_is_not_accepted(self):
        review = FakeReview(self.directory)
        with self.assertRaisesRegex(AssertionError, "disabled"):
            reach_save(review, screen_with_save(VISIBLE, disabled=True), "disabled")

    def test_keyboard_dismissal_only_sends_escape_when_visible(self):
        class KeyboardReview:
            def __init__(self, visible):
                self.visible = visible
                self.calls = []

            def sim(self, *args):
                self.calls.append(args)
                return {"visible": self.visible}

            def keyboard(self, visible):
                self.calls.append(("confirm", visible))
                return True

        hidden = KeyboardReview(False)
        dismiss_keyboard_if_visible(hidden)
        self.assertEqual(hidden.calls, [("keyboard-state",)])
        visible = KeyboardReview(True)
        dismiss_keyboard_if_visible(visible)
        self.assertEqual(
            visible.calls,
            [("keyboard-state",), ("ios", "key", "41"), ("confirm", False)],
        )


if __name__ == "__main__":
    unittest.main()
