"""Validated Xcode entry points; no App target or implicit dependency downloads."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_XCODE = "Xcode 27.0\nBuild version 27A266a"
EXPECTED_SDK = "27.0"
EXPECTED_SDK_BUILD = "24A430"
EXPECTED_RUNTIME = "com.apple.CoreSimulator.SimRuntime.iOS-27-0"
EXPECTED_RUNTIME_BUILD = "24A434"
EXPECTED_DEVICE = "iPhone 18 Pro"
SNAPSHOT_NAMES = {
    "catalog-light",
    "catalog-dark",
    "inputs-light",
    "inputs-dark",
    "compact-accessibility",
    "locale-ja",
    "locale-en",
    "collection-light",
    "collection-dark",
    "collection-compact-accessibility",
}


def output(*command, cwd=ROOT):
    return subprocess.check_output(
        command, cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def apple_env():
    """Keep Xcode's linker and SDK ahead of Nix's Darwin stdenv wrappers."""
    env = os.environ.copy()
    for key in list(env):
        if key.startswith("NIX_") or key in {
            "CC",
            "CXX",
            "LD",
            "SDKROOT",
            "LIBRARY_PATH",
            "CPATH",
            "CFLAGS",
            "LDFLAGS",
        }:
            env.pop(key, None)
    toolchain = (
        Path(env["DEVELOPER_DIR"]) / "Toolchains/XcodeDefault.xctoolchain/usr/bin"
    )
    env["PATH"] = f"{toolchain}:/usr/bin:/bin:/usr/sbin:/sbin"
    return env


def doctor():
    required = [
        "swiftlint",
        "swiftformat",
        "just",
        "ruff",
        "nixfmt",
        "python3",
        "yamllint",
        "actionlint",
    ]
    missing = [tool for tool in required if shutil.which(tool) is None]
    if missing or not os.environ.get("SNAPSHOT_SOURCE"):
        raise RuntimeError(
            f"Nix shell missing tools/source: {missing}; run nix develop"
        )
    if output("xcodebuild", "-version") != EXPECTED_XCODE:
        raise RuntimeError(
            f"Expected {EXPECTED_XCODE!r}, got {output('xcodebuild', '-version')!r}"
        )
    if (
        output("xcrun", "--sdk", "iphonesimulator", "--show-sdk-version")
        != EXPECTED_SDK
    ):
        raise RuntimeError("iOS Simulator SDK version mismatch")
    if (
        output("xcrun", "--sdk", "iphonesimulator", "--show-sdk-build-version")
        != EXPECTED_SDK_BUILD
    ):
        raise RuntimeError("iOS Simulator SDK build mismatch")
    if output("uname", "-m") != "arm64":
        raise RuntimeError("Expected arm64 host")
    runtimes = json.loads(output("xcrun", "simctl", "list", "runtimes", "-j"))[
        "runtimes"
    ]
    runtime = next(
        (item for item in runtimes if item["identifier"] == EXPECTED_RUNTIME), None
    )
    if (
        runtime is None
        or runtime.get("buildversion") != EXPECTED_RUNTIME_BUILD
        or not runtime.get("isAvailable")
    ):
        raise RuntimeError(f"Expected iOS 27.0 runtime build {EXPECTED_RUNTIME_BUILD}")
    devices = json.loads(output("xcrun", "simctl", "list", "devices", "-j"))["devices"]
    matches = [
        item
        for item in devices.get(EXPECTED_RUNTIME, [])
        if item["name"] == EXPECTED_DEVICE and item["isAvailable"]
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one available {EXPECTED_DEVICE} on {EXPECTED_RUNTIME}"
        )
    print(
        f"Xcode 27.0 (27A266a), SDK 27.0 ({EXPECTED_SDK_BUILD}), runtime 27.0 ({EXPECTED_RUNTIME_BUILD}), {EXPECTED_DEVICE}, arm64"
    )
    print(f"Simulator UDID: {matches[0]['udid']}")
    print(f"Swift: {output('xcrun', 'swift', '--version').splitlines()[0]}")
    print(f"Nix snapshot source: {os.environ['SNAPSHOT_SOURCE']}")
    return matches[0]["udid"]


def xcode(action, cwd=ROOT, scheme="ShadcnIOS", result=None):
    device = doctor()
    command = [
        "xcodebuild",
        action,
        "-quiet",
        "-scheme",
        scheme,
        "-destination",
        f"platform=iOS Simulator,id={device}",
        "-derivedDataPath",
        str(ROOT / "DerivedData" / scheme),
        "-disableAutomaticPackageResolution",
        "CODE_SIGNING_ALLOWED=NO",
    ]
    if action == "test":
        command[3:3] = ["-parallel-testing-enabled", "NO", "-enableCodeCoverage", "NO"]
    if result:
        result.parent.mkdir(parents=True, exist_ok=True)
        if result.exists():
            shutil.rmtree(result)
        command.extend(["-resultBundlePath", str(result)])
    print(" ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=apple_env(), check=True, timeout=240)


def snapshot_hashes():
    directory = ROOT / "Testing/Tests/ShadcnIOSSnapshotTests/__Snapshots__"
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in directory.rglob("*.png")
    }


def snapshots(record=False):
    prepared = ROOT / ".prepared/SnapshotTesting/Package.swift"
    if not prepared.exists():
        raise RuntimeError(
            "Test source missing; run just prepare-deps inside nix develop"
        )
    manifest = ROOT / "tools/snapshots.json"
    if not record:
        if not manifest.exists():
            raise RuntimeError(
                "Snapshot manifest missing; run just record-snapshots and review images"
            )
        expected = json.loads(manifest.read_text())
        if {
            Path(name).stem.removeprefix("components.") for name in expected
        } != SNAPSHOT_NAMES:
            raise RuntimeError("Snapshot manifest does not list the full test matrix")
        missing = [name for name in expected if not (ROOT / name).is_file()]
        if missing:
            raise RuntimeError(f"Missing baseline images: {missing}")
    before = snapshot_hashes()
    differences = ROOT / "TestResults/SnapshotDiffs"
    if differences.exists():
        shutil.rmtree(differences)
    env = apple_env()
    marker = ROOT / ".prepared/record-snapshots"
    if record:
        marker.write_text("Record mode enabled by just record-snapshots\n")
    elif marker.exists():
        raise RuntimeError(
            "Record marker is present; remove .prepared/record-snapshots before comparison"
        )
    device = doctor()
    result = (
        ROOT / "TestResults" / ("record.xcresult" if record else "snapshot.xcresult")
    )
    if result.exists():
        shutil.rmtree(result)
    result.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "xcodebuild",
        "test",
        "-quiet",
        "-parallel-testing-enabled",
        "NO",
        "-enableCodeCoverage",
        "NO",
        "-scheme",
        "ShadcnIOSVisualTests-Package",
        "-destination",
        f"platform=iOS Simulator,id={device}",
        "-derivedDataPath",
        str(ROOT / "DerivedData/Visual"),
        "-disableAutomaticPackageResolution",
        "-resultBundlePath",
        str(result),
        "CODE_SIGNING_ALLOWED=NO",
    ]
    print(" ".join(command), flush=True)
    try:
        completed = subprocess.run(
            command, cwd=ROOT / "Testing", env=env, check=False, timeout=240
        )
    finally:
        if record:
            marker.unlink(missing_ok=True)
    after = snapshot_hashes()
    if not record and before != after:
        raise RuntimeError("Comparison created or changed baseline images")
    if record:
        if {
            Path(name).stem.removeprefix("components.") for name in after
        } != SNAPSHOT_NAMES:
            raise RuntimeError("Recording did not produce the full test matrix")
        (ROOT / "tools/snapshots.json").write_text(
            json.dumps(sorted(after), indent=2) + "\n"
        )
        print(f"Recorded {len(after)} PNGs. Review visually before committing.")
    if completed.returncode:
        if record and after:
            report = json.loads(
                output(
                    "xcrun",
                    "xcresulttool",
                    "get",
                    "test-results",
                    "tests",
                    "--path",
                    str(result),
                    "--format",
                    "json",
                )
            )
            messages = []

            def failures(node):
                if isinstance(node, dict):
                    if node.get("nodeType") == "Failure Message":
                        messages.append(node.get("name", ""))
                    for value in node.values():
                        failures(value)
                elif isinstance(node, list):
                    for value in node:
                        failures(value)

            failures(report)
            if messages and all(
                "Record mode is on." in message for message in messages
            ):
                print(
                    "Recording completed; XCTest reports intentional record-mode failures."
                )
                return
        raise SystemExit(completed.returncode)


def verify_copy():
    doctor()
    destination = ROOT / ".prepared/CopyCheck"
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    names = json.loads((ROOT / "tools/registry.json").read_text())
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/shadcn_ios.py"),
            "init",
            "--destination",
            str(destination),
            *names,
        ],
        check=True,
    )
    (destination / "Package.swift").write_text(
        """// swift-tools-version: 6.0
