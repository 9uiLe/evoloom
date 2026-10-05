"""Shared pinned-Simulator command, observation and evidence session."""

import json
import os
import shutil
import subprocess
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path

from tasks import HOST_APP, apple_env, prepare_simulator

APP_ID = "dev.evoloom.reviewhost"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class CommandTimeout(RuntimeError):
    """A bounded command ended before returning a result."""


class SimUseSession:
    def __init__(self, device: str, directory: Path):
        self.device = device
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=False)
        self.log = self.directory / "actions.jsonl"
        self.failures: list[str] = []
        self.prefix = "setup"
        self.ui_sequence = 0

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
            self.write_event(
                args,
                time.monotonic() - started,
                "timeout",
                self._text(error.stdout),
                self._text(error.stderr),
            )
            if args[:2] == ("sim-use", "ui"):
                try:
                    self.capture_ui_timeout()
                except (KeyError, OSError, RuntimeError, TypeError, ValueError):
                    try:
                        (self.directory / "ui-timeout-diagnostic-error.txt").write_text(
                            traceback.format_exc()
                        )
                    except OSError:
                        pass
            raise CommandTimeout(f"Timed out: {args}") from error
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

    @staticmethod
    def _text(value: str | bytes | None) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value or ""

    def capture_ui_timeout(self) -> None:
        """Keep independent process, daemon, and display evidence after AX stalls."""
        # Fixed sim-use v0.14.0 keeps its per-UDID daemon log here even when
        # daemon status cannot answer while the UI request is still blocked.
        daemon_log_path = Path(f"/tmp/sim-use-{os.getuid()}/{self.device}.log")
        checks = (
            ("xcrun", "simctl", "spawn", self.device, "launchctl", "list"),
            ("sim-use", "daemon", "status", "--json"),
            (
                "sim-use",
                "app-state",
                "--device",
                self.device,
                "--bundle-id",
                APP_ID,
                "--json",
            ),
        )
        for args in checks:
            try:
                output = self.command(*args, timeout=10)
            except (OSError, RuntimeError):
                continue
            if args[1:3] == ("daemon", "status"):
                try:
                    daemons = json.loads(output)["data"]["daemons"]
                    target = next(
                        (
                            item
                            for item in daemons
                            if item.get("deviceId") == self.device
                        ),
                        None,
                    )
                    if target and target.get("logPath"):
                        daemon_log_path = Path(target["logPath"])
                except (KeyError, TypeError, ValueError, OSError):
                    pass
        try:
            if daemon_log_path.is_file():
                with daemon_log_path.open("rb") as source:
                    source.seek(0, 2)
                    source.seek(max(0, source.tell() - 65536))
                    tail = source.read()
                (self.directory / "sim-use-daemon-tail.log").write_bytes(tail)
        except OSError:
            pass
        screenshot = self.directory / "ui-timeout-display.png"
        screenshot_succeeded = False
        try:
            self.command(
                "xcrun",
                "simctl",
                "io",
                self.device,
                "screenshot",
                str(screenshot),
                timeout=15,
            )
            screenshot_succeeded = True
        except (OSError, RuntimeError):
            pass
        try:
            if screenshot.exists():
                with screenshot.open("rb") as image:
                    valid_png = screenshot_succeeded and image.read(8) == PNG_SIGNATURE
                if not valid_png:
                    screenshot.unlink()
        except OSError:
            pass

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
            if args[:2] != ("sim-use", "ui") or status != 0
            else "Saved separately as *.ui.json",
            "stderr": error,
        }
        with self.log.open("a") as file:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")

    def sim(self, *args: str) -> dict:
        output = self.command(
            "sim-use",
            *args,
            "--device",
            self.device,
            "--json",
            timeout=45 if args[0] == "ui" else 30,
        )
        result = json.loads(output)
        if not result.get("ok"):
            raise RuntimeError(f"sim-use rejected {args}: {result}")
        return result["data"]

    def ui(self, name: str, seconds: float = 8) -> dict:
        deadline = None
        while True:
            data = self.sim("ui")
            self.ui_sequence += 1
            (
                self.directory / f"{self.prefix}-{name}-{self.ui_sequence:03}.ui.json"
            ).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
            screen = data.get("screen", {})
            if screen.get("width", 0) > 0 and screen.get("height", 0) > 0:
                return data
            now = time.monotonic()
            if deadline is None:
                # Start the viewport wait when a zero viewport is observed.
                # A slow first command must not consume the entire wait.
                deadline = now + seconds
            if now >= deadline:
                raise AssertionError(f"Simulator viewport did not become ready: {name}")
            time.sleep(0.25)

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
        image = self.directory / f"{self.prefix}-{name}.png"
        try:
            self.sim("screenshot", "--output", str(image))
        except CommandTimeout:
            # sim-use's streaming screenshot runs in-process even with its
            # daemon enabled. Recover evidence through Apple's fixed device.
            image.unlink(missing_ok=True)
            try:
                self.command(
                    "xcrun",
                    "simctl",
                    "io",
                    self.device,
                    "screenshot",
                    str(image),
                    timeout=30,
                )
                self.require_png(image)
            except (OSError, RuntimeError):
                image.unlink(missing_ok=True)
                raise
            image.with_suffix(".capture.json").write_text(
                json.dumps(
                    {
                        "source": "simctl fallback",
                        "reason": "sim-use screenshot timeout",
                    }
                )
                + "\n"
            )
            return
        self.require_png(image)

    @staticmethod
    def require_png(image: Path) -> None:
        try:
            with image.open("rb") as source:
                valid = source.read(8) == PNG_SIGNATURE
        except OSError:
            valid = False
        if not valid:
            image.unlink(missing_ok=True)
            raise RuntimeError(f"Screenshot missing or invalid PNG: {image}")

    def launch(
        self, screen: str, expected_label: str, appearance: str = "light"
    ) -> dict:
        self.command(
            "xcrun", "simctl", "ui", self.device, "appearance", appearance, timeout=60
        )
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
        return self.await_ui(
            f"{screen}-{appearance}-initial",
            lambda data: any(
                item.get("label") == expected_label for item in data["entries"]
            ),
        )


