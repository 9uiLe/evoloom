# Validation record

Environment checked on 2026-10-03: Apple Silicon, Xcode 27.0 (27A266a),
Apple Swift 6.4, iPhoneSimulator SDK 27.0 (24A430), iOS 27.0 Simulator runtime
(24A434), iPhone 18 Pro (arm64). `nix develop -c just doctor` checked the exact
versions and available device. `flake.lock` pins nixpkgs and SnapshotTesting.
The product now targets iOS 26 and uses Swift tools 6.2; Xcode reported that
`.iOS(.v26)` is unavailable with the former 6.0 manifest.

| Command or check | Result |
| --- | --- |
| `nix develop -c just prepare-deps` | Pass; Nix-fixed SnapshotTesting source copied to `.prepared`. |
| `nix develop -c just format` twice | Pass; second run changed no Swift, Python, Nix, JSON or just files. |
| `nix develop -c just check` | Pass; formatting, SwiftLint, Ruff, yamllint, actionlint, CLI tests, iOS library build, unit tests, copy install test and image comparison. |
| Xcode Preview canvas | Pass with iPhone 18 Pro; light, dark, Collection and adjusted theme rendered. |
| Swift Package result bundles | Unit: 5 passed; copied Package: 1 passed; visual target: 6 tests passed, comparing 10 PNGs. |
| Distribution tests | 6 passed, including a guard against `add` before license/config initialization. |
| iOS 26.5 runtime | Root Package tests: 5 passed on iPhone 17 Pro, runtime build 23F77, using Xcode 27.0. This was a separate run; image baselines remain fixed to iOS 27.0. |
| Clean checkout | Pass; cloned the committed repository into a separate directory, then ran `nix develop -c just doctor`, `nix develop -c just prepare-deps` and `nix develop -c just check`. No tracked files changed. |

The 10 committed reference PNGs came from `just record-snapshots` on the
specified Simulator. Their light/dark catalogs, error inputs, 320 pt Increased
Contrast and accessibility text examples, Japanese/English content, and List
composition were opened and visually checked for clipping, hierarchy, text
contrast and action sizing. The Xcode canvas was also inspected in all four
Preview variants. See the image paths in `tools/snapshots.json`.
The long-copy review exposed truncated Empty State text; the component now
lets its title and description grow vertically. The final record command
passed with 10 real PNGs, and the subsequent normal comparison passed.

Negative checks performed and then reverted: a SwiftLint force unwrap made
`just lint` fail; a formatting violation made `just format-check` fail; a
missing baseline failed the snapshot preflight; a falsified runtime build
failed `doctor`; a one-point card radius change failed image comparison and
produced expected/actual/diff PNGs plus an xcresult failure. The restored
source and normal comparison passed afterward.

The GitHub Actions workflow is defined and validated by actionlint. Its
self-hosted runner execution has not been verified. Manual VoiceOver,
keyboard traversal and actual network-backed app behavior are outside the
Package-only validation.

## Design token refactor, 2026-10-04

The neutral values moved to `Sources/ShadcnIOS/Tokens/DesignTokens.swift`.
Components now read `iosDesignTokens` and share color, spacing, radius,
typography and control dimensions. Legacy Swift API names remain aliases.
The copy registry includes `tokens`, and the CLI refuses an old copied
`Theme/Theme.swift` until the user migrates it explicitly.

`nix develop -c just build-package`, `just format-check`, `just lint`,
`just test-unit`, `just verify-copy-install`, and `just check` passed with
Xcode 27.0 (27A266a) and the fixed iPhone 18 Pro iOS 27.0 Simulator. The
result bundles report 6 unit tests and 7 visual test methods passed; 7 CLI
tests passed. Two consecutive `just format` runs produced the same file
hashes, and format-check and lint reported no violations.
`just record-snapshots` produced 11 real PNGs, and the 10
existing reference images remained byte-identical after correcting the
TextArea scaling formula. The new `components.customized-tokens.png` was
opened at full size, along with the existing dark catalog and 320 pt
accessibility image. The custom primary, spacing and input radius were visible;
labels and supporting text remained legible.

A separate clean `master` clone ran `nix develop -c just prepare-deps` and
`nix develop -c just check` successfully. Its tracked working tree stayed
clean. SnapshotTesting itself emitted iOS deprecation warnings on that first
build; the Package and visual tests still passed.

A temporary one-point radius change in the customized fixture made
`testCustomizedDesignTokens` fail with Xcode exit code 65. Its expected,
actual and diff PNGs showed the changed Button and Input corners. The change
was reverted. The normal comparison passed afterward. The Preview source
compiled as part of the library build; the Xcode canvas was not reopened for
this refactor. The workflow remains configured for `master` pushes, but a
successful remote CI run has not been observed.
