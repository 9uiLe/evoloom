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
Save reachability accepts either an initially visible action or one reached
after an outer ScrollView swipe and, when needed, native keyboard dismissal.
The script checks the full Button frame against the measured 402 × 874 pt
scene and its 62 pt top / 34 pt bottom safe areas, verifies a minimum 44 pt
operation area and enabled state, then asks sim-use which element is at the
Button's center. The keyboard-on observation and final reachable screenshot
are separate. An accessibility-tree entry outside the viewport is not counted
as reachable. At most two outer swipes are attempted; an obscured, disabled or
still offscreen action fails. This checks access to the fixture's empty Save
action, not persistence or a successful save.
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

## Recorded operation evidence

The checked-in [sim-use screen captures](images/pr3-sim-use/) are actual
Simulator display PNGs, separate from the 39 committed snapshot baselines and
the PNGs rendered by each image-test run. Each linked artifact also contains
the per-command `actions.jsonl`, observed UI JSON, environment and any
`failure.txt` for that run.

- [Button operation run](https://github.com/9uiLe/evoloom/actions/runs/37258531007)
  at code `904e70b2fa575c5566d21d436a4ad9dec4820ac3`: the full workflow
  succeeded. Its Button step took 4m11s, including ready, processing,
  failure, retry, completion, external disable, dark and large Japanese
  observations. The [artifact](https://github.com/9uiLe/evoloom/actions/runs/37258531007/artifacts/11323334626)
  contains its action counts, accessibility observations and actual captures.
- [Detail operation run](https://github.com/9uiLe/evoloom/actions/runs/37257155593)
  at code `932dce848bb68d18b39e67cc1f5dab155578c2b5`: the full workflow
  succeeded. Its Detail step took 6m56s, including Title and multiline Notes edits, visible
  software keyboard at accessibility-medium size, outer ScrollView reachability,
  and a TextEditor-internal swipe. The outer editor frame remained
  `x=20, y=490, 362×110 pt`; the before/after PNGs show its text moving.
  The script also checked that the cropped editor image changed while its AX
  frame stayed fixed. Its
  [artifact](https://github.com/9uiLe/evoloom/actions/runs/37257155593/artifacts/11324120881)
  contains all 15 actual operation PNGs, UI observations and command records.

Both runs used Xcode 27.0 (27A266a), iPhoneSimulator SDK 27.0 (24A430),
iOS 27.0 (24A434), arm64 iPhone 18 Pro, 402×874 pt app scene, en-US simulator
language and Nix-pinned sim-use 0.14.0. Their fixed UDID was
`4F17718A-544A-4115-888E-27ABF543A529`. Japanese fixture routes use
Japanese copy; all other route strings are English. The operation PNGs are
linked to their capture code above; the later commit that stores those PNGs
only changes their repository location. An earlier Button step succeeded
inside a failed combined run; the checked-in Button images instead come from
the later fully successful run above.

In an earlier [Detail run](https://github.com/9uiLe/evoloom/actions/runs/37255651511),
the Detail step succeeded but the full workflow failed on an unrelated
`collection-empty` native chrome pixel mismatch. That run's before/after Notes
PNGs passed the later cropped-image assertion when checked locally; its
[artifact](https://github.com/9uiLe/evoloom/actions/runs/37255651511/artifacts/11322414638)
retains the strict diff. The checked-in Detail operation PNGs are from the
subsequent successful run above.

The earlier large-text script incorrectly failed as soon as `Save project`
appeared in the pre-scroll accessibility tree. AX presence alone did not show
whether its frame was on screen or unobscured; an initially reachable Button
is also a valid layout. The updated script removes that precondition and
records the screen/frame/point-hit observations. Its small Python regression
tests cover initially reachable, reached after scrolling, top/left/right
overflow, keyboard obstruction and disabled states. The previous Cloud
operation evidence predates this correction; use the latest manual run linked
from PR #3 for its execution result.

On the local pinned simulator, sim-use confirmed both accepted reachability
paths on the same review fixture: normal-size Save was initially visible and
hit-tested as the Button; at accessibility-medium size it started below the
screen and became visible after one outer swipe. See the actual Simulator
[normal](images/pr3-reach-diagnostic/normal-initially-reachable.png),
[large before](images/pr3-reach-diagnostic/large-before-scroll.png), and
[large after](images/pr3-reach-diagnostic/large-after-scroll.png) captures.
The local full detail scenario stopped earlier because tapping Notes did not
make `sim-use keyboard-state` report a software keyboard. Thus these local
captures do not validate keyboard-on reachability; the explicit Cloud detail
run is recorded separately in PR #3. All three PNGs were captured against
code `a79b604a4227a747d911392fa533df6814ea3283`; their later storage
commit is not a separate operation run.

The first corrected [Cloud detail run](https://github.com/9uiLe/evoloom/actions/runs/37266129931)
captured all five host images and matched the strict comparison. Its sim-use
log shows a software keyboard over large Notes, an outer swipe, keyboard
dismissal, and a visible enabled Save hit target. Later, after launching the
long-Notes route, sim-use briefly returned an AX tree with entries but a
`0 × 0` screen; the old helper accepted that tree and image-crop calculation
failed by dividing by zero. The shared `Review.ui` observation now waits at
most eight seconds for nonzero screen dimensions, saving each interim UI JSON
and failing explicitly if the viewport never becomes ready. This is a
readiness correction for both detail and settings operation scripts, not a
change to the product view. The full Cloud operation must be rerun after it.
The run's [keyboard-on screen](images/pr3-reach-diagnostic/cloud-large-notes-keyboard.png)
and [Save reached screen](images/pr3-reach-diagnostic/cloud-large-save-reached.png)
are actual sim-use PNGs from capture code `a79b604`; the run as a whole failed
later and is not presented as a successful full operation check.

A later [Button manual run](https://github.com/9uiLe/evoloom/actions/runs/37257019496)
passed its Package and hosted image tests but timed out after 30s in the first
`simctl ui … appearance light` call, before the host app was launched. The
shared launch helper now allows that Apple command 60s; it still records an
error and stops on timeout, without retrying the operation or changing the
Button fixture. This is a cold Simulator command bound, not a measured change
to the Button action's response time.

The pre-change detail baselines are in commit
[`25f923f`](https://github.com/9uiLe/evoloom/tree/25f923fca2ba947c91ebc968378921107c8c8ce3).
The PR records the replacement baseline commit and operation run separately,
including any local and Cloud differences. Neither a passing comparison nor
the fixture layout is a general design quality claim.
