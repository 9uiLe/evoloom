"""Materialize Nix-fixed Swift package sources before any Xcode build."""

import shutil
from pathlib import Path

from prepared_sources import STAMP, nix_sources, record_prepared_sources

ROOT = Path(__file__).resolve().parents[1]
PREPARED = ROOT / ".prepared"


def remove_tree(target):
    if target.exists():
        for path in target.rglob("*"):
            path.chmod(path.stat().st_mode | 0o200)
        target.chmod(target.stat().st_mode | 0o200)
        shutil.rmtree(target)


sources = nix_sources()
snapshot = Path(sources["SNAPSHOT_SOURCE"])
PREPARED.mkdir(exist_ok=True)
(PREPARED / STAMP).unlink(missing_ok=True)
for obsolete in ("AppMacros", "swift-syntax"):
    remove_tree(PREPARED / obsolete)

snapshot_target = PREPARED / "SnapshotTesting"
remove_tree(snapshot_target)
(snapshot_target / "Sources").mkdir(parents=True)
shutil.copytree(
    snapshot / "Sources/SnapshotTesting",
    snapshot_target / "Sources/SnapshotTesting",
    copy_function=shutil.copyfile,
)
shutil.copyfile(snapshot / "LICENSE", snapshot_target / "LICENSE")
(snapshot_target / "Package.swift").write_text(
    """// swift-tools-version: 6.2
import PackageDescription
let package = Package(
    name: "SnapshotTestingLocal",
    platforms: [.iOS(.v26)],
    products: [.library(name: "SnapshotTesting", targets: ["SnapshotTesting"])],
    targets: [.target(name: "SnapshotTesting")],
    swiftLanguageModes: [.v5]
)
"""
)

record_prepared_sources(PREPARED, sources)
print(f"Prepared SnapshotTesting from {snapshot}")
