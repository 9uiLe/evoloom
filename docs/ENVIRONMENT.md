# Fixed environment and dependency boundary

`flake.lock` fixes nixpkgs at `44a91898084f46797b5fac650c7e8c9ac38c43d4`
with its NAR hash and SnapshotTesting 1.18.9 at
`bf8d8c27f0f0c6d5e77bff0db76ab68f2050d15d` with its NAR hash.
`nix develop` supplies SwiftLint 0.65.1, SwiftFormat 0.63.0, just 1.58.0,
Python 3.14.7, Ruff 0.16.8, nixfmt 1.5.0, yamllint 1.37.1 and actionlint
1.7.12. Python also formats the two JSON manifests; just formats its own
task file. The snapshot dependency is
fetched by Nix, then `just prepare-deps` copies its `SnapshotTesting` module
to `.prepared/` and gives it a local SwiftPM manifest. That module has no
source imports from the upstream package's `InlineSnapshotTesting` or
`SnapshotTestingCustomDump` modules; those products and their transitive
`swift-syntax` and `swift-custom-dump` dependencies are excluded. The
generated manifest uses Swift 5 language mode, matching the upstream manifest
on this Xcode. The root product manifest has no external dependency. The
product, visual-test and prepared dependency manifests use Swift tools 6.2
because Xcode reports that `PackageDescription` exposes `.iOS(.v26)` starting
with that version.

Apple prerequisites remain outside Nix: macOS on arm64; Xcode 27.0 build
27A266a at `/Applications/Xcode-27.0.0.app/Contents/Developer`; Apple Swift
6.4; iPhoneSimulator SDK 27.0 build 24A430; iOS 27.0 Simulator runtime build
24A434; an available iPhone 18 Pro. `just doctor` checks exact versions,
runtime build, device and architecture. It does not change the system-wide
Xcode selection. The Nix shell sets `DEVELOPER_DIR` and clears `SDKROOT` so
`xcrun` uses the chosen Apple toolchain and SDK; Nix's Swift build support is
not used for iOS. These Apple artifacts, Simulator pixels and Xcode license
are not reproducible from `flake.lock`.

The product's deployment target is iOS 26. The root Package unit tests also
ran on the installed iOS 26.5 runtime (build 23F77) with an iPhone 17 Pro.
The pinned image baselines and `just check` continue to use iOS 27.0; the
iOS 26.5 run is separate from that image comparison.

Preparation and test execution are separate. `just prepare-deps` is the only
step that materializes external Swift source. The test harness depends on
local paths only. Xcode commands use `-disableAutomaticPackageResolution`;
absence of `.prepared/SnapshotTesting` is an explicit error. To verify a
clean checkout, clone to another directory, run `nix develop`, `just doctor`,
`just prepare-deps`, then `just check` on the specified Apple host. A missing
tool or mismatched Simulator fails before tests.

References: [Nix manual](https://nixos.org/manual/nix/stable/),
[SwiftLint](https://github.com/realm/SwiftLint),
[SwiftFormat](https://github.com/nicklockwood/SwiftFormat), and
[SnapshotTesting](https://github.com/pointfreeco/swift-snapshot-testing).
