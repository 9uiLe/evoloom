"""Shared pinned-Simulator command, observation and evidence session."""

import json
import shutil
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from tasks import HOST_APP, apple_env, prepare_simulator

APP_ID = "dev.evoloom.reviewhost"


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
        deadline = time.monotonic() + seconds
        while True:
            data = self.sim("ui")
            self.ui_sequence += 1
            (
                self.directory / f"{self.prefix}-{name}-{self.ui_sequence:03}.ui.json"
            ).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
            screen = data.get("screen", {})
            if screen.get("width", 0) > 0 and screen.get("height", 0) > 0:
                return data
            if time.monotonic() >= deadline:
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
        self.sim(
            "screenshot", "--output", str(self.directory / f"{self.prefix}-{name}.png")
        )

    def launch(self, screen: str, appearance: str = "light") -> dict:
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
        if screen.startswith("settings"):
            title = "設定" if "Japanese" in screen else "Settings"
        elif screen.startswith("detail"):
            title = "タイトル" if "Japanese" in screen else "Title"
        else:
            title = "ボタンの状態" if "Japanese" in screen else "Button states"
        return self.await_ui(
            f"{screen}-{appearance}-initial",
            lambda data: any(item.get("label") == title for item in data["entries"]),
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
