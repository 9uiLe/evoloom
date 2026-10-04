# Testing and baseline review

Run `nix develop -c just prepare-deps`, then `nix develop -c just check`.
The root Package unit target checks token boundaries and foreground/background
contrast. Python tests check registry closure, cycles, dry-run, conflict
protection and unsafe paths. `verify-copy-install` creates a temporary Package
from copied source, compiles it for the iOS Simulator and runs a test.

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
| `switch-states-dark` | Native Toggle on/off tracks in dark mode; the on track uses the gray semantic token. |
| `customized-tokens` | A single changed token set propagates to Button, Card, Input and Badge, including color, spacing, radius and operation height. |
| `inputs-light`, `inputs-dark` | Normal, error, disabled and long Input and TextArea content. Native focus border is implemented but not captured because keyboard and focus timing would add instability. |
| `compact-accessibility` | 320 pt width, accessibility medium text, Increased Contrast, long Card, Alert, Button, Badge and Empty copy. |
| `collection-light`, `collection-dark`, `collection-compact-accessibility` | A representative native List composition in regular, dark and narrow accessibility configurations. Navigation, search and sheet interaction are covered by Preview, not by a static image. |
| `locale-ja`, `locale-en` | Japanese and English content. |

To record, run `nix develop -c just record-snapshots`. This is a deliberate
write operation; it places a short-lived marker under `.prepared` so the
Simulator test process enters record mode, then removes it. The recorder checks
that SnapshotTesting acknowledged each intentional write and that all twelve
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
