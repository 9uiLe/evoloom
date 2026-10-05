"""Shared sim-use evidence and fixed-device boundaries."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sim_use_session import PNG_SIGNATURE, SimUseSession, install_existing_host


class SessionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.session = SimUseSession("fixed-device", Path(temporary.name) / "run")

    def events(self):
        return [json.loads(line) for line in self.session.log.read_text().splitlines()]

    def test_ui_uses_fixed_device_and_returns_observation(self):
        observed = {"ok": True, "data": {"appPackage": "dev.evoloom.reviewhost"}}
        with patch.object(
            self.session, "command", return_value=json.dumps(observed)
        ) as command:
            self.assertEqual(self.session.sim("ui"), observed["data"])
        command.assert_called_once_with(
            "sim-use", "ui", "--device", "fixed-device", "--json", timeout=45
        )

    def test_action_uses_fixed_device_and_action_timeout(self):
        with patch.object(
            self.session, "command", return_value='{"ok": true, "data": {}}'
        ) as command:
            self.session.sim("tap", "--point", "20,30")
        command.assert_called_once_with(
            "sim-use",
            "tap",
            "--point",
            "20,30",
            "--device",
            "fixed-device",
            "--json",
            timeout=30,
        )

    def test_sim_use_commands_use_pinned_tool_without_reused_daemon(self):
        result = subprocess.CompletedProcess(("sim-use", "ui"), 0, "ready", "")
        with patch("sim_use_session.subprocess.run", return_value=result) as run:
            self.assertEqual(self.session.command("sim-use", "ui"), "ready")
        self.assertEqual(run.call_args.kwargs["env"]["SIM_USE_NO_DAEMON"], "1")

    def test_command_failure_records_status_and_output(self):
        result = subprocess.CompletedProcess(
            ("sim-use", "tap"), 7, "partial", "failure"
        )
        with (
            patch("sim_use_session.subprocess.run", return_value=result),
            self.assertRaisesRegex(RuntimeError, "Command failed \\(7\\)"),
        ):
            self.session.command("sim-use", "tap")
        event = self.events()[0]
        self.assertEqual(
            (event["status"], event["stdout"], event["stderr"]),
            (7, "partial", "failure"),
        )

    def test_command_timeout_records_failure_without_success_observation(self):
        error = subprocess.TimeoutExpired(
            ("sim-use", "ui"), 45, output=b"partial", stderr=b"AX stalled"
        )
        with (
            patch("sim_use_session.subprocess.run", side_effect=error),
            patch("sim_use_session.apple_env", return_value={}),
            self.assertRaisesRegex(RuntimeError, "Timed out"),
        ):
            self.session.command("sim-use", "ui", timeout=45)
        self.assertEqual(
            (
                self.events()[0]["status"],
                self.events()[0]["stdout"],
                self.events()[0]["stderr"],
            ),
            ("timeout", "partial", "AX stalled"),
        )
        self.assertEqual(list(self.session.directory.glob("*.ui.json")), [])
        self.assertFalse((self.session.directory / "ui-timeout-display.png").exists())

    def test_ui_timeout_preserves_daemon_and_display_evidence(self):
        daemon_log = self.session.directory / "upstream.log"
        daemon_log.write_text("daemon accepted UI request\n")

        def run(args, **_kwargs):
            if args[:2] == ("sim-use", "ui"):
                raise subprocess.TimeoutExpired(args, 45, output=b"", stderr=b"waiting")
            if args[:3] == ("sim-use", "daemon", "status"):
                output = json.dumps(
                    {
                        "data": {
                            "daemons": [
                                {"deviceId": "fixed-device", "logPath": str(daemon_log)}
                            ]
                        }
                    }
                )
            elif args[:3] == ("xcrun", "simctl", "io"):
                Path(args[-1]).write_bytes(PNG_SIGNATURE + b"captured")
                output = "Screenshot saved"
            else:
                output = "running"
            return subprocess.CompletedProcess(args, 0, output, "")

        with (
            patch("sim_use_session.subprocess.run", side_effect=run),
            patch("sim_use_session.apple_env", return_value={}),
            self.assertRaisesRegex(RuntimeError, "Timed out"),
        ):
            self.session.command("sim-use", "ui", timeout=45)
        self.assertIn(
            "daemon accepted UI request",
            (self.session.directory / "sim-use-daemon-tail.log").read_text(),
        )
        self.assertTrue((self.session.directory / "ui-timeout-display.png").exists())
        self.assertEqual(self.events()[0]["status"], "timeout")
        self.assertTrue(
            any(
                event["argv"][:3] == ["xcrun", "simctl", "spawn"]
                for event in self.events()
            )
        )

    def test_diagnostic_error_does_not_replace_ui_timeout(self):
        error = subprocess.TimeoutExpired(("sim-use", "ui"), 45)
        with (
            patch("sim_use_session.subprocess.run", side_effect=error),
            patch.object(
                self.session,
                "capture_ui_timeout",
                side_effect=ValueError("diagnostic failed"),
            ),
            self.assertRaisesRegex(RuntimeError, "Timed out"),
        ):
            self.session.command("sim-use", "ui", timeout=45)
        self.assertIn(
            "diagnostic failed",
            (self.session.directory / "ui-timeout-diagnostic-error.txt").read_text(),
        )

    def test_failed_display_capture_does_not_leave_png(self):
        def command(*args, **_kwargs):
            if args[:3] == ("xcrun", "simctl", "io"):
                Path(args[-1]).write_bytes(PNG_SIGNATURE + b"incomplete")
                raise RuntimeError("Capture failed")
            if args[:3] == ("sim-use", "daemon", "status"):
                return '{"data": {"daemons": []}}'
            return ""

        self.session.command = command
        self.session.capture_ui_timeout()
        self.assertFalse((self.session.directory / "ui-timeout-display.png").exists())

    @patch("sim_use_session.HOST_APP")
    @patch("sim_use_session.prepare_simulator")
    def test_existing_host_preparation_uses_fixed_device(self, prepare, host):
        host.is_dir.return_value = True
        calls = []
        self.session.command = lambda *args, **kwargs: calls.append((args, kwargs))
        install_existing_host(self.session)
        prepare.assert_called_once_with()
        self.assertEqual(
            calls,
            [
                (
                    ("xcrun", "simctl", "bootstatus", "fixed-device", "-b"),
                    {"timeout": 120},
                ),
                (
                    ("xcrun", "simctl", "install", "fixed-device", str(host)),
                    {"timeout": 120},
                ),
            ],
        )

    @patch("sim_use_session.HOST_APP")
    @patch("sim_use_session.prepare_simulator")
    def test_missing_host_stops_before_install(self, _prepare, host):
        host.is_dir.return_value = False
        calls = []
        self.session.command = lambda *args, **kwargs: calls.append(args)
        with self.assertRaisesRegex(RuntimeError, "Built host missing"):
            install_existing_host(self.session)
        self.assertEqual(
            calls, [("xcrun", "simctl", "bootstatus", "fixed-device", "-b")]
        )


if __name__ == "__main__":
    unittest.main()
