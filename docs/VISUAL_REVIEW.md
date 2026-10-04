# Reviewing representative screens

The screens under `Testing/Sources/EvoloomReviewFixtures/` are fixed design
examples. The development Package compiles them beside its tests; the root
`Evoloom` library product contains none of them. Their purpose is to compare
shared component decisions in context, not to provide an app or product flow.
`ComponentCatalog.swift` keeps the older component Preview and the native
collection example. `ReviewScreens.swift` adds two readable component pages,
a Settings `Form`, and a detail/edit screen. Preview and image tests instantiate
these same view types and fixed data. The collection Preview lets a reviewer
change normal, empty, loading and error states; snapshots construct each state
directly. Navigation, List, Form, search and sheet use SwiftUI controls. The
static screenshots do not test their interaction, VoiceOver or keyboard flow.

## Preview and fixed capture

Run `nix develop -c just prepare-deps`, open `Testing/Package.swift` in Xcode,
select the fixed iPhone 18 Pro simulator and open the files above. Choose a
named `#Preview` in the canvas. The image tests remain available if Canvas is
unavailable. The root `Package.swift` remains the normal consumer entrypoint.

Run `nix develop -c just test-snapshot` to compare and save every **actual**
render from that test invocation in `TestResults/Rendered/components.<case>.png`.
Run `nix develop -c just test-ios` for the same images together with the unit
tests, in one XCTest session. `just check` also builds a copied-source Package.
The capture uses the existing SnapshotTesting strategy and does not start a
second Simulator session for PR images. Actual PNGs are saved from the
comparison callback, including on a pixel mismatch. If an earlier build or
baseline preflight fails, no render exists; read the command failure and the
`ios.xcresult` or `snapshot.xcresult` that exists. `ci-report.json` and the CI
Job Summary report the actual count and missing names. The CI artifact
`ios-test-evidence` contains `TestResults/Rendered`, `SnapshotDiffs` on
mismatch, xcresult bundles and the committed baseline PNGs. The artifact step
runs after test success or failure. It cannot fabricate images after a build
failure.

The record command is separate: `nix develop -c just record-snapshots` writes
baseline PNGs under `Testing/Tests/EvoloomSnapshotTests/__Snapshots__/` and
updates `tools/snapshots.json`. Review each changed image at full size, then
run `just test-snapshot` without record mode. Comparison checks exact RGBA
pixels and refuses missing, added or changed baselines; no tolerance was
increased for these screens.

The pinned host is Xcode 27.0 build 27A266a, iOS Simulator 27.0 build 24A434,
iPhone 18 Pro on arm64. The host sets a 390 pt width (320 pt for narrow cases),
3× scale, zero safe-area inset, system fonts, UTC and explicit `en_US` or
`ja_JP`, appearance and Dynamic Type. XCTest uses `-testLanguage en`
and `-testRegion US`. `just doctor` rejects a different Apple environment.
The Preview canvas is interactive and does not claim pixel identity with a
fixed test host.

| Screen | Normal captures | Focused case and reason |
| --- | --- | --- |
| Component pages | Controls and feedback, light/dark | Controls include input error, disabled/loading buttons and both switch values; feedback shows empty and loading presentation. Two pages avoid shrinking a long catalog. |
| Settings Form | Light/dark | `review-settings-error` has invalid email, correction text, disabled Save and a disabled managed field. |
| Collection List | Light/dark | Empty, loading, error and 320 pt accessibility-medium Increased Contrast cover state and density risks. |
| Detail/edit | Light/dark | `review-detail-ja-long` uses narrow width and long Japanese notes. |

The first baselines are a **starting point for discussion**, not design
approval. In the first review, the settings error fixture was corrected to
show invalid input and disable Save. The collection image now captures the
whole native NavigationStack, including toolbar and search, so its six
existing baselines changed intentionally. The light collection's native
search and toolbar chrome still appear faint in this fixed host; assess them
in Xcode Canvas and a real integration before treating this as an accepted
product decision. No runtime component tokens or styles changed in this PR.

## Put images in a PR

For an UI change, include the observed issue, affected screen/state, before
and after images, capture conditions, review findings and the CI run for the
image commit. Generate the representative Markdown from the committed
baselines with `nix develop -c python3 tools/pr_images.py --sha <full-SHA>`.
The script checks all ten listed PNGs and uses raw image URLs pinned to that
SHA. Paste it into the PR description; confirm the ten images display in the
rendered GitHub PR. These are **committed baselines**, even when the CI for the
same SHA passes. Add `--ci-url <successful-run-URL>` after the comparison
finishes and verify that the run checked that exact SHA. Current-run actual
images live in the artifact and are not available as stable inline Markdown
image URLs. Do not put artifact download URLs in `![](...)`.

Review baseline PNG changes in **Files changed** and compare them to
`TestResults/Rendered` from that SHA's CI artifact. If tests fail after
rendering, inspect `SnapshotDiffs/<case>/expected.png`, `actual.png` and
`diff.png`, as well as xcresult. If capture did not start, state “image not
generated” and the build or environment error. Do not call an unverified
baseline a successful current-run render. Reviewers decide whether the new
appearance is desirable; snapshot success only means it matches the chosen
baseline. The integrating product remains responsible for screen reading
order, contextual labels, focus and VoiceOver testing.
