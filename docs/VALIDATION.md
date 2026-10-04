# Validation record

Entries before the Evoloom rename describe results under the names and paths
used at the time. They are historical records, not current installation
instructions. Current commands and paths are in the README and the latest
validation entry below.

Environment checked on 2026-10-03: Apple Silicon, Xcode 27.0 (27A266a),
Apple Swift 6.4, iPhoneSimulator SDK 27.0 (24A430), iOS 27.0 Simulator runtime
(24A434), iPhone 18 Pro (arm64). `nix develop -c just doctor` checked the exact
versions and available device. At that baseline, `flake.lock` pinned nixpkgs
and SnapshotTesting. The product targeted iOS 26 with Swift tools 6.2; Xcode reported that
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

## Dark Toggle track, 2026-10-04

The dark `toggleOnBackground` semantic token now supplies a medium gray
on-state track to the native `IOSSwitch`; the light palette keeps its existing
primary track. `just record-snapshots` recorded 12 real PNGs. Only the existing
dark catalog image changed, and `switch-states-dark` was added to show on and
off together. Both images were opened at full size: the white thumb, gray on
track and darker native off track were distinguishable, with no clipped labels.
`nix develop -c just check` passed: format, lint, 7 CLI tests, 6 unit tests,
copied Package compilation and tests, and 8 visual test methods comparing 12
PNGs. Xcode 27.0 (27A266a), iOS Simulator 27.0 (24A434), iPhone 18 Pro arm64.

## AppMacros integration, 2026-10-04

