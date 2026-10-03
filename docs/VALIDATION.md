# Validation record

Environment checked on 2026-10-03: Apple Silicon, Xcode 27.0 (27A266a),
Apple Swift 6.4, iPhoneSimulator SDK 27.0 (24A430), iOS 27.0 Simulator runtime
(24A434), iPhone 18 Pro (arm64). `nix develop -c just doctor` checked the exact
versions and available device. `flake.lock` pins nixpkgs and SnapshotTesting.

| Command or check | Result |
| --- | --- |
| `nix develop -c just prepare-deps` | Pass; Nix-fixed SnapshotTesting source copied to `.prepared`. |
| `nix develop -c just format` twice | Pass; second run changed no Swift, Python, Nix, JSON or just files. |
| `nix develop -c just check` | Pass; formatting, SwiftLint, Ruff, yamllint, actionlint, CLI tests, iOS library build, unit tests, copy install test and image comparison. |
| Xcode Preview canvas | Pass with iPhone 18 Pro; light, dark, Collection and adjusted theme rendered. |
| Swift Package result bundles | Unit: 5 passed; copied Package: 1 passed; visual target: 6 tests passed, comparing 10 PNGs. |
| Clean checkout | Pass; cloned the committed repository into a separate directory, then ran `nix develop -c just doctor`, `nix develop -c just prepare-deps` and `nix develop -c just check`. No tracked files changed. |

The 10 committed reference PNGs came from `just record-snapshots` on the
specified Simulator. Their light/dark catalogs, error inputs, 320 pt Increased
Contrast and accessibility text examples, Japanese/English content, and List
composition were opened and visually checked for clipping, hierarchy, text
contrast and action sizing. The Xcode canvas was also inspected in all four
Preview variants. See the image paths in `tools/snapshots.json`.

Negative checks performed and then reverted: a SwiftLint force unwrap made
`just lint` fail; a formatting violation made `just format-check` fail; a
missing baseline failed the snapshot preflight; a falsified runtime build
failed `doctor`; a one-point card radius change failed image comparison and
produced expected/actual/diff PNGs plus an xcresult failure. The restored
source and normal comparison passed afterward.

The GitHub Actions workflow is defined and validated by actionlint. No remote
is configured, and the workflow has not run on a CI host. Manual VoiceOver,
keyboard traversal and actual network-backed app behavior are outside the
Package-only validation.
