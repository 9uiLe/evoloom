"""Materialize Nix-fixed Swift package sources before any Xcode build."""

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREPARED = ROOT / ".prepared"


def remove_tree(target):
    if target.exists():
        for path in target.rglob("*"):
            path.chmod(path.stat().st_mode | 0o200)
        target.chmod(target.stat().st_mode | 0o200)
        shutil.rmtree(target)


def replace_tree(source, target):
    remove_tree(target)
    shutil.copytree(source, target, copy_function=shutil.copyfile)


def source(name, witness):
    value = os.environ.get(name)
    if not value or not (Path(value) / witness).exists():
        raise SystemExit(f"Nix source {name} is missing; run nix develop first")
    return Path(value)


snapshot = source("SNAPSHOT_SOURCE", "Sources/SnapshotTesting")
macros = source("APP_MACROS_SOURCE", "Sources/AppMacros")
syntax = source("SWIFT_SYNTAX_SOURCE", "Sources/SwiftSyntax")
PREPARED.mkdir(exist_ok=True)

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

replace_tree(syntax, PREPARED / "swift-syntax")
macro_target = PREPARED / "AppMacros"
remove_tree(macro_target)
(macro_target / "Sources").mkdir(parents=True)
for module in ("AppMacros", "AppMacrosMacros"):
    shutil.copytree(
        macros / "Sources" / module,
        macro_target / "Sources" / module,
        copy_function=shutil.copyfile,
    )
shutil.copyfile(macros / "LICENSE", macro_target / "LICENSE")
(macro_target / "Package.swift").write_text(
    """// swift-tools-version: 6.3
import CompilerPluginSupport
import PackageDescription
let package = Package(
    name: "swift-app-macros",
    platforms: [.iOS(.v26), .macOS(.v26)],
    products: [.library(name: "AppMacros", targets: ["AppMacros"])],
    dependencies: [.package(name: "swift-syntax", path: "../swift-syntax")],
    targets: [
        .macro(name: "AppMacrosMacros", dependencies: [
            .product(name: "SwiftCompilerPlugin", package: "swift-syntax"),
            .product(name: "SwiftDiagnostics", package: "swift-syntax"),
            .product(name: "SwiftSyntax", package: "swift-syntax"),
            .product(name: "SwiftSyntaxBuilder", package: "swift-syntax"),
            .product(name: "SwiftSyntaxMacros", package: "swift-syntax"),
        ]),
        .target(name: "AppMacros", dependencies: ["AppMacrosMacros"]),
    ],
    swiftLanguageModes: [.v6]
)
"""
)
print(f"Prepared SnapshotTesting from {snapshot}")
print(f"Prepared AppMacros from {macros}")
print(f"Prepared swift-syntax from {syntax}")
