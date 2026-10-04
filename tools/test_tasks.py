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


if __name__ == "__main__":
    unittest.main()