def record_environment(directory: Path, device: str) -> None:
    languages = subprocess.run(
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
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
        env=apple_env(),
    )
    (directory / "environment.json").write_text(
        json.dumps(
            {
                "device": device,
                "head": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], text=True, timeout=10
                ).strip(),
                "working_tree_dirty": bool(
                    subprocess.check_output(
                        ["git", "status", "--porcelain"], text=True, timeout=10
                    ).strip()
                ),
                "xcode": subprocess.check_output(
                    ["xcodebuild", "-version"], text=True, timeout=30
                ).strip(),
                "sim_use": subprocess.check_output(
                    ["sim-use", "--version"], text=True, timeout=15
                ).strip(),
                "sim_use_binary": shutil.which("sim-use"),
                "content_size": subprocess.check_output(
                    ["xcrun", "simctl", "ui", device, "content_size"],
                    text=True,
                    timeout=60,
                ).strip(),
                "simulator_languages": languages.stdout.strip()
                if languages.returncode == 0
                else f"unavailable: {languages.stderr.strip()}",
                "simulator_languages_status": languages.returncode,
                "runtime": "iOS 27.0 (24A434)",
                "device_name": "iPhone 18 Pro",
                "scene_points": "402 x 874; app window safe area is managed by iOS",
                "fixture_locale": "Japanese fixture routes use Japanese copy; otherwise English copy. Simulator locale is recorded separately.",
            },
            indent=2,
        )
        + "\n"
    )


def install_existing_host(review: SimUseSession) -> None:
    prepare_simulator()
    review.command("xcrun", "simctl", "bootstatus", review.device, "-b", timeout=120)
    if not HOST_APP.is_dir():
        raise RuntimeError(
            f"Built host missing at {HOST_APP}; run just build-host first"
        )
    review.command(
        "xcrun", "simctl", "install", review.device, str(HOST_APP), timeout=120
    )