`swift-app-macros` PR [#10](https://github.com/9uiLe/swift-app-macros/pull/10)
was merged to `master` as `c87f52673499ab71bac7e841290a5fa4261a8a0a`.
Its new `@AutoEquatableView` generates a comparison boundary for comparable
parent inputs and an ordinary body for actions, Bindings and arbitrary child
Views. Upstream `swift test --disable-automatic-resolution` passed 75 tests;
the iOS Simulator package build and 28 release-tool tests passed. Required PR
checks passed before merge. The merged-commit
[CI run](https://github.com/9uiLe/swift-app-macros/actions/runs/37145972806)
also completed successfully.

At integration time, this Package pinned that merged commit and swift-syntax
603.0.2 in `flake.lock`.
The Nix preparation creates local SwiftPM sources; Xcode builds and tests use
`-disableAutomaticPackageResolution`. A separate clean temporary consumer
resolved the public Package manifest to the pinned merged commit and exact
swift-syntax version. Its iOS Simulator Package build passed after adding
Xcode's `-skipMacroValidation` to the noninteractive verification command.
Without that flag, Xcode blocked a first-time external macro pending approval;
the failure was an approval gate, not a Swift compilation error. Manifest
checks also showed that an unprepared consumer
inside the Nix shell selects the public pin, while the prepared development
checkout selects the local Nix source.

`nix develop -c just check` passed on Xcode 27.0 (27A266a), iPhone 18 Pro
arm64, iOS Simulator 27.0 (24A434): format, lint, 7 CLI tests, iOS Package
build, 7 unit tests, copied Package build and 1 test, and 8 visual test methods
comparing 12 PNGs. The second formatter run changed no files, and a temporary
unused Python import made `just lint` fail with Ruff F401; it was reverted.
The existing PNG baselines stayed unchanged. The dark component catalog and
narrow accessibility Collection baseline were opened for visual review; labels
and operations were not clipped. SnapshotTesting 1.18.9 emitted deprecation
warnings when its prepared source rebuilt; the test result was Passed.

Static display components receive the equality boundary. Components with
Bindings, actions or arbitrary child Views receive the ordinary body fallback;
the macro is attached consistently, but no unsupported performance claim is
made for those components. The Preview source compiled with the library; the
Xcode canvas was not reopened in this integration.

## AppMacros 0.4.0 update, 2026-10-04

The [0.4.0 release](https://github.com/9uiLe/swift-app-macros/releases/tag/0.4.0)
points to commit `4146637f4d9cf59e5051840311063ddd45a1b316` and pins
swift-syntax 604.0.0. This Package now pins those sources in its public
manifest and Nix lock. `nix flake update appMacros swiftSyntax` produced the
new NAR hashes; `nix develop -c just prepare-deps` materialized both fixed
sources. With the local dependency mode disabled, `swift package resolve`
selected the release commit and swift-syntax 604.0.0, and an iOS Simulator
Package build succeeded with `-disableAutomaticPackageResolution`.

`nix develop -c just check` passed on Xcode 27.0 (27A266a), iPhone 18 Pro
arm64, iOS Simulator 27.0 (24A434). It covered format and lint, 7 CLI tests,
the library and Preview source build, 7 unit tests, copied Package build and
1 test, and 8 image test methods comparing the existing 12 PNGs. Unit, copy
and image `.xcresult` summaries reported zero failures. No component source
or image baseline changed. This update did not reopen the Xcode Preview canvas.

## Evoloom rename, 2026-10-04

The root Package, library product, Swift module, tests, visual test Package,
CLI and copy output use `Evoloom`. The Swift component files and design token
implementation moved directories without code changes. All 12 baseline PNGs
were moved to `Testing/Tests/EvoloomSnapshotTests` without byte changes; their
SHA-256 hashes match the former files. No image was re-recorded and no
intentional visual difference was introduced. The public `IOS…` API remains.

`nix develop -c just prepare-deps` and `nix develop -c just check` passed on
Xcode 27.0 (27A266a), iPhone 18 Pro arm64, iOS Simulator 27.0 (24A434). The
check covered format, lint, 10 CLI tests, the library and Preview compilation,
7 root unit tests, the copied Package build and 1 test, and 8 visual methods
comparing 12 PNGs. The unit, copy and visual xcresult summaries reported zero
failures. Two consecutive `just format` runs left the second run unchanged.
A separate temporary ordinary consumer resolved the public `swift-app-macros`
commit and swift-syntax 604.0.0 from SwiftPM cache and built the `Evoloom`
library for the iOS Simulator without `.prepared` or the local dependency
environment variable. This consumer check intentionally used the regular
SwiftPM path; Nix still fixes the development and test dependencies.
A separate clone of the local rename commit then ran
`nix develop -c just doctor`, `nix develop -c just prepare-deps` and
`nix develop -c just check` successfully; its tracked working tree stayed
clean.

The old `.shadcn-ios.json` and `Sources/ShadcnIOSCopied` paths now stop the
CLI before any install, even with `--overwrite`. Tests verify that customized
bytes remain unchanged. `LICENSE` and its original contributor notice were
preserved. `flake.lock`, dependency revisions, component rendering and visual
baseline bytes did not change. The Xcode Preview canvas was not reopened for
this rename; its source compiled as part of the library. Remote GitHub rename,
push and CI execution were not performed for this local change.

## Public GitHub-hosted CI, 2026-10-04

The repository is now [9uiLe/evoloom](https://github.com/9uiLe/evoloom),
public, with `master` as the default branch. Commit `ac8be8a` on `master`
introduced changed-path CI selection and an explicit Xcode test language and
region. The [GitHub-hosted full run](https://github.com/9uiLe/evoloom/actions/runs/37175410424)
passed on the pinned `xcode-27` ARM64 runner. Its archived xcresult summaries
report 7 root Package tests, 1 copied Package test and 8 visual test methods,
all passed with zero failures. The visual methods compared 12 real PNG
baselines; the artifact contained no diff images. Format, lint, CLI tests and
the iOS library build also passed in that run.

Locally, `nix develop -c just check` passed after the same change. The
changed-path detector's 15 Python/CLI tests passed, including documentation
only, each test area, combined paths, an unknown path and a source-to-docs
rename. Five baselines were re-recorded after setting
`-testLanguage en -testRegion US`. Their PNG bytes matched the earlier Cloud
actual images, and light, dark, compact accessibility and Japanese output were
reviewed.
The visual comparator still requires exact pixel equality.

## Dark switch state clarity, 2026-10-04

The native `IOSSwitch` now displays a localized On/Off status and a filled or
empty circle beside its setting label in dark appearance. The selected gray
track token was lightened from 0.54/0.54/0.56 to 0.58/0.58/0.60; the light
palette stayed unchanged. The same visible status appears when Differentiate
Without Color is enabled. The status is hidden from accessibility so the
native Toggle remains the spoken control. Apple, Material, Carbon and Fluent
guidance used for this design choice is linked from `DESIGN.md`.

`nix develop -c just record-snapshots` generated 14 real PNGs on Xcode 27.0
(27A266a), iPhone 18 Pro arm64, iOS Simulator 27.0 (24A434). The existing
dark catalog and switch comparison images changed as expected; dark Increased
Contrast and Japanese switch images were added. All four affected images were
opened and checked for state separation, clipping and label legibility. The
normal `nix develop -c just check` passed, including format, lint, 15 CLI
tests, iOS library and Preview source compilation, 7 unit tests, the copied
Package build and 1 test, and 8 visual methods comparing all 14 PNGs. The
unit, copy and image result bundles reported zero failures. Two formatter
runs left the second run unchanged. The Xcode Preview canvas and manual
VoiceOver interaction were not opened for this change.

## Card tokens, copy dependencies and shared Collection fixture, 2026-10-04

`IOSCard` now supplies `cardForeground` to its child content while respecting
children with explicit styles. `IOSCardHeader` applies that color to its title
and uses the new `cardMutedForeground` for supporting text. The new initializer
argument is optional; existing palette calls remain source-compatible. The
light and dark customized-token images use strongly different card surfaces,
show default and supporting text, and include an explicitly colored child.
Both images were opened at full size; the title, supporting text and child
colors remained distinct and readable. The neutral light/dark catalogs,
compact accessibility image, and Collection normal/empty/loading/error images
were also opened. The Collection images use the same internal `CollectionContent`
as the Preview's interactive screen; they omit the navigation bar, searchable
field, destination and sheet. The loading state gives the screen a visible
"Loading items" element while `IOSSkeleton` remains decorative.

The former `@AutoEquatableView` boundary covered five display-only components;
the six components with Bindings, actions or child Views used the macro's
ordinary-body fallback. Components now use ordinary SwiftUI `body`. The root
manifest has no external Swift package dependencies; `xcrun swift package
dump-package` reported `dependencies: []` and tools version 6.2. Nix still pins
SnapshotTesting 1.18.9 for the separate visual test Package. `nix flake lock`
removed only the former AppMacros and swift-syntax inputs; nixpkgs and
SnapshotTesting revisions remained fixed. The copy-install test compiled and
tested a copied Package without either macro package.
With the prepared SnapshotTesting directory temporarily hidden, the Nix
`just build-package` command still passed, while `just test-snapshot` failed
with an explicit `just prepare-deps` instruction. The directory was restored.

On Apple Silicon macOS 27.0 build 26A428, Xcode 27.0 (27A266a), iPhone 18 Pro
arm64 and iOS Simulator 27.0 (24A434), `nix develop -c just prepare-deps`,
`just format-check`, `just lint`, and `just check` passed. The full check ran
15 Python/CLI tests, the iOS library and Preview source build, 6 root unit
tests, the copied Package build and 1 test, and 8 visual test methods comparing
18 real PNGs. Result bundles reported zero failures. Two consecutive formatter
runs changed no files. Recording and comparison were separate commands. A
temporary Card foreground regression made both customized-theme comparisons
fail with expected/actual/diff PNGs; after restoring the source, normal
comparison passed. Hiding one baseline made comparison fail before Xcode and
did not recreate the image. The Xcode Preview canvas, manual VoiceOver flow,
keyboard operation, search and sheet interactions were not run for this change.

## Development app host for visual review, 2026-10-04

On the fixed local Xcode 27.0 (27A266a), SDK 27.0 (24A430), iOS 27.0 runtime
(24A434), iPhone 18 Pro arm64 and macOS build 26A428, Nix provided XcodeGen
2.44.1. `just prepare-host` generated an ignored project from
`Testing/Host/project.json`; its app built and launched without signing. The
app uses the existing fixture module and preserves the root library Package.
The Simulator's actual light and dark Collection displays showed a legible
plus symbol and search icon/field. Hosted `drawHierarchyInKeyWindow` images
showed the same native chrome. The simulator screenshot includes status-bar
glyphs; the snapshot leaves them out but retains the actual top and bottom
safe-area layout at 1206 × 2622 px. An empty-state launch displayed the selected fixture.
Canvas remains unverified.

Five collection baselines were deliberately re-recorded in the app host. The
other 23 PNGs retained their fixed-host paths and pixels. A one-session
app-host experiment changed seven unrelated fixed-size cases, so the active
matrix keeps two serial sessions. `just test-ios` passed 15 Package methods
and five app-host methods; `just test-snapshot` passed nine and five methods;
each comparison saved 28 actual PNGs with no baseline change. `just
check-fast`, `just build-package`, and `just verify-copy-install` passed
locally. A hosted baseline removed temporarily was rejected before build and
then restored. A temporary altered baseline produced `expected.png`,
`actual.png` and `diff.png`. Xcode 27.0 then stalled more than five minutes
while cleaning up the failed hosted test; it was terminated, so a natural
nonzero test exit was not observed in this local trial. The normal task has a
600-second Xcode timeout and CI keeps the rendered diffs even when it trips.
`just check` passed after the baseline was restored. No
appearance token or product dependency changed.

Apple documents native JSON `project.xcproj` support from Xcode 27, with 27.2
as the new-format default. Installed Xcode 27.0 did not expose the Project
Format control or accept `xcodebuild -convert-project xcproj`; native JSON was
not validated. The checked-in JSON is an XcodeGen spec, not `.xcproj`.

## Hosted image mismatch termination, 2026-10-04

The earlier five-minute stall above remains a record of the old in-test
failure path. A second one-case diagnostic changed fixed Collection copy and
ran only `testCollectionLight`. On the same pinned local Apple environment,
the actual PNG appeared 39.6 seconds after xcodebuild started, and the diff
appeared at 42.1 seconds. The command was still running 60 seconds after the
diff; a process sample showed xcodebuild waiting for the test operation. The
diagnostic ended that process group at 117.1 seconds and restored the fixture.
This locates the observed wait after image comparison, but it does not prove
which Xcode, XCTest or SnapshotTesting internal operation caused it.

Hosted XCTest now captures and saves the real-window image without asserting
pixel equality. After xcodebuild exits, `tools/compare_host_images.py` decodes
both PNGs to RGBA, compares dimensions and pixels exactly, writes
expected/actual/diff for a mismatch, and fails the outer task. Pillow 12.3.0
is supplied by the existing pinned nixpkgs revision. Package-only snapshots
still use their Swift exact-pixel comparison. The 28 baselines and product
sources did not change.

In a targeted changed-copy trial, hosted xcodebuild exited 0 after 19.5
seconds; the external comparison reported a pixel mismatch and produced the
three images 0.25 seconds later. Its CLI returned 1. A separate full
`test-snapshot` trial changed only the light hosted case; all 14 XCTest methods
passed, 28 actual PNGs were saved, and the outer command exited 1 with only
`collection-light` mismatching after 47.5 seconds. After restoring that line,
`test-snapshot` passed with all five hosted images matching and no stale diff.
These are warm local observations under different build inputs, not a general
performance estimate. CI failure-path and artifact verification are recorded
separately when the temporary Cloud run completes.
