# Reviewing representative screens

The root `Evoloom` Swift Package remains the product. `Testing/Sources/EvoloomReviewFixtures/` holds fixed Preview and review views. `Testing/Host/` is a development-only app with a real scene and key window; it imports the same fixture product and is never distributed with the library or copied components. `Testing/Host/project.json` is the checked-in XcodeGen definition. `just prepare-host` generates an ignored `.xcodeproj` with the Nix-pinned XcodeGen. No fixture source is copied into the app.

The host was added because the package test process had no connected scene. A plain native `NavigationStack`/`List`/`searchable`/toolbar reproduced white search and plus glyphs on a light background; `drawHierarchy` there returned a black image. With the app scene, the glyphs and search field are visible in both the simulator display and `drawHierarchyInKeyWindow` snapshot. No component tint or token was changed to mask the capture problem. See the [SnapshotTesting host discussion](https://github.com/pointfreeco/swift-snapshot-testing/discussions/1031).

## Display and capture

```sh
nix develop -c just prepare-deps
nix develop -c just prepare-host
nix develop -c just run-host collection normal light
nix develop -c just run-host collection normal dark
nix develop -c just run-host collection error light
nix develop -c just run-host settings normal light
nix develop -c just test-snapshot
```

`run-host` builds, installs and launches the app on the exact simulator selected by `just doctor`. The first argument is `collection`, `controls`, `feedback`, `settings`, `settingsError`, `settingsJapanese`, `settingsJapaneseError`, `detail`, `detailJapanese`, `detailLongNotes`, `buttonFlow` or `buttonFlowJapanese`; the second is a collection state (`normal`, `empty`, `loading`, `error`); the third is `light` or `dark`. `detailLongNotes` is a development-only route with fixed overflowing TextEditor content for internal scroll review. Open Xcode 27's Device Hub to inspect the app. After its view appears, `xcrun simctl io <doctor-UDID> screenshot <path>.png` captures the entire display. An immediate screenshot after launch can capture a blank frame; wait for the view, without a fixed long sleep.

For Canvas, open `Testing/Package.swift`, select iPhone 18 Pro and a named `#Preview` in the fixture sources. Xcode 27.0 Canvas previously failed to resolve Evoloom on this machine. The app display and simulator tests are verified alternatives; Canvas has not been reverified after this change.

`just test-ios` executes package unit and fixed-size image tests, then five scene-backed collection images, serially on the same simulator. `just test-snapshot` runs only the two image groups. Combining all tests into the app session was tried: seven old fixed-size cases changed solely from the host context. Keeping those baselines avoids re-recording unrelated settings, detail and narrow images. The collection 320 pt large-text case remains a fixed-size layout test; its native chrome is **not** used to judge contrast.

Scene-backed list cases use an iPhone 18 Pro window at 402 × 874 pt, 3× (1206 × 2622 px), real safe area, system fonts, `en_US`, UTC, standard Dynamic Type and explicit light/dark appearance. The snapshot captures app content without status bar glyphs. The fixed-size cases use a `UIHostingController`, 390 or 320 pt width, specified height, 3×, zero test safe area and explicit locale, Dynamic Type and appearance. Both modes require macOS 27.0 build 26A428, Xcode 27.0 build 27A266a, SDK 27.0 build 24A430, iOS 27.0 runtime build 24A434 and arm64. `just doctor` rejects a mismatch.

| Screen | Image cases | Purpose |
| --- | --- | --- |
| Components | Controls and feedback, light/dark | Labels, input states, buttons, switches and feedback at readable page size. |
| Settings and detail | Light/dark; error, narrow Japanese, large text and long Japanese cases | Native Form, outlined editing, disabled state and wrapping. |
| Button transition | Ready/running/completed/failed in light, representative dark and large Japanese states | Stable visual states for the same fixture used by the operation review. |
| Collection | Scene-backed normal light/dark, empty, loading, error | Native toolbar/search and fixed state content in an app environment. |
| Collection narrow | 320 pt, accessibility medium, Increased Contrast | Density and wrapping only; fixed-host native chrome is unreliable. |

Preview and capture instantiate the same fixture views and data. Static images do not exercise search input, sheet, navigation, keyboard, animations or VoiceOver.

## Record and compare

`nix develop -c just record-snapshots` deliberately updates both baseline groups and `tools/snapshots.json`. The hosted test captures five actual PNGs, and only this recording command copies them to the baseline directory. Review every changed PNG at full size, then run `nix develop -c just test-snapshot`. Comparison prechecks all 38 manifest paths and hashes before and after. The 33 Package images use the existing exact RGBA comparison inside XCTest. The five scene-backed images are captured inside the app test, then compared as decoded RGBA pixels by the Nix-pinned Pillow command **after that test process exits**. Missing or extra cases, invalid PNGs, dimensions and pixel changes fail the command. Normal comparison never rewrites a baseline. Five scene-backed baselines live under `Testing/Host/Tests/__Snapshots__/HostedCollectionTests/`; the other 33 live under `Testing/Tests/EvoloomSnapshotTests/__Snapshots__/ComponentSnapshots/`.

## First Settings review

Before the adjustment, both the fixed-host PNG and the actual app display showed a rounded input outline inside each rounded Form group. The two input rows filled much of the first group, and Save occupied a separate white Form group with wide empty margins. The actionable error and disabled value were already visible; their state logic did not need to change. We considered global outline removal, an explicit Form-only input appearance, and a screen-only native field. The explicit `.formRow` appearance keeps the labeled-field behavior in one component while leaving the outlined default for the detail screen. Two Save placements were viewed in the app: a separate clear row left a large gap after Preferences, while its footer kept the action next to that group. The Settings fixture alone places a full-width Save action there. Neither choice changes the shared palette or native Form spacing.

The changed baselines are `review-settings-light`, `review-settings-dark` and `review-settings-error`. `review-settings-narrow-ja` (320 pt, `ja_JP`) checks long labels and hints; `review-settings-large-text` (390 pt, accessibility medium) checks wrapping and action size. All use the fixed 3× host and zero test safe area. The iPhone 18 Pro app uses a real 402 × 874 pt scene and safe area, so its status bar and vertical placement differ from the fixed images. Compare the Form rows and states rather than expecting pixel identity. The component controls and detail baselines did not change because their inputs retain `.outlined`.

The fixed large-text image includes the Save action, while the same 402 × 874 pt app display initially shows only its top edge; reaching it requires Form scrolling. [The sim-use operation review](SIM_USE_REVIEW.md) verifies normal-size focus, editing, Toggle, error/disabled transitions, and large-text Save reachability in the real scene. On the local host, the large-text software-keyboard combination initially failed because the keyboard stopped appearing. The later [2026-10-05 Cloud operation run](https://github.com/9uiLe/evoloom/actions/runs/37232909641) completed that case with `keyboard-state` and screenshot evidence, then reached Save after a Form swipe and Escape. That is historical evidence for PR #2, not a validation of this change. These captures do not verify VoiceOver or persistence.

## Detail and Button review

The Detail fixture keeps its outlined fields. Its navigation heading is now
stable while Title is edited, the overview Card no longer has a redundant
separator, and the long-Japanese variant includes translated labels and hints.
These are fixture-level layout and copy choices; no shared token or product
component changed. The new Button fixture holds the same primary action width
through ready, processing, completed and failed states. The seven Button PNGs
are fixed starting states; actual transitions and disabled taps are checked
with sim-use on the scene-backed app. See
[the operation record and reproduction steps](DETAIL_BUTTON_REVIEW.md).

Successful and mismatching comparisons save actual PNGs to `TestResults/Rendered/components.<case>.png`. Mismatches also save `TestResults/SnapshotDiffs/<case>/expected.png`, `actual.png` and `diff.png`. `TestResults/host-image-comparison.json` identifies each hosted case and its comparison status. `ci-report.json` separates the hosted Xcode capture outcome from the image comparison outcome. `ios.xcresult` and `host-ios.xcresult` (or `snapshot.xcresult` and `host-snapshot.xcresult`) retain the two sessions. `TestResults/Logs/` contains Xcode output even if a result bundle is incomplete. A pre-render build or environment failure makes no image; inspect the first failed step and CI's `image-status.txt`. The `ios-test-evidence` artifact uploads available actuals, diffs, logs, xcresults and both baseline directories after success or failure. A canceled GitHub job may stop before upload, so artifact availability is not guaranteed on cancellation.

## Put images in a PR

State the issue, affected screen/state, change reason, capture conditions, before/after baseline images, findings and remaining questions. Generate SHA-pinned Markdown with `nix develop -c python3 tools/pr_images.py --sha <full-commit-SHA>`. Use `--extra-case review-detail-large-text` or `--extra-case button-flow-running-dark` for representative states; repeat the option for other named cases when relevant. It verifies every linked image blob in that exact commit, including hosted list paths and optional cases. Paste it into the PR and confirm the images render. Add `--ci-url` after successful comparison of the same PR head SHA. An Actions PR run may test a synthetic merge checkout; report its checkout SHA from `ci-report.json` separately. Inline PNGs are **committed baselines**, never actuals from that CI run. Actuals and diffs are in the artifact; artifact download URLs are not inline image URLs.

Reviewers decide whether an appearance is desirable. Snapshot success only preserves it. The integrating product owns screen reading order, contextual labels, focus and VoiceOver validation.

## Xcode JSON project format

The checked-in source is JSON (`Testing/Host/project.json`), formatted by repository checks, and XcodeGen 2.44.1 generates an ignored `project.pbxproj`. Apple documents a native `project.xcproj` JSON format for Xcode 27+, default in 27.2. Installed Xcode 27.0 (27A266a) has no Project Format selector, and `xcodebuild -convert-project xcproj` failed here. A native `.xcproj` was **not** generated or validated; the XcodeGen JSON spec is a different format. When the pinned Apple environment moves to 27.2+, convert the generated project with Xcode's selector, compare its build/tests, then decide whether to commit native `.xcproj` and remove XcodeGen. See [Apple's format guide](https://developer.apple.com/documentation/xcode/updating-your-xcode-project-configuration-file-format).
