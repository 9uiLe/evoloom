# Detail editing and Button transition review

The root `Evoloom` Package is unchanged. Both screens live in the development-only
`EvoloomReviewFixtures` target, which Preview, the existing app host and fixed
image tests share. `ReviewDetailView` still uses the public outlined `IOSInput`
and `IOSTextArea`. Its Save action is empty: reaching or tapping it does not
demonstrate persistence. `ReviewButtonFlowView` simulates an operation; it has
no timer, network request or stored result. The fixture owns phase, result,
retry and the visible run count. `IOSButton` remains a native Button with its
existing loading and disabled contract.

## Reproduce

```sh
nix develop -c just doctor
nix develop -c just prepare-deps
nix develop -c just run-host detail normal light
nix develop -c just run-host detailJapanese normal dark
nix develop -c just run-host detailLongNotes normal light
nix develop -c just run-host buttonFlow normal light
nix develop -c just verify-detail-interaction
nix develop -c just verify-button-transition
nix develop -c just test-snapshot
```

For a focused rerun without another build, first run `nix develop -c just
build-host`, then `nix develop -c python3 tools/sim_use_detail_button.py
--scenario detail --reuse-built-host` (or `--scenario button`). The separate
`verify-settings-interaction` entry remains available. Manual GitHub Actions
`workflow_dispatch` flags `verify_detail_interaction` and
`verify_button_transition` reuse the app already built by the normal iOS test
step. Ordinary PR CI runs the Package and host snapshots, strict image
comparison and copied-source build, without the extra interaction scenarios.

Each sim-use run creates a new UTC-named `TestResults/SimUse/` directory.
`environment.json` records the code checkout, Apple versions, fixed UDID,
content size and Nix-store sim-use binary. `actions.jsonl` records every
command, UTC time, duration and exit status. Numbered `*.ui.json` files
preserve the accessibility observations, and PNGs are actual Simulator screen
captures. `failure.txt` identifies a failed assertion or command. No previous
run directory is reused. The CI `ios-test-evidence` artifact includes these
files even after a normal test failure, subject to GitHub cancellation limits.

The scripts follow observe → act → verify on the exact UDID returned by
`doctor`. Detail requires Title and Notes values to change, an inserted
newline, an editor-internal swipe distinct from an outer ScrollView swipe,
software keyboard visibility, and a reachable Save action at
accessibility-medium size. It also observes long Japanese and dark appearance.
The editor-scroll check launches `detailLongNotes` with fixed overflowing
content. This avoids making a timed accessibility input tool type hundreds of
characters. Before and after PNGs show the Notes text moving inside its
outline while the Title, Notes frame, hint and Save stay in place; the script
also checks the editor's accessibility frame. The normal route separately
checks typed Notes, a newline and a changed Title.
Button requires ready → processing → failure → retry → processing → completed,
checks the native Button's disabled state and the unchanged run count after
physical taps during processing and external disable, then observes dark and
large Japanese states. Changes to Simulator content size are restored in
`finally`. Every poll and command has a finite timeout.

## Observation and design decision

Before this change, the iPhone 18 Pro scene and 390 pt fixed images displayed
the editable project title twice: as the large navigation heading and as the
Title value. The heading was bound to the unsaved field, so it changed during
editing. The Card's description and status were separated by a rule even
though they were one overview. At 320 pt, the supposedly Japanese case still
used English labels, hints, Card text and Save. These are direct observations
from the previous image and fixture source. Notes focus showed the software
keyboard; an outer swipe moved Save upward into the visible region. We did
not observe a defect in the outlined field border or keyboard avoidance that
justified changing the product component or shared tokens.

The screen now uses a stable “Project details” navigation heading, keeps the
editable value in the Title field, removes the overview's extra separator,
and supplies Japanese fixture strings throughout its long-Japanese case.
These are screen-specific hierarchy and localization choices. The outlined
Input, TextArea and Save Button implementations and their public API are
unchanged. The new fixed images cover detail light/dark, 320 pt Japanese and
accessibility-medium text. A fixed 1050 pt image is a wrapping check, not
evidence that Save is reachable on the 402 × 874 pt app scene.

In the Button fixture, an intrinsic-width primary action grew when its loading
hourglass appeared. The fixture now gives that screen's primary label the
available width, so its outer width and vertical placement stay constant
across states. The product `IOSButton` remains composable and is not forced
full-width in other screens. The screen uses a worded status Badge and result
text/Inline Alert; success and failure are not conveyed by color alone.

## Capture scope and limits

`just record-snapshots` explicitly writes baselines. Review the changed PNGs
and `tools/snapshots.json`, then use `just test-snapshot` for normal comparison.
The fixed Package host renders at 390 pt or 320 pt, 3× scale, zero test safe
area, specified light/dark appearance, system fonts, explicit locale and
content size. The real app scene is 402 × 874 pt with iOS safe areas. The
sim-use screenshots include the status bar and keyboard when visible; do not
compare their pixels directly with the fixed images. Xcode 27.0 (27A266a),
iPhoneSimulator SDK 27.0 (24A430), iOS 27.0 runtime (24A434), arm64 iPhone
18 Pro and sim-use 0.14.0 are checked by `just doctor`. Static images cannot
verify input, focus, keyboard, double submission, VoiceOver or saved data.
The integrating product owns contextual reading order and final VoiceOver
validation.

The pre-change detail baselines are in commit
[`25f923f`](https://github.com/9uiLe/evoloom/tree/25f923fca2ba947c91ebc968378921107c8c8ce3).
The PR records the replacement baseline commit and operation run separately,
including any local and Cloud differences. Neither a passing comparison nor
the fixture layout is a general design quality claim.
