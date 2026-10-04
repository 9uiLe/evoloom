"""Validated Xcode entry points; no App target or implicit dependency downloads."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from prepared_sources import nix_sources, verify_prepared_sources

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_XCODE = "Xcode 27.0\nBuild version 27A266a"
EXPECTED_MACOS_BUILD = "26A428"
EXPECTED_SDK = "27.0"
EXPECTED_SDK_BUILD = "24A430"
EXPECTED_RUNTIME = "com.apple.CoreSimulator.SimRuntime.iOS-27-0"
EXPECTED_RUNTIME_BUILD = "24A434"
EXPECTED_DEVICE = "iPhone 18 Pro"
XCODE_TIMEOUT_SECONDS = 600
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
    "collection-empty",
    "collection-loading",
    "collection-error",
    "customized-tokens",
    "customized-tokens-dark",
    "switch-states-dark",
    "switch-states-dark-increased-contrast",
    "switch-states-dark-ja",
    "review-components-controls-light",
    "review-components-controls-dark",
    "review-components-feedback-light",
    "review-components-feedback-dark",
    "review-settings-light",
    "review-settings-dark",
    "review-settings-error",
    "review-detail-light",
    "review-detail-dark",
    "review-detail-ja-long",
}
UNIT_TEST_COUNT = 6
SNAPSHOT_TEST_COUNT = 9
HOSTED_SNAPSHOT_TEST_COUNT = 5
HOST_PROJECT = ROOT / "Testing/Host/EvoloomReviewHost.xcodeproj"


def metric(phase, seconds, **details):
    target = ROOT / "TestResults/metrics.jsonl"
    target.parent.mkdir(exist_ok=True)
    with target.open("a") as output_file:
        output_file.write(
            json.dumps(
                {"phase": phase, "seconds": round(seconds, 3), **details},
                sort_keys=True,
            )
            + "\n"
        )


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
        "xcodegen",
    ]
    missing = [tool for tool in required if shutil.which(tool) is None]
    if missing:
        raise RuntimeError(f"Nix shell missing tools: {missing}; run nix develop")
    if output("xcodegen", "--version") != "Version: 2.44.1":
        raise RuntimeError("Expected Nix-pinned XcodeGen 2.44.1")
    sources = nix_sources()
    if output("sw_vers", "-buildVersion") != EXPECTED_MACOS_BUILD:
        raise RuntimeError(f"Expected macOS build {EXPECTED_MACOS_BUILD}")
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
    print(f"Nix snapshot source: {sources['SNAPSHOT_SOURCE']}")
    return matches[0]["udid"]


def prepared_dependencies():
    verify_prepared_sources(ROOT / ".prepared")


def prepare_simulator():
    device = doctor()
    devices = json.loads(output("xcrun", "simctl", "list", "devices", "-j"))["devices"]
    state = next(
        item["state"] for item in devices[EXPECTED_RUNTIME] if item["udid"] == device
    )
    started = time.monotonic()
    if state == "Shutdown":
        subprocess.run(["xcrun", "simctl", "boot", device], check=True, env=apple_env())
    elif state not in {"Booted", "Booting"}:
        raise RuntimeError(f"Cannot prepare simulator in state {state}")
    metric(
        "simulator-boot-request",
        time.monotonic() - started,
        state_before=state,
        device=device,
    )
    print(f"Simulator {device}: {state}; boot requested if needed", flush=True)


def xcode(
    action,
    cwd=ROOT,
    scheme="Evoloom",
    result=None,
    derived_data=None,
    only_testing=(),
    check=True,
    project=None,
):
    device = doctor()
    command = [
        "xcodebuild",
        action,
        "-quiet",
        *(["-project", str(project)] if project else []),
        "-scheme",
        scheme,
        "-destination",
        f"platform=iOS Simulator,id={device}",
        "-derivedDataPath",
        str(ROOT / "DerivedData" / (derived_data or scheme)),
        "-disableAutomaticPackageResolution",
        "CODE_SIGNING_ALLOWED=NO",
    ]
    if os.environ.get("EVOLOOM_BUILD_DIAGNOSTICS") == "1":
        command.remove("-quiet")
        command.append("-showBuildTimingSummary")
    if action in {"test", "test-without-building"}:
        scheme_position = command.index("-scheme")
        command[scheme_position:scheme_position] = [
            "-parallel-testing-enabled",
            "NO",
            "-enableCodeCoverage",
            "NO",
            "-testLanguage",
            "en",
            "-testRegion",
            "US",
        ]
        for identifier in only_testing:
            command.append(f"-only-testing:{identifier}")
    if result:
        result.parent.mkdir(parents=True, exist_ok=True)
        if result.exists():
            shutil.rmtree(result)
        command.extend(["-resultBundlePath", str(result)])
    print(" ".join(command), flush=True)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=apple_env(),
            check=check,
            timeout=XCODE_TIMEOUT_SECONDS,
        )
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as error:
        metric(
            "xcode",
            time.monotonic() - started,
            action=action,
            scheme=scheme,
            result=type(error).__name__,
        )
        raise
    metric(
        "xcode",
        time.monotonic() - started,
        action=action,
        scheme=scheme,
        result="passed" if completed.returncode == 0 else "failed",
    )
    return completed


def test_result_count(path, expected):
    summary = json.loads(
        output(
            "xcrun",
            "xcresulttool",
            "get",
            "test-results",
            "summary",
            "--path",
            str(path),
            "--format",
            "json",
        )
    )
    if (
        summary.get("totalTestCount") != expected
        or summary.get("failedTests")
        or summary.get("skippedTests")
    ):
        raise RuntimeError(
            f"Expected {expected} passing tests in {path}, got {summary}"
        )


def snapshot_hashes():
    directories = (
        ROOT / "Testing/Tests/EvoloomSnapshotTests/__Snapshots__",
        ROOT / "Testing/Host/Tests/__Snapshots__",
    )
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for directory in directories
        for path in directory.rglob("*.png")
    }


def prepare_host():
    prepared_dependencies()
    subprocess.run(
        [
            "xcodegen",
            "generate",
            "--spec",
            "Testing/Host/project.json",
            "--project",
            "Testing/Host",
        ],
        cwd=ROOT,
        check=True,
    )


def host_xcode(action, **kwargs):
    prepare_host()
    return xcode(
        action,
        cwd=ROOT,
        scheme="EvoloomReviewHost",
        project=HOST_PROJECT,
        derived_data="Host",
        **kwargs,
    )


def clear_rendered_images():
    rendered = ROOT / "TestResults/Rendered"
    if rendered.exists():
        shutil.rmtree(rendered)


def rendered_preflight():
    expected = {
        Path(path).name
        for path in json.loads((ROOT / "tools/snapshots.json").read_text())
    }
    actual = {path.name for path in (ROOT / "TestResults/Rendered").glob("*.png")}
    if actual != expected:
        raise RuntimeError(
            f"Expected {len(expected)} actual render PNGs, got {len(actual)}; "
            f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
        )


def snapshot_preflight():
    manifest = ROOT / "tools/snapshots.json"
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
    unexpected = sorted(set(snapshot_hashes()) - set(expected))
    if unexpected:
        raise RuntimeError(f"Unexpected baseline images: {unexpected}")
    if (ROOT / ".prepared/record-snapshots").exists():
        raise RuntimeError(
            "Record marker is present; remove .prepared/record-snapshots before comparison"
        )
    if (ROOT / ".prepared/record-host-snapshots").exists():
        raise RuntimeError("Host record marker is present; remove it before comparison")
    return len(expected)


def snapshots(record=False):
    prepared_dependencies()
    if not record:
        snapshot_preflight()
    before = snapshot_hashes()
    clear_rendered_images()
    differences = ROOT / "TestResults/SnapshotDiffs"
    if differences.exists():
        shutil.rmtree(differences)
    marker = ROOT / ".prepared/record-snapshots"
    host_marker = ROOT / ".prepared/record-host-snapshots"
    if record:
        marker.write_text("Record mode enabled by just record-snapshots\n")
        host_marker.write_text("Record mode enabled by just record-snapshots\n")
    result = (
        ROOT / "TestResults" / ("record.xcresult" if record else "snapshot.xcresult")
    )
    host_result = (
        ROOT
        / "TestResults"
        / ("host-record.xcresult" if record else "host-snapshot.xcresult")
    )
    try:
        completed = xcode(
            "test",
            cwd=ROOT / "Testing",
            scheme="EvoloomVisualTests",
            result=result,
            derived_data="Visual",
            only_testing=("EvoloomSnapshotTests/ComponentSnapshots",),
            check=False,
        )
        hosted = host_xcode(
            "test",
            result=host_result,
            only_testing=("EvoloomHostedTests/HostedCollectionTests",),
            check=False,
        )
    finally:
        if record:
            marker.unlink(missing_ok=True)
            host_marker.unlink(missing_ok=True)
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
        raise SystemExit(completed.returncode)
    if hosted.returncode:
        raise SystemExit(hosted.returncode)
    test_result_count(result, SNAPSHOT_TEST_COUNT)
    test_result_count(host_result, HOSTED_SNAPSHOT_TEST_COUNT)
    if not record:
        rendered_preflight()


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
            str(ROOT / "tools/evoloom.py"),
            "init",
            "--destination",
            str(destination),
            *names,
        ],
        check=True,
    )
    (destination / "Package.swift").write_text(
        """// swift-tools-version: 6.2
