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

`run-host` builds, installs and launches the app on the exact simulator selected by `just doctor`. The first argument is `collection`, `controls`, `feedback`, `settings`, `settingsError` or `detail`; the second is a collection state (`normal`, `empty`, `loading`, `error`); the third is `light` or `dark`. Open Simulator to inspect the app. After its view appears, `xcrun simctl io <doctor-UDID> screenshot <path>.png` captures the entire display. An immediate screenshot after launch can capture a blank frame; wait for the view, without a fixed long sleep.

For Canvas, open `Testing/Package.swift`, select iPhone 18 Pro and a named `#Preview` in the fixture sources. Xcode 27.0 Canvas previously failed to resolve Evoloom on this machine. The app display and simulator tests are verified alternatives; Canvas has not been reverified after this change.

`just test-ios` executes package unit and fixed-size image tests, then five scene-backed collection images, serially on the same simulator. `just test-snapshot` runs only the two image groups. Combining all tests into the app session was tried: seven old fixed-size cases changed solely from the host context. Keeping those baselines avoids re-recording unrelated settings, detail and narrow images. The collection 320 pt large-text case remains a fixed-size layout test; its native chrome is **not** used to judge contrast.

Scene-backed list cases use an iPhone 18 Pro window at 402 × 874 pt, 3× (1206 × 2622 px), real safe area, system fonts, `en_US`, UTC, standard Dynamic Type and explicit light/dark appearance. The snapshot captures app content without status bar glyphs. The fixed-size cases use a `UIHostingController`, 390 or 320 pt width, specified height, 3×, zero test safe area and explicit locale, Dynamic Type and appearance. Both modes require macOS 27.0 build 26A428, Xcode 27.0 build 27A266a, SDK 27.0 build 24A430, iOS 27.0 runtime build 24A434 and arm64. `just doctor` rejects a mismatch.

| Screen | Image cases | Purpose |
| --- | --- | --- |
| Components | Controls and feedback, light/dark | Labels, input states, buttons, switches and feedback at readable page size. |
| Settings and detail | Light/dark; error and long Japanese cases | Native Form, editing, disabled state and wrapping. |
| Collection | Scene-backed normal light/dark, empty, loading, error | Native toolbar/search and fixed state content in an app environment. |
| Collection narrow | 320 pt, accessibility medium, Increased Contrast | Density and wrapping only; fixed-host native chrome is unreliable. |

Preview and capture instantiate the same fixture views and data. Static images do not exercise search input, sheet, navigation, keyboard, animations or VoiceOver.

## Record and compare

`nix develop -c just record-snapshots` deliberately updates both baseline groups and `tools/snapshots.json`. The hosted test captures five actual PNGs, and only this recording command copies them to the baseline directory. Review every changed PNG at full size, then run `nix develop -c just test-snapshot`. Comparison prechecks all 28 manifest paths and hashes before and after. The 23 Package images use the existing exact RGBA comparison inside XCTest. The five scene-backed images are captured inside the app test, then compared as decoded RGBA pixels by the Nix-pinned Pillow command **after that test process exits**. Missing or extra cases, invalid PNGs, dimensions and pixel changes fail the command. Normal comparison never rewrites a baseline. Five scene-backed baselines live under `Testing/Host/Tests/__Snapshots__/HostedCollectionTests/`; the other 23 live under `Testing/Tests/EvoloomSnapshotTests/__Snapshots__/ComponentSnapshots/`.

Successful and mismatching comparisons save actual PNGs to `TestResults/Rendered/components.<case>.png`. Mismatches also save `TestResults/SnapshotDiffs/<case>/expected.png`, `actual.png` and `diff.png`. `TestResults/host-image-comparison.json` identifies each hosted case and its comparison status. `ci-report.json` separates the hosted Xcode capture outcome from the image comparison outcome. `ios.xcresult` and `host-ios.xcresult` (or `snapshot.xcresult` and `host-snapshot.xcresult`) retain the two sessions. `TestResults/Logs/` contains Xcode output even if a result bundle is incomplete. A pre-render build or environment failure makes no image; inspect the first failed step and CI's `image-status.txt`. The `ios-test-evidence` artifact uploads available actuals, diffs, logs, xcresults and both baseline directories after success or failure. A canceled GitHub job may stop before upload, so artifact availability is not guaranteed on cancellation.

## Put images in a PR

State the issue, affected screen/state, change reason, capture conditions, before/after baseline images, findings and remaining questions. Generate SHA-pinned Markdown with `nix develop -c python3 tools/pr_images.py --sha <full-commit-SHA>`. It verifies image blobs in that exact commit, including hosted list paths. Paste it into the PR and confirm the images render. Add `--ci-url` after successful comparison of the same PR head SHA. An Actions PR run may test a synthetic merge checkout; report its checkout SHA from `ci-report.json` separately. Inline PNGs are **committed baselines**, never actuals from that CI run. Actuals and diffs are in the artifact; artifact download URLs are not inline image URLs.

Reviewers decide whether an appearance is desirable. Snapshot success only preserves it. The integrating product owns screen reading order, contextual labels, focus and VoiceOver validation.

## Xcode JSON project format

The checked-in source is JSON (`Testing/Host/project.json`), formatted by repository checks, and XcodeGen 2.44.1 generates an ignored `project.pbxproj`. Apple documents a native `project.xcproj` JSON format for Xcode 27+, default in 27.2. Installed Xcode 27.0 (27A266a) has no Project Format selector, and `xcodebuild -convert-project xcproj` failed here. A native `.xcproj` was **not** generated or validated; the XcodeGen JSON spec is a different format. When the pinned Apple environment moves to 27.2+, convert the generated project with Xcode's selector, compare its build/tests, then decide whether to commit native `.xcproj` and remove XcodeGen. See [Apple's format guide](https://developer.apple.com/documentation/xcode/updating-your-xcode-project-configuration-file-format).