import PackageDescription
let package = Package(name: "CopyCheck", platforms: [.iOS(.v17)],
    products: [.library(name: "ShadcnIOSCopied", targets: ["ShadcnIOSCopied"])],
    targets: [.target(name: "ShadcnIOSCopied"),
              .testTarget(name: "CopyCheckTests", dependencies: ["ShadcnIOSCopied"])])
"""
    )
    test = destination / "Tests/CopyCheckTests/CopyCheckTests.swift"
    test.parent.mkdir(parents=True)
    test.write_text(
        "import ShadcnIOSCopied\nimport XCTest\nfinal class CopyCheckTests: XCTestCase { func testTheme() { XCTAssertEqual(IOSTheme.neutral.spacing.md, 16) } }\n"
    )
    xcode(
        "test",
        cwd=destination,
        scheme="CopyCheck",
        result=ROOT / "TestResults/copy.xcresult",
    )


def main():
    command = sys.argv[1] if len(sys.argv) == 2 else ""
    actions = {
        "doctor": doctor,
        "build-package": lambda: xcode("build"),
        "test-unit": lambda: xcode("test", result=ROOT / "TestResults/unit.xcresult"),
        "test-snapshot": snapshots,
        "record-snapshots": lambda: snapshots(record=True),
        "verify-copy-install": verify_copy,
    }
    if command not in actions:
        raise SystemExit(f"Unknown command: {command}")
    actions[command]()


if __name__ == "__main__":
    main()
