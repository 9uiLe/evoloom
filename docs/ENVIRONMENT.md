# Fixed environment and dependency boundary

`flake.lock` records immutable revisions and NAR hashes for all Nix inputs:

| Source | Fixed version / revision | Use |
| --- | --- | --- |
| nixpkgs | `44a91898084f46797b5fac650c7e8c9ac38c43d4` | SwiftLint 0.65.1, SwiftFormat 0.63.0, just 1.58.0, Python 3.14.7, Ruff 0.16.8, nixfmt 1.5.0, yamllint 1.37.1, actionlint 1.7.12, ShellCheck 0.11.0, shfmt 3.14.1 |
| swift-snapshot-testing | `1.18.9`, revision `bf8d8c27f0f0c6d5e77bff0db76ab68f2050d15d` | Test-only image comparison |

Run `nix develop`, then `just prepare-deps`. That preparation copies the
Nix-fixed sources to ignored `.prepared/` local Swift packages and records the
selected Nix store paths in `.prepared/sources.json` after copying finishes.
Visual test commands reject missing or stale preparation, including files left
from an earlier `flake.lock`; rerun `just prepare-deps` after updating the
lock. Root library builds, root unit tests and copy builds do not require the
prepared SnapshotTesting Package. SnapshotTesting is reduced to its image
comparison module, excluding its optional sibling products and their
transitive dependencies. Its prepared
manifest uses Swift 5 language mode, matching the upstream manifest on this
Xcode. Both the root product and visual test harness use Swift tools 6.2.
The root `Package.swift` has no external dependency and remains readable
without `.prepared`; ordinary consumers only need SwiftPM and Apple's
toolchain. The `just` visual test task fails explicitly if the test-only
SnapshotTesting source has not been prepared. Development and CI resolve that
test source through the Nix-fixed local path, with automatic
SwiftPM package resolution disabled.

Apple prerequisites remain outside Nix: macOS 27.0 build 26A428 on arm64;
Xcode 27.0 build 27A266a at the local path
`/Applications/Xcode-27.0.0.app/Contents/Developer`; Apple Swift
6.4; iPhoneSimulator SDK 27.0 build 24A430; iOS 27.0 Simulator runtime build
24A434; an available iPhone 18 Pro. `just doctor` checks exact versions,
runtime build, device, macOS build and architecture. It does not change the
system-wide Xcode selection. The Nix shell sets `DEVELOPER_DIR` to that
local path or to `EVOLOOM_XCODE_DEVELOPER_DIR` when supplied, and clears `SDKROOT` so
`xcrun` uses the chosen Apple toolchain and SDK. Build commands also remove
Nix compiler and SDK variables and put Xcode's toolchain first on `PATH`.
These Apple artifacts, Simulator pixels and Xcode license are outside the Nix
lock.

GitHub Actions runs on GitHub's ARM64 `xcode-27` hosted image. The image
currently offers Xcode 27.0 build 27A266a and the iOS 27.0 Simulator with an
iPhone 18 Pro; CI selects
`/Applications/Xcode_27.0.0.app/Contents/Developer` through
`EVOLOOM_XCODE_DEVELOPER_DIR`. The shell overwrites Nix's temporary Darwin
SDK `DEVELOPER_DIR` with that Apple toolchain path.
The hosted image is externally managed and can change. `just doctor` rejects
a different macOS, Xcode, SDK or runtime build instead of selecting a newer
Simulator. CI installs Determinate Nix v3.22.2 using its Action pinned to
commit `527f17dd63d2d60d3e5552934bc84b9a33a14d11`; the fixed development
packages and Swift test sources still come from `flake.lock`.

The product deployment target is iOS 26. The root Package unit tests also
ran on the installed iOS 26.5 runtime (build 23F77) with an iPhone 17 Pro in
the earlier baseline validation. Pinned image baselines and `just check` use
iOS 27.0; the iOS 26.5 run is separate.

Preparation and execution are separate. `just prepare-deps` is the only step
that materializes external Swift source. Development and CI Xcode commands use
`-disableAutomaticPackageResolution`; the visual test Package references the
prepared local SnapshotTesting path. Its missing or stale source fails with a
preparation instruction. To verify a clean checkout, clone to another
directory, run `nix develop`, `just doctor`,
`just prepare-deps`, then `just check` on the specified Apple host. A missing
tool or mismatched Simulator fails before tests.

References: [Nix manual](https://nixos.org/manual/nix/stable/),
[SwiftLint](https://github.com/realm/SwiftLint),
[SwiftFormat](https://github.com/nicklockwood/SwiftFormat), and
[SnapshotTesting](https://github.com/pointfreeco/swift-snapshot-testing).
Hosted CI details: [GitHub's Xcode 27 image](https://github.com/actions/runner-images/blob/main/images/macos/xcode-27-arm64-Readme.md)
and the [fixed Nix installer Action](https://github.com/DeterminateSystems/determinate-nix-action/tree/v3.22.2).
