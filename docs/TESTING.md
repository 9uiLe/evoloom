# Testing and baseline review

Run `nix develop -c just check-fast` for formatting, lint and Python/CLI
tests. Run `nix develop -c just prepare-deps`, then `nix develop -c just check`
for the complete local suite (`check-full` is an alias). The root Package
contains only the library product, so ordinary SwiftPM use needs no prepared
test dependency. The development Package under `Testing/` places unit and
image tests in one test target and `just test-ios` runs all 15 methods in one
XCTest session. Unit tests cover token contrast, Bindings and the Button action
gate. Python tests cover registry closure, copy imports, cycles, dry-run,
conflict protection, unsafe paths and CI selection. `verify-copy-install`
creates a temporary Package containing every copied component and builds its
library for the iOS Simulator without a separate test runner. The former copy
test only asserted the default spacing value; that assertion remains in the
unit tests, while the copy build covers Swift compilation of all copied files.
It does not exercise copied controls at runtime. Each Xcode command retains
its 600-second failure timeout. An optional `just prepare-simulator` requests
boot of the fixed device for diagnosis. Cloud trials found no overall gain,
so the normal full check leaves startup to Xcode. The recorded boot request
time does not assert that testmanagerd or the runner is ready.
Xcode tests explicitly use `-testLanguage en -testRegion US`; the SwiftUI
fixtures then set `en_US` or `ja_JP` for their own content. This also fixes
native List typography and Japanese fallback fonts across a Japanese-language
local host and the English-language GitHub runner. Five baselines changed when
the test runner language was fixed. They were regenerated from the local iOS
Simulator, visually reviewed, and their PNG bytes matched the corresponding
actual images from [the failed Cloud comparison](https://github.com/9uiLe/evoloom/actions/runs/37173749612).

GitHub Actions uses a lightweight Linux job to select checks before installing
Nix. For PRs it compares from the merge base. For master pushes it compares
from the latest successful **full** validation ancestor, found from GitHub's
Jobs API; a documentation-only or partial success is never used as that base.
If that API, Git history or ancestor check is unavailable, the full suite runs.
This cumulative range makes it safe to cancel an older run when a newer commit
arrives, including a code commit followed by documentation only. Manual full
runs use a separate concurrency group so a push does not cancel them. The
constant `validation` job checks that all selected jobs succeeded; skipped
jobs are accepted only when no checks were selected. Its full-validation marker
step runs only after the complete selected suite passes, so a documentation
run cannot become the next comparison base or leave a required check pending.
The Linux static job runs independently of the macOS iOS job. The path matrix:

| Changed path | CI checks |
| --- | --- |
| README, design/contribution/license text, or `docs/*.md` only, with a validated ancestor | No Nix or tests; the aggregate job succeeds. |
| `Sources/`, root `Package.swift`, Nix, `justfile`, or workflow | Formatting, lint, CLI, combined iOS unit and snapshot tests, copied Package build. |
| Existing unit test source under `Testing/Tests/EvoloomSnapshotTests/` | Formatting, lint and filtered unit tests. |
| Existing snapshot test source or PNG under `Testing/` | Snapshot comparison; Swift edits also run formatting and lint. |
| Newly added Swift test source | Formatting, lint, unit and snapshot tests, so either kind of new test executes. |
| `Testing/Package.swift` | Complete suite. |
| CLI implementation or registry | Formatting, lint, CLI tests and copied Package build. |
| CLI test source | Formatting, lint and CLI tests. |
| Formatter/linter configuration | Formatting and lint. |
| Any unrecognized path or unavailable Git comparison | The complete suite. |

Multiple paths combine their checks. `workflow_dispatch` always runs the
complete suite. The path detector uses NUL-delimited Git output and treats
renames as a deletion plus an addition. iOS checks still require the fixed
Apple environment; unit and image tests require Nix-prepared SnapshotTesting.
The copied Package build does not. Local `nix develop -c just check` always
runs the complete suite. An independent `just build-package` command verifies
the product alone; the combined test build already compiles it and the Preview
fixtures in regular CI.
The optional manual `use_xcode_cache` input measures a pinned cache without
changing normal push checks. Cache hit or miss never skips compilation or
tests. Manual `build_diagnostics` prints Xcode's build timing summary and
compile commands so an incremental source-change run can be inspected. The CI
Job Summary and `TestResults/ci-report.json` record the checkout,
selected scope, cache state, action time, test count, 28 baselines and actual
render count. Image-save duration is measured in the Package comparison
callback or hosted capture test, depending on the case.
See [timing and cache evidence](CI_PERFORMANCE.md) for comparisons and limits.

The `EvoloomSnapshotTests` target in `Testing/Package.swift` depends on the
development-only `EvoloomReviewFixtures` target and stores 23 baselines under
`Testing/Tests/EvoloomSnapshotTests/__Snapshots__/`. Five collection cases use
`Testing/Host/Tests/HostedCollectionTests.swift` and its baseline directory.
The development app provides a scene/key window for native search and toolbar
effects. Both test sessions use the same fixed Simulator serially. Fixed-size
visual tests use a `UIHostingController` and SnapshotTesting's real PNG strategy.
They set 390 or 320 pt width, fixed height, scale 3, zero test safe area,
system fonts, light/dark appearance, explicit content size, `en_US` or
`ja_JP` locale and UTC timezone. Fixtures use constant data and a static
skeleton, with no network, random identifiers, clocks or animation. Exact
pixel comparison uses normalized RGBA bytes with no tolerance. The 23
Package images still compare inside XCTest with `SnapshotImageDiffing.swift`;
its callback saves actual images on success and expected/actual/diff on
mismatch. The five app-hosted tests use SnapshotTesting to capture the real
key window, then save actual PNGs without asserting pixel equality inside
XCTest. After hosted xcodebuild exits, `tools/compare_host_images.py` decodes
the baseline and actual PNGs with Nix-pinned Pillow and compares exact RGBA
dimensions and pixels. A mismatch writes `expected.png`, `actual.png` and
`diff.png` under `TestResults/SnapshotDiffs/<case>/` and makes the outer task
return nonzero. Both paths save actuals to `TestResults/Rendered/` without a
second render for PR images. The hosted xcresult records capture results;
`host-image-comparison.json` records the separate pixel result. A build
failure has no actual PNG; the CI report names missing images. Equal images
produce no diff files. The Package mismatch path and its separate Xcode
behavior remain as before; the observed termination stall was in the hosted
failure path.
The API follows the fixed [SnapshotTesting source](https://github.com/pointfreeco/swift-snapshot-testing/tree/1.18.9).

| Image test | Risk covered |
| --- | --- |
| `catalog-light`, `catalog-dark` | Standard appearance for every initial component; all button variants, disabled/loading/destructive role, Card, Badge variants, Switch, Alert, Empty, Separator, Skeleton. |
| `switch-states-dark`, `switch-states-dark-increased-contrast`, `switch-states-dark-ja` | Native Toggle on/off tracks, thumb position, state text and glyph in dark mode; Increased Contrast and Japanese labels. |
| `customized-tokens`, `customized-tokens-dark` | Strongly different Card backgrounds, default and supporting Card text, and an explicitly styled child in both appearances; also Button, Input, Badge, spacing, radius and operation height. |
| `inputs-light`, `inputs-dark` | Normal, error, disabled and long Input and TextArea content. Native focus border is implemented but not captured because keyboard and focus timing would add instability. |
| `compact-accessibility` | 320 pt width, accessibility medium text, Increased Contrast, long Card, Alert, Button, Badge and Empty copy. |
| `collection-light`, `collection-dark`, `collection-empty`, `collection-loading`, `collection-error` | The whole Preview `ExampleCollectionView` in a scene-backed app, including native NavigationStack, toolbar, search and List. Static images do not exercise the controls. |
| `collection-compact-accessibility` | Fixed 320 pt large-text layout and Increased Contrast. Native search/toolbar chrome is unreliable in this fixed host, so this case covers density and wrapping only. |
| `review-components-controls-*`, `review-components-feedback-*` | Two readable component pages in light/dark, covering labels, error, switch, disabled/loading, Card, Badge, Alert, Empty and Skeleton. |
| `review-settings-*` | Native Settings Form in light/dark and invalid-email/disabled-Save state. |
| `review-detail-*` | Detail/edit in light/dark and long Japanese notes at 320 pt. |
| `locale-ja`, `locale-en` | Japanese and English content. |

To record, run `nix develop -c just record-snapshots`. This is a deliberate
write operation; it places a short-lived marker under `.prepared` for the
Package test's record mode, then removes it. The hosted test always saves
actuals; only the recording command copies those five images to baselines.
The recorder checks that SnapshotTesting acknowledged the Package writes and
that all 28 expected PNGs exist across both baseline directories. Open every PNG at full size and inspect clipping,
tap area, contrast and hierarchy, particularly dark, error, narrow and large
text images. Review `TestResults/record.xcresult` and `host-record.xcresult`; commit the PNGs and
`tools/snapshots.json` together. Then run `nix develop -c just test-snapshot`.
Normal comparison prechecks every listed PNG, hashes them before and after,
and refuses new or changed baselines. Xcode's `.xcresult`, logs, actual PNGs,
hosted comparison report and available expected/actual/diff images are
retained under `TestResults/`; CI uploads them on failure and success. See [visual review](VISUAL_REVIEW.md)
for the Preview, PR images and first baseline review.

Before updating the Apple environment, select an exact Xcode build, SDK,
runtime build, device class and architecture, change the doctor expectations,
record fresh images, visually compare all old/new images, and document the
reason. Pixel images alone do not verify VoiceOver, focus movement, keyboard
operation, or double submission. Review those in an integrating app.
