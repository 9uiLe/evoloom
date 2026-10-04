# Fixed environment and dependency boundary

`flake.lock` records immutable revisions and NAR hashes for all Nix inputs:

| Source | Fixed version / revision | Use |
| --- | --- | --- |
| nixpkgs | `44a91898084f46797b5fac650c7e8c9ac38c43d4` | SwiftLint 0.65.1, SwiftFormat 0.63.0, just 1.58.0, Python 3.14.7, Ruff 0.16.8, nixfmt 1.5.0, yamllint 1.37.1, actionlint 1.7.12 |
| swift-app-macros | `0.4.0`, revision `4146637f4d9cf59e5051840311063ddd45a1b316` | `AppMacros` and `@AutoEquatableView` |
| swift-syntax | `604.0.0`, revision `050f1a346fbbac0ca2cfb15a95274f7bd1cf0ccf` | Macro compiler plugin and its local Swift module graph |
| swift-snapshot-testing | `1.18.9`, revision `bf8d8c27f0f0c6d5e77bff0db76ab68f2050d15d` | Test-only image comparison |

Run `nix develop`, then `just prepare-deps`. That preparation copies the
Nix-fixed sources to ignored `.prepared/` local Swift packages and records the
selected Nix store paths in `.prepared/sources.json` after copying finishes.
Build and test commands reject missing or stale preparation, including files
left from an earlier `flake.lock`; rerun `just prepare-deps` after updating the
lock. The AppMacros manifest contains only its product and compiler plugin and
points to the prepared swift-syntax source. The pinned swift-syntax package has
no remote SwiftPM dependencies. SnapshotTesting is reduced to
its image comparison module, excluding its optional sibling products and their
transitive dependencies. Its prepared manifest uses Swift 5 language mode,
matching the upstream manifest on this Xcode. The root product uses Swift
tools 6.3, required by the pinned macro package; the visual test harness uses
tools 6.2. `Package.swift` selects local AppMacros only when
`EVOLOOM_LOCAL_DEPS=1` is set by the Nix shell and the prepared macro
manifest exists beside the root manifest. For normal consumers, including a
clone opened inside that shell without `.prepared`, it pins the upstream Git
commit through SwiftPM and remains readable. The `just` build and test tasks
still fail explicitly if developer dependencies have not been prepared.
The normal consumer path lets SwiftPM resolve the macro's exact swift-syntax
version; Nix controls developer and CI resolution through local paths.

Apple prerequisites remain outside Nix: macOS on arm64; Xcode 27.0 build
27A266a at `/Applications/Xcode-27.0.0.app/Contents/Developer`; Apple Swift
6.4; iPhoneSimulator SDK 27.0 build 24A430; iOS 27.0 Simulator runtime build
24A434; an available iPhone 18 Pro. `just doctor` checks exact versions,
runtime build, device and architecture. It does not change the system-wide
Xcode selection. The Nix shell sets `DEVELOPER_DIR` and clears `SDKROOT` so
`xcrun` uses the chosen Apple toolchain and SDK. Build commands also remove
Nix compiler and SDK variables and put Xcode's toolchain first on `PATH`.
These Apple artifacts, Simulator pixels and Xcode license are outside the Nix
lock.

The product deployment target is iOS 26. The root Package unit tests also
ran on the installed iOS 26.5 runtime (build 23F77) with an iPhone 17 Pro in
the earlier baseline validation. Pinned image baselines and `just check` use
iOS 27.0; the iOS 26.5 run is separate.

Preparation and execution are separate. `just prepare-deps` is the only step
that materializes external Swift source. Development and CI Xcode commands use
`-disableAutomaticPackageResolution` and local package paths. Missing or stale
prepared sources fail with a preparation instruction. They use Xcode's
`-skipMacroValidation` because CI cannot accept an interactive macro approval;
the macro source is pinned by Nix's NAR hash and reviewed before the check.
Xcode's local help documents that this flag bypasses macro validation. To
verify a clean checkout,
clone to another directory, run `nix develop`, `just doctor`,
`just prepare-deps`, then `just check` on the specified Apple host. A missing
tool or mismatched Simulator fails before tests.

References: [Nix manual](https://nixos.org/manual/nix/stable/),
[SwiftLint](https://github.com/realm/SwiftLint),
[SwiftFormat](https://github.com/nicklockwood/SwiftFormat),
[AppMacros](https://github.com/9uiLe/swift-app-macros),
[swift-syntax](https://github.com/swiftlang/swift-syntax), and
[SnapshotTesting](https://github.com/pointfreeco/swift-snapshot-testing).
