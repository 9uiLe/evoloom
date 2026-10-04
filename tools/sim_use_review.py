"""Exercise the development host on the pinned simulator with sim-use."""

import argparse
import json
import os
import shutil
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from tasks import ROOT, apple_env, doctor, run_host

APP_ID = "dev.evoloom.reviewhost"
ERROR_EN = "Enter a valid email address before saving."


class Review:
    def __init__(self, device: str, directory: Path):
        self.device = device
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=False)
        self.log = self.directory / "actions.jsonl"
        self.failures: list[str] = []
        self.prefix = "setup"

    def command(self, *args: str, timeout: int = 30) -> str:
        started = time.monotonic()
        try:
            result = subprocess.run(
                args,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=apple_env() if args[0] == "xcrun" else None,
            )
        except subprocess.TimeoutExpired as error:
            self.write_event(args, time.monotonic() - started, "timeout", str(error))
            raise RuntimeError(f"Timed out: {args}") from error
        self.write_event(
            args,
            time.monotonic() - started,
            result.returncode,
            result.stdout,
            result.stderr,
        )
        if result.returncode:
            raise RuntimeError(
                f"Command failed ({result.returncode}): {args}\n{result.stderr}\n{result.stdout}"
            )
        return result.stdout.strip()

    def write_event(
        self,
        args: tuple[str, ...],
        elapsed: float,
        status: object,
        output: str,
        error: str = "",
    ) -> None:
        event = {
            "time": datetime.now(UTC).isoformat(),
            "argv": args,
            "seconds": round(elapsed, 3),
            "status": status,
            "stdout": output
            if args[:2] != ("sim-use", "ui")
            else "Saved separately as *.ui.json",
            "stderr": error,
        }
        with self.log.open("a") as file:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")

    def sim(self, *args: str) -> dict:
        output = self.command("sim-use", *args, "--device", self.device, "--json")
        result = json.loads(output)
        if not result.get("ok"):
            raise RuntimeError(f"sim-use rejected {args}: {result}")
        return result["data"]

    def ui(self, name: str) -> dict:
        data = self.sim("ui")
        (self.directory / f"{self.prefix}-{name}.ui.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        )
        return data

    def await_ui(self, name: str, predicate, seconds: float = 12) -> dict:
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            data = self.ui(name)
            if data.get("appPackage") == APP_ID and predicate(data):
                return data
            time.sleep(0.25)
        raise AssertionError(f"Expected UI did not appear in {seconds}s: {name}")

    def entry(self, data: dict, role: str, label: str) -> dict:
        matches = [
            item
            for item in data["entries"]
            if item["role"] == role and item.get("label") == label
        ]
        if len(matches) != 1:
            raise AssertionError(f"Expected one {role} {label!r}, found {len(matches)}")
        return matches[0]

    def keyboard(self, visible: bool) -> bool:
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            if self.sim("keyboard-state")["visible"] == visible:
                return True
            time.sleep(0.25)
        self.failures.append(
            f"{self.prefix}: Software keyboard visible={visible} was not observed"
        )
        return False

    def screenshot(self, name: str) -> None:
        self.sim(
            "screenshot", "--output", str(self.directory / f"{self.prefix}-{name}.png")
        )

    def launch(self, screen: str, appearance: str = "light") -> dict:
        self.command("xcrun", "simctl", "ui", self.device, "appearance", appearance)
        args = [
            "xcrun",
            "simctl",
            "launch",
            "--terminate-running-process",
            self.device,
            APP_ID,
            f"--screen={screen}",
        ]
        if appearance == "dark":
            args.append("--dark")
        self.command(*args)
        title = (
            "設定"
            if "Japanese" in screen
            else "Settings"
            if screen.startswith("settings")
            else "Title"
        )
        return self.await_ui(
            f"{screen}-{appearance}-initial",
            lambda data: any(item.get("label") == title for item in data["entries"]),
        )

    def tap_field(self, label: str) -> dict:
        self.sim(
            "tap",
            "--label",
            label,
            "--element-type",
            "TextField",
            "--wait-timeout",
            "8",
        )
        return self.ui(f"focused-{label.lower().replace(' ', '-')}")

    def replace_text(self, label: str, value: str) -> dict:
        data = self.ui(f"before-replace-{label.lower().replace(' ', '-')}")
        field = self.entry(data, "TextField", label)
        if self.sim("keyboard-state")["visible"]:
            frame = field["frame"]
            # Long-press near the text. Short error values occupy only the leading edge.
            x = round(frame["x"] + (25 if len(field.get("value", "")) < 10 else 148))
            y = round(frame["y"] + frame["height"] / 2)
            self.sim(
                "paste",
                value,
                "--replace",
                "--via-menu",
                "--target-x",
                str(x),
                "--target-y",
                str(y),
            )
            menu = self.await_ui(
                "paste-result",
                lambda current: any(
                    item.get("label") == "Paste"
                    or (
                        item["role"] == "TextField"
                        and item.get("label") == label
                        and item.get("value") == value
                    )
                    for item in current["entries"]
                ),
                seconds=3,
            )
            if any(item.get("label") == "Paste" for item in menu["entries"]):
                self.entry(menu, "StaticText", "Paste")
                self.sim("tap", "--label", "Paste", "--element-type", "StaticText")
        else:
            self.sim("paste", value, "--replace")
        return self.await_ui(
            f"replaced-{label.lower().replace(' ', '-')}",
            lambda current: any(
                item["role"] == "TextField"
                and item.get("label") == label
                and item.get("value") == value
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
        normal = self.ui("normal-light")
        self.entry(normal, "TextField", "Display name")
        self.assert_save(normal, disabled=False)
        self.screenshot("normal-light")
        self.tap_field("Display name")
        self.keyboard(True)
        self.screenshot("display-name-focused-keyboard")
        self.replace_text("Display name", "Evoloom review")
        self.tap_field("Email")
        self.keyboard(True)
        self.screenshot("email-focused-keyboard")
        self.replace_text("Email", "new@example.com")
        self.toggle("0")
        self.toggle("1")

    def error_form(self) -> None:
        error = self.launch("settingsError")
        self.entry(error, "StaticText", ERROR_EN)
        self.assert_save(error, disabled=True)
        workspace = self.entry(error, "TextField", "Workspace")
        if "disabled" not in workspace["states"] or workspace["value"] != "Field notes":
            raise AssertionError("Workspace must retain its disabled value")
        self.screenshot("error-disabled")
        self.tap_field("Workspace")
        self.keyboard(False)
        self.tap_field("Email")
        self.keyboard(True)
        corrected = self.replace_text("Email", "valid@example.com")
        if any(item.get("label") == ERROR_EN for item in corrected["entries"]):
            raise AssertionError("Error remained after valid fixture input")
        self.screenshot("error-corrected-keyboard")
        # Escape dismisses the native keyboard; no Save action is invoked here.
        self.sim("ios", "key", "41")
        self.keyboard(False)
        corrected = self.ui("error-corrected-save")
        self.assert_save(corrected, disabled=False)
        self.screenshot("error-corrected-save")

        self.tap_field("Email")
        self.replace_text("Email", "invalid")
        invalid = self.await_ui(
            "error-returned",
            lambda data: any(item.get("label") == ERROR_EN for item in data["entries"]),
        )
        if "@" in self.entry(invalid, "TextField", "Email")["value"]:
            raise AssertionError("Email did not return to an invalid value")
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
            initial = self.launch("settings")
            self.entry(initial, "TextField", "Email")
            self.screenshot("large-initial")
            focused = self.tap_field("Email")
            keyboard_visible = self.keyboard(True)
            self.screenshot("large-email-focused")
            self.sim("gesture", "scroll-up")
            scrolled = self.ui("large-after-scroll")
            before_y = self.entry(focused, "TextField", "Email")["frame"]["y"]
            after_y = self.entry(scrolled, "TextField", "Email")["frame"]["y"]
            if after_y >= before_y:
                raise AssertionError(
                    "Form did not move upward after the scroll gesture"
                )
            if keyboard_visible:
                self.keyboard(True)
            self.screenshot("large-after-scroll")
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
        japanese = self.launch("settingsJapaneseError")
        self.entry(japanese, "TextField", "チーム全員に表示する名前")
        self.entry(
            japanese,
            "StaticText",
            "保存する前に、有効なメールアドレスを入力してください。",
        )
        self.screenshot("japanese-error")
        dark = self.launch("settingsError", "dark")
        self.entry(dark, "TextField", "Workspace")
        self.assert_save(dark, disabled=True)
        self.screenshot("dark-error")
        self.tap_field("Email")
        self.screenshot("dark-error-focused")

    def outlined(self) -> None:
        detail = self.launch("detail")
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
    review = Review(device, directory)
    (directory / "environment.json").write_text(
        json.dumps(
            {
                "device": device,
                "head": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], text=True
                ).strip(),
                "working_tree_dirty": bool(
                    subprocess.check_output(
                        ["git", "status", "--porcelain"], text=True
                    ).strip()
                ),
                "xcode": subprocess.check_output(
                    ["xcodebuild", "-version"], text=True
                ).strip(),
                "sim_use": subprocess.check_output(
                    ["sim-use", "--version"], text=True
                ).strip(),
                "sim_use_binary": shutil.which("sim-use"),
                "content_size": subprocess.check_output(
                    ["xcrun", "simctl", "ui", device, "content_size"], text=True
                ).strip(),
                "simulator_languages": subprocess.check_output(
                    [
                        "xcrun",
                        "simctl",
                        "spawn",
                        device,
                        "defaults",
                        "read",
                        "-g",
                        "AppleLanguages",
                    ],
                    text=True,
                ).strip(),
                "runtime": "iOS 27.0 (24A434)",
                "device_name": "iPhone 18 Pro",
                "scene_points": "402 x 874; app window safe area is managed by iOS",
                "fixture_locale": "ja_JP for settingsJapanese routes; otherwise system locale",
            },
            indent=2,
        )
        + "\n"
    )
    os.environ.update(
        EVOLOOM_SCREEN="settings", EVOLOOM_STATE="normal", EVOLOOM_APPEARANCE="light"
    )
    try:
        if args.reuse_built_host:
            review.launch("settings")
        else:
            run_host()
        review.await_ui(
            "host-ready",
            lambda data: any(
                item.get("label") == "Settings" for item in data["entries"]
            ),
        )
        scenarios = {
            "normal": review.normal_form,
            "error": review.error_form,
            "large": review.large_text,
            "japanese-dark": review.japanese_and_dark,
            "outlined": review.outlined,
        }
        selected = list(scenarios) if args.scenario == "all" else [args.scenario]
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
