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
            for manifest in (
                "SnapshotTesting/Package.swift",
                "AppMacros/Package.swift",
                "swift-syntax/Package.swift",
            ):
                path = prepared / manifest
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()

            sources = {
                "SNAPSHOT_SOURCE": root / "snapshot-source",
                "APP_MACROS_SOURCE": root / "macro-source",
                "SWIFT_SYNTAX_SOURCE": root / "syntax-source",
            }
            for key, witness in (
                ("SNAPSHOT_SOURCE", "Sources/SnapshotTesting"),
                ("APP_MACROS_SOURCE", "Sources/AppMacros"),
                ("SWIFT_SYNTAX_SOURCE", "Sources/SwiftSyntax"),
            ):
                (sources[key] / witness).mkdir(parents=True)

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

                newer_macro = root / "new-macro-source"
                (newer_macro / "Sources/AppMacros").mkdir(parents=True)
                with (
                    patch.dict(os.environ, {"APP_MACROS_SOURCE": str(newer_macro)}),
                    self.assertRaisesRegex(RuntimeError, "prepare-deps"),
                ):
                    tasks.prepared_dependencies()


if __name__ == "__main__":
    unittest.main()
