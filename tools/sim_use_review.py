"""Exercise the Settings development host on the pinned simulator with sim-use."""

import argparse
import os
from datetime import UTC, datetime
from pathlib import Path

from sim_use_session import SimUseSession, install_existing_host, record_environment
from tasks import ROOT, doctor, run_host

ERROR_EN = "Enter a valid email address before saving."


class SettingsReview(SimUseSession):
    def tap_field(self, label: str) -> dict:
        observed = self.ui(f"before-focus-{label.lower().replace(' ', '-')}")
        frame = self.entry(observed, "TextField", label)["frame"]
        self.sim(
            "tap",
            "--point",
            f"{round(frame['x'] + frame['width'] / 2)},{round(frame['y'] + frame['height'] / 2)}",
        )
        self.sim("keyboard-state")
        return self.ui(f"focused-{label.lower().replace(' ', '-')}")

    def append_text(self, label: str, suffix: str) -> dict:
        data = self.ui(f"before-edit-{label.lower().replace(' ', '-')}")
        field = self.entry(data, "TextField", label)
        expected = field["value"] + suffix
        self.sim("type", suffix)
        return self.await_ui(
            f"edited-{label.lower().replace(' ', '-')}",
            lambda current: any(
                item["role"] == "TextField"
                and item.get("label") == label
                and item.get("value") == expected
                for item in current["entries"]
            ),
        )

    def assert_save(self, data: dict, disabled: bool) -> None:
        button = self.entry(data, "Button", "Save settings")
        if ("disabled" in button["states"]) != disabled:
            raise AssertionError(
                f"Save disabled={disabled} expected, got {button['states']}"
            )

    def toggle(self, expected: str) -> None:
        data = self.ui("before-toggle")
        item = self.entry(
            data, "CheckBox", "Project updates, Receive changes on this device."
        )
        frame = item["frame"]
        # The AX frame spans the whole Form row; the native switch is on its trailing edge.
        self.sim(
            "tap",
            "--point",
            f"{round(frame['x'] + frame['width'] - 35)},{round(frame['y'] + frame['height'] / 2)}",
            "--duration",
            "0.05",
        )
        self.await_ui(
            "after-toggle",
            lambda current: (
                self.entry(
                    current,
                    "CheckBox",
                    "Project updates, Receive changes on this device.",
                ).get("value")
                == expected
            ),
        )

    def normal_form(self) -> None:
        normal = self.launch("settings", "Settings")
        self.screenshot("normal-light")
        self.entry(normal, "TextField", "Display name")
        self.assert_save(normal, disabled=False)
        self.tap_field("Display name")
        self.screenshot("display-name-focused")
        self.tap_field("Email")
        self.screenshot("email-focused")
        self.tap_field("Display name")
        self.append_text("Display name", "X")
        self.tap_field("Email")
        self.append_text("Email", "x")
        self.toggle("0")
        self.toggle("1")

    def error_form(self) -> None:
        error = self.launch("settingsError", "Settings")
        self.entry(error, "StaticText", ERROR_EN)
        self.assert_save(error, disabled=True)
        workspace = self.entry(error, "TextField", "Workspace")
        if "disabled" not in workspace["states"] or workspace["value"] != "Field notes":
            raise AssertionError("Workspace must retain its disabled value")
        self.screenshot("error-disabled")
        self.tap_field("Workspace")
        self.keyboard(False)
        self.tap_field("Email")
        self.sim("type", "@example.com")
        self.ui("error-after-type")
        self.screenshot("error-after-type")
        corrected = self.await_ui(
            "error-corrected",
            lambda data: (
                self.entry(data, "TextField", "Email")["value"].startswith("invalid@")
                and not any(item.get("label") == ERROR_EN for item in data["entries"])
            ),
        )
        if any(item.get("label") == ERROR_EN for item in corrected["entries"]):
            raise AssertionError("Error remained after valid fixture input")
        self.assert_save(corrected, disabled=False)
        self.screenshot("error-corrected")
        # The email keyboard may insert an extra @; remove the observed suffix.
        appended = len(self.entry(corrected, "TextField", "Email")["value"]) - len(
            "invalid"
        )
        self.sim("ios", "key-sequence", "--keycodes", ",".join(["42"] * appended))
        invalid = self.await_ui(
            "error-returned",
            lambda data: any(item.get("label") == ERROR_EN for item in data["entries"]),
        )
        if self.entry(invalid, "TextField", "Email")["value"] != "invalid":
            raise AssertionError("Email did not return to the initial invalid value")
        self.assert_save(invalid, disabled=True)
        self.screenshot("error-returned")

    def large_text(self) -> None:
        original_size = self.command(
            "xcrun", "simctl", "ui", self.device, "content_size"
        )
        try:
            self.command(
                "xcrun",
                "simctl",
                "ui",
                self.device,
                "content_size",
                "accessibility-medium",
            )
            if (
                self.command("xcrun", "simctl", "ui", self.device, "content_size")
                != "accessibility-medium"
            ):
                raise AssertionError("Simulator did not adopt accessibility-medium")
            initial = self.launch("settings", "Settings")
            self.entry(initial, "TextField", "Email")
            self.screenshot("large-initial")
            focused = self.tap_field("Email")
            keyboard_visible = self.keyboard(True)
            self.screenshot("large-email-focused")
            # Keep the swipe inside the Form above the software keyboard.
            self.sim(
                "swipe",
                "--from",
                "200,500",
                "--to",
                "200,220",
                "--coordinate-space",
                "ui",
            )
            scrolled = self.ui("large-after-scroll")
            self.screenshot("large-after-scroll")
            before_y = self.entry(focused, "TextField", "Email")["frame"]["y"]
            after_y = self.entry(scrolled, "TextField", "Email")["frame"]["y"]
            if after_y >= before_y:
                raise AssertionError(
                    "Form did not move upward after the scroll gesture"
                )
            if keyboard_visible:
                self.keyboard(True)
            if keyboard_visible:
                self.sim("ios", "key", "41")
                self.keyboard(False)
            reached = self.await_ui(
                "large-save-reached",
                lambda data: any(
                    item["role"] == "Button"
                    and item.get("label") == "Save settings"
                    and item["frame"]["y"] + item["frame"]["height"]
                    <= data["screen"]["height"] - 34
                    for item in data["entries"]
                ),
            )
            self.assert_save(reached, disabled=False)
            self.screenshot("large-save-reached")
        finally:
            self.command(
                "xcrun", "simctl", "ui", self.device, "content_size", original_size
            )

    def japanese_and_dark(self) -> None:
        japanese = self.launch("settingsJapaneseError", "設定")
        self.entry(japanese, "TextField", "チーム全員に表示する名前")
        self.entry(
            japanese,
            "StaticText",
            "保存する前に、有効なメールアドレスを入力してください。",
        )
        self.screenshot("japanese-error")
        dark = self.launch("settingsError", "Settings", "dark")
        self.entry(dark, "TextField", "Workspace")
        self.assert_save(dark, disabled=True)
        self.screenshot("dark-error")
        self.tap_field("Email")
        self.screenshot("dark-error-focused")

    def outlined(self) -> None:
        detail = self.launch("detail", "Title")
        field = self.entry(detail, "TextField", "Title")
        before = field["value"]
        self.screenshot("outlined-initial")
        self.tap_field("Title")
        self.sim("type", "X")
        changed = self.await_ui(
            "outlined-edited",
            lambda data: self.entry(data, "TextField", "Title").get("value") != before,
        )
        self.entry(changed, "TextField", "Title")
        self.screenshot("outlined-edited")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--reuse-built-host",
        action="store_true",
        help="Use the app already installed on the fixed simulator",
    )
    parser.add_argument(
        "--scenario",
        choices=["all", "normal", "error", "large", "japanese-dark", "outlined"],
        default="all",
    )
    args = parser.parse_args()
    device = doctor()
    directory = args.output or ROOT / "TestResults/SimUse" / datetime.now(UTC).strftime(
        "%Y%m%dT%H%M%SZ"
    )
    review = SettingsReview(device, directory)
    os.environ.update(
        EVOLOOM_SCREEN="settings", EVOLOOM_STATE="normal", EVOLOOM_APPEARANCE="light"
    )
    try:
        if args.reuse_built_host:
            install_existing_host(review)
            record_environment(directory, device)
            review.launch("settings", "Settings")
        else:
            run_host()
            record_environment(directory, device)
        review.await_ui(
            "host-ready",
            lambda data: any(
                item.get("label") == "Settings" for item in data["entries"]
            ),
        )
        scenarios = {
            "large": review.large_text,
            "normal": review.normal_form,
            "error": review.error_form,
            "japanese-dark": review.japanese_and_dark,
            "outlined": review.outlined,
        }
        selected = (
            ["large", "normal", "japanese-dark", "error"]
            if args.scenario == "all"
            else [args.scenario]
        )
        for name in selected:
            review.prefix = name
            prior_failures = len(review.failures)
            try:
                scenarios[name]()
                state = (
                    "completed" if len(review.failures) == prior_failures else "failed"
                )
                print(f"{name}: {state}", flush=True)
            except (AssertionError, RuntimeError) as error:
                review.failures.append(f"{name}: {type(error).__name__}: {error}")
                print(
                    f"{name}: failed; continuing to collect other evidence", flush=True
                )
        if review.failures:
            raise AssertionError("; ".join(review.failures))
    except Exception as error:
        (directory / "failure.txt").write_text(f"{type(error).__name__}: {error}\n")
        print(f"Interaction review failed; evidence: {directory}")
        raise
    print(f"Interaction review passed; evidence: {directory}")


if __name__ == "__main__":
    main()
