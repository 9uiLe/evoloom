import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tasks


class PreparedSourceTests(unittest.TestCase):
    def test_build_rejects_unrecorded_or_stale_nix_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prepared = root / ".prepared"
            for manifest in ("SnapshotTesting/Package.swift",):
                path = prepared / manifest
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()

            sources = {"SNAPSHOT_SOURCE": root / "snapshot-source"}
            (sources["SNAPSHOT_SOURCE"] / "Sources/SnapshotTesting").mkdir(parents=True)

            with (
                patch.object(tasks, "ROOT", root),
                patch.dict(
                    os.environ, {key: str(path) for key, path in sources.items()}
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "prepare-deps"):
                    tasks.prepared_dependencies()

                (prepared / "sources.json").write_text(
                    json.dumps(
                        {key: str(path.resolve()) for key, path in sources.items()}
                    )
                )
                tasks.prepared_dependencies()

                newer_snapshot = root / "new-snapshot-source"
                (newer_snapshot / "Sources/SnapshotTesting").mkdir(parents=True)
                with (
                    patch.dict(os.environ, {"SNAPSHOT_SOURCE": str(newer_snapshot)}),
                    self.assertRaisesRegex(RuntimeError, "prepare-deps"),
                ):
                    tasks.prepared_dependencies()


if __name__ == "__main__":
    unittest.main()