import PackageDescription
let package = Package(name: "CopyCheck", platforms: [.iOS(.v26)],
    products: [.library(name: "EvoloomCopied", targets: ["EvoloomCopied"])],
    targets: [.target(name: "EvoloomCopied")])
"""
    )
    xcode(
        "build",
        cwd=destination,
        scheme="CopyCheck",
        result=ROOT / "TestResults/copy-build.xcresult",
    )


def unit_tests():
    result = ROOT / "TestResults/unit.xcresult"
    xcode(
        "test",
        cwd=ROOT / "Testing",
        scheme="EvoloomVisualTests",
        result=result,
        derived_data="Visual",
        only_testing=(
            "EvoloomSnapshotTests/DesignTokensTests",
            "EvoloomSnapshotTests/InteractionTests",
        ),
    )
    test_result_count(result, UNIT_TEST_COUNT)


def ios_tests():
    prepared_dependencies()
    snapshot_preflight()
    before = snapshot_hashes()
    clear_rendered_images()
    differences = ROOT / "TestResults/SnapshotDiffs"
    if differences.exists():
        shutil.rmtree(differences)
    result = ROOT / "TestResults/ios.xcresult"
    host_result = ROOT / "TestResults/host-ios.xcresult"
    completed = xcode(
        "test",
        cwd=ROOT / "Testing",
        scheme="EvoloomVisualTests",
        result=result,
        derived_data="Visual",
        check=False,
    )
    hosted = host_xcode("test", result=host_result, check=False)
    if before != snapshot_hashes():
        raise RuntimeError("Comparison created or changed baseline images")
    if completed.returncode:
        raise SystemExit(completed.returncode)
    if hosted.returncode:
        raise SystemExit(hosted.returncode)
    test_result_count(result, UNIT_TEST_COUNT + SNAPSHOT_TEST_COUNT)
    test_result_count(host_result, HOSTED_SNAPSHOT_TEST_COUNT)
    rendered_preflight()


def run_host():
    screen = os.environ.get("EVOLOOM_SCREEN", "collection")
    state = os.environ.get("EVOLOOM_STATE", "normal")
    appearance = os.environ.get("EVOLOOM_APPEARANCE", "light")
    if screen not in {
        "collection",
        "controls",
        "feedback",
        "settings",
        "settingsError",
        "detail",
    }:
        raise RuntimeError(f"Unknown review screen: {screen}")
    if state not in {"normal", "empty", "loading", "error"}:
        raise RuntimeError(f"Unknown collection state: {state}")
    if appearance not in {"light", "dark"}:
        raise RuntimeError(f"Unknown appearance: {appearance}")
    device = doctor()
    prepare_simulator()
    host_xcode("build")
    subprocess.run(
        ["xcrun", "simctl", "bootstatus", device, "-b"], check=True, env=apple_env()
    )
    app = (
        ROOT
        / "DerivedData/Host/Build/Products/Debug-iphonesimulator/EvoloomReviewHost.app"
    )
    subprocess.run(
        ["xcrun", "simctl", "install", device, str(app)], check=True, env=apple_env()
    )
    subprocess.run(
        ["xcrun", "simctl", "ui", device, "appearance", appearance],
        check=True,
        env=apple_env(),
    )
    launch = [
        "xcrun",
        "simctl",
        "launch",
        "--terminate-running-process",
        device,
        "dev.evoloom.reviewhost",
        f"--screen={screen}",
        f"--state={state}",
    ]
    if appearance == "dark":
        launch.append("--dark")
    subprocess.run(launch, check=True, env=apple_env())


def main():
    command = sys.argv[1] if len(sys.argv) == 2 else ""
    actions = {
        "doctor": doctor,
        "prepare-simulator": prepare_simulator,
        "build-package": lambda: xcode("build"),
        "prepare-host": prepare_host,
        "build-host": lambda: host_xcode("build"),
        "run-host": run_host,
        "test-unit": unit_tests,
        "test-ios": ios_tests,
        "test-snapshot": snapshots,
        "record-snapshots": lambda: snapshots(record=True),
        "verify-copy-install": verify_copy,
    }
    if command not in actions:
        raise SystemExit(f"Unknown command: {command}")
    actions[command]()


if __name__ == "__main__":
    main()
