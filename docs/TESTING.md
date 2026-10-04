# Testing and baseline review

Run `nix develop -c just prepare-deps`, then `nix develop -c just check`.
The root Package unit target checks token boundaries, Card supporting text
contrast, Bindings and the Button action gate. Python tests check registry
closure, copy source imports, cycles, dry-run, conflict protection and unsafe
paths. `verify-copy-install` creates a temporary Package from copied source,
compiles it for the iOS Simulator and runs a test without AppMacros.
Each Xcode command has a 600-second failure timeout. On the first GitHub-hosted
run, the copied Package test reached its test case just before the former
240-second limit; the runner's cold Simulator startup required a longer bound.
The timeout does not delay a completed test.
Xcode tests explicitly use `-testLanguage en -testRegion US`; the SwiftUI
fixtures then set `en_US` or `ja_JP` for their own content. This also fixes
native List typography and Japanese fallback fonts across a Japanese-language
local host and the English-language GitHub runner. Five baselines changed when
the test runner language was fixed. They were regenerated from the local iOS
Simulator, visually reviewed, and their PNG bytes matched the corresponding
actual images from [the failed Cloud comparison](https://github.com/9uiLe/evoloom/actions/runs/37173749612).

GitHub Actions compares the changed paths for pushes and pull requests before
installing Nix. It runs only the checks affected by those paths:

| Changed path | CI checks |
| --- | --- |
| README, design/contribution/license text, or `docs/*.md` only | No Nix or tests; the change-detection job still succeeds. |
| `Sources/`, root `Package.swift`, Nix, `justfile`, or workflow | Formatting, lint, CLI, iOS build, unit, copied Package and snapshots. |
| `Tests/` | Formatting, lint and Package unit tests. |
| `Testing/` | Snapshot comparison; Swift or manifest edits also run formatting and lint. |
| CLI implementation or registry | Formatting, lint, CLI tests and copied Package. |
| CLI test source | Formatting, lint and CLI tests. |
| Formatter/linter configuration | Formatting and lint. |
| Any unrecognized path or unavailable Git comparison | The complete suite. |

Multiple paths combine their checks. `workflow_dispatch` always runs the
complete suite. The path detector uses NUL-delimited Git output and treats
renames as a deletion plus an addition so a source removal cannot be hidden by
a move into a documentation path. iOS checks still require the fixed Apple
environment and Nix-prepared dependencies. Local `nix develop -c just check`
always runs the complete suite.

The `EvoloomSnapshotTests` target in `Testing/Package.swift` stores its
baselines under `Testing/Tests/EvoloomSnapshotTests/__Snapshots__/`.
Visual tests use a `UIHostingController` and SnapshotTesting's real PNG image
strategy. They set 390 or 320 pt width, fixed height, scale 3, zero safe area,
system fonts, light/dark appearance, explicit content size, `en_US` or
`ja_JP` locale and UTC timezone. Fixtures use constant data and a static
skeleton, with no network, random identifiers, clocks or animation. Exact
pixel comparison uses normalized RGBA bytes with no tolerance. SnapshotTesting
handles rendering and baseline naming. Its standard three-attachment image
diff stalled Xcode 27's Package test runner on a mismatch in this environment,
so the test supplies an exact diff that writes `expected.png`, `actual.png` and
`diff.png` under `TestResults/SnapshotDiffs/<case>/`. The xcresult records the
failure and paths. Equal images produce no diff files.
The API follows the fixed [SnapshotTesting source](https://github.com/pointfreeco/swift-snapshot-testing/tree/1.18.9).

| Image test | Risk covered |
| --- | --- |
| `catalog-light`, `catalog-dark` | Standard appearance for every initial component; all button variants, disabled/loading/destructive role, Card, Badge variants, Switch, Alert, Empty, Separator, Skeleton. |
| `switch-states-dark`, `switch-states-dark-increased-contrast`, `switch-states-dark-ja` | Native Toggle on/off tracks, thumb position, state text and glyph in dark mode; Increased Contrast and Japanese labels. |
| `customized-tokens`, `customized-tokens-dark` | Strongly different Card backgrounds, default and supporting Card text, and an explicitly styled child in both appearances; also Button, Input, Badge, spacing, radius and operation height. |
| `inputs-light`, `inputs-dark` | Normal, error, disabled and long Input and TextArea content. Native focus border is implemented but not captured because keyboard and focus timing would add instability. |
| `compact-accessibility` | 320 pt width, accessibility medium text, Increased Contrast, long Card, Alert, Button, Badge and Empty copy. |
| `collection-light`, `collection-dark`, `collection-compact-accessibility`, `collection-empty`, `collection-loading`, `collection-error` | The `CollectionContent` List used by `ExampleCollectionView`, including normal/empty/loading/error states and narrow large text. Snapshot host supplies a NavigationStack with its bar hidden. Search UI, toolbar, destination and sheet are omitted; Preview provides a manual path to those controls, not an automated interaction test. |
| `locale-ja`, `locale-en` | Japanese and English content. |

To record, run `nix develop -c just record-snapshots`. This is a deliberate
write operation; it places a short-lived marker under `.prepared` so the
Simulator test process enters record mode, then removes it. The recorder checks
that SnapshotTesting acknowledged each intentional write and that all eighteen
expected PNGs exist. Open every baseline PNG at full size and inspect clipping,
tap area, contrast and hierarchy, particularly dark, error, narrow and large
text images. Review `TestResults/record.xcresult` and commit the PNGs and
`tools/snapshots.json` together. Then run `nix develop -c just test-snapshot`.
Normal comparison prechecks every listed PNG, hashes them before and after,
and refuses new or changed baselines. Xcode's `.xcresult` and the library's
expected/actual/diff attachments are retained under `TestResults/` and CI
uploads them on failure.

Before updating the Apple environment, select an exact Xcode build, SDK,
runtime build, device class and architecture, change the doctor expectations,
record fresh images, visually compare all old/new images, and document the
reason. Pixel images alone do not verify VoiceOver, focus movement, keyboard
operation, or double submission. Review those in an integrating app.
