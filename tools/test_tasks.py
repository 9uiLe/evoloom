import json
import unittest
from unittest.mock import patch

import tasks


class PrepareSimulatorTests(unittest.TestCase):
    def prepare(self, state):
        devices = {
            "devices": {
                tasks.EXPECTED_RUNTIME: [{"udid": "fixed-device", "state": state}]
            }
        }
        with (
            patch.object(tasks, "doctor", return_value="fixed-device"),
            patch.object(tasks, "output", return_value=json.dumps(devices)),
            patch.object(tasks, "apple_env", return_value={}),
            patch.object(tasks, "metric") as record,
            patch.object(tasks.subprocess, "run") as run,
        ):
            if state == "Creating":
                with self.assertRaisesRegex(RuntimeError, "Creating"):
                    tasks.prepare_simulator()
            else:
                tasks.prepare_simulator()
            return run, record

    def test_shutdown_device_requests_boot_without_erasing(self):
        run, record = self.prepare("Shutdown")
        run.assert_called_once_with(
            ["xcrun", "simctl", "boot", "fixed-device"], check=True, env={}
        )
        self.assertEqual(record.call_args.kwargs["state_before"], "Shutdown")

    def test_booted_device_is_reused(self):
        run, record = self.prepare("Booted")
        run.assert_not_called()
        self.assertEqual(record.call_args.kwargs["state_before"], "Booted")

    def test_unexpected_device_state_fails(self):
        run, record = self.prepare("Creating")
        run.assert_not_called()
        record.assert_not_called()


class XcodeCommandTests(unittest.TestCase):
    def test_test_options_preserve_scheme_in_both_logging_modes(self):
        for diagnostics in ("0", "1"):
            with (
                self.subTest(diagnostics=diagnostics),
                patch.dict(tasks.os.environ, EVOLOOM_BUILD_DIAGNOSTICS=diagnostics),
                patch.object(tasks, "doctor", return_value="fixed-device"),
                patch.object(tasks, "apple_env", return_value={}),
                patch.object(tasks, "metric"),
                patch.object(tasks.subprocess, "run") as run,
            ):
                tasks.xcode("test", scheme="Fixed-Package")
                command = run.call_args.args[0]
                self.assertEqual(command[command.index("-scheme") + 1], "Fixed-Package")
                self.assertEqual(
                    command[command.index("-parallel-testing-enabled") + 1], "NO"
                )
                self.assertEqual(
                    "-showBuildTimingSummary" in command, diagnostics == "1"
                )


if __name__ == "__main__":
    unittest.main()
