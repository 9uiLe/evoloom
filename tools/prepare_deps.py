"""Materialize only the SnapshotTesting module from Nix's fixed source."""

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ["SNAPSHOT_SOURCE"])
TARGET = ROOT / ".prepared" / "SnapshotTesting"

if not (SOURCE / "Sources" / "SnapshotTesting").is_dir():
    raise SystemExit("Nix SnapshotTesting source is missing; run nix develop first")

if TARGET.exists():
    for path in TARGET.rglob("*"):
        path.chmod(path.stat().st_mode | 0o200)
    TARGET.chmod(TARGET.stat().st_mode | 0o200)
    shutil.rmtree(TARGET)
TARGET.mkdir(parents=True)
shutil.copytree(
    SOURCE / "Sources" / "SnapshotTesting",
    TARGET / "Sources" / "SnapshotTesting",
    copy_function=shutil.copyfile,
)
shutil.copyfile(SOURCE / "LICENSE", TARGET / "LICENSE")
(TARGET / "Package.swift").write_text(
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
print(f"Prepared SnapshotTesting at {TARGET} from {SOURCE}")
