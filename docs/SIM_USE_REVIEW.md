# Settings Form interaction review

The product remains the root Swift Package. `Testing/Host/` is the existing
development-only app. `sim-use` observes and operates that app on the exact
iPhone 18 Pro selected by `just doctor`; it is not an Evoloom runtime or copied
component dependency. The host still uses `ReviewSettingsView` from the shared
fixture target. Save's fixture action is empty: a tap cannot prove persistence.

## Reproduce

```sh
nix develop -c just doctor
nix develop -c just prepare-deps
nix develop -c just verify-settings-interaction
```

The last command builds and installs the existing host once, then runs the
normal/error input and Toggle checks, a real-scene accessibility-medium check,
and Japanese/dark appearance. Each scenario follows
observe → act → verify: it reads `sim-use ui --json` before and after actions,
checks values and enabled states rather than command exit alone, and saves
`sim-use screenshot` PNGs. The fixed UDID is passed to every sim-use action;
other booted devices are left alone. A new UTC-named directory under
`TestResults/SimUse/` stores `environment.json`, `actions.jsonl`, UI JSON,
PNGs and `failure.txt` if any check fails. Existing directories are never
reused. The command fails if the foreground app, expected value, disabled
state, software keyboard or reachable Save differs. A scenario failure does
not prevent the remaining scenarios from collecting evidence. Operations
have explicit timeouts; no unbounded retry or fixed long sleep is used.

For one scenario during adjustment, run, for example:

```sh
nix develop -c python3 tools/sim_use_review.py --scenario large --reuse-built-host
```

`--reuse-built-host` installs the existing `DerivedData/Host` build into the
fixed Simulator; run `just build-host` first when using it locally. Omit the
flag for an independently reproducible run that builds the host. Scenarios
are `normal`, `error`, `large`, `japanese-dark`, and `outlined`. The default
operation check runs `large`, `normal`, `japanese-dark`, then `error`, with
`large` before text injection so the
software-keyboard state can be inspected before HID input changes it.
Japanese/dark observation precedes the final error-edit scenario. Only the
large scenario dismisses the keyboard, because it needs to reach Save after
keyboard-visible scrolling; the error scenario ends once the invalid value
and disabled Save return.
`outlined` is available as a focused check; its existing default appearance
also remains in the regular snapshot suite. The manual GitHub Actions
`workflow_dispatch` input `verify_settings_interaction` runs this command in
the existing iOS job after the image tests, reuses that host build, and uploads the resulting evidence
with the usual `ios-test-evidence` artifact. Ordinary PR CI keeps its current
snapshot and Package checks without the extra operation session.

The `normal` and `error` scenarios check Display name and Email editing,
focus movement, native Toggle value `1→0→1`, initial error and disabled Save,
disabled Workspace, error removal for a value containing `@`, and error return
when the value no longer contains `@`. They deliberately check the fixture's current
condition, not business-grade email validation. The repeatable check types a
short suffix with sim-use, verifies the exact AX value, then removes that
suffix with the documented Backspace keycode. It does not depend on the
iOS paste menu, which failed to appear on the initial Cloud operation run.
The error scenario verifies the changed field value and Save/error states;
it does not require the software keyboard to stay visible after the normal
scenario's HID typing. The normal scenario proves focus by editing each
target field after a tap and saves the visible focus state; the large scenario
explicitly requires the software keyboard while scrolling. HID typing can
change the keyboard connection state in later scenarios, so the normal
scenario does not duplicate that large-case requirement.
The native Toggle's accessibility frame spans its Form row, so the script
touches the switch at the trailing edge of the observed frame and verifies
the value transition. It does not retain `@N` aliases across screen changes.

`large` sets `simctl ui <UDID> content_size accessibility-medium`, verifies
that setting, then restores the original size in a `finally` block. It checks
software keyboard visibility through both `keyboard-state` and the captured
screen, requires the Email field's frame to move upward after a Form scroll,
and requires Save's frame to be inside the real
402×874 pt scene above the bottom safe area. The fixed 390×1050 pt snapshot
does not establish this reachability. `japanese-dark` checks the shared long
Japanese fixture's label, value, hint and actionable error at real device
width, then checks the dark error/disabled presentation. `outlined` edits the
detail screen's default outlined Title input. These are screen operation
checks; they do not claim VoiceOver reading quality.

## Local observation on 2026-10-05 JST

The local Nix package is sim-use 0.14.0. Its signed universal binary is from
the [official v0.14.0 release](https://github.com/lycorp-jp/sim-use/releases/tag/v0.14.0),
with fixed archive SHA-256
`67e2ee29a7246272de8646e46664a93d9cebcace134094cfd3d07dfb82bda3e6`.
Xcode is 27.0 (27A266a), iPhoneSimulator SDK 27.0 (24A430), runtime 27.0
(24A434), arm64 iPhone 18 Pro UDID
`10849834-229F-4AB1-A1B3-88BBEB25B5CF`. The simulator system language is
Japanese; the English fixture strings remain English. `sim-use devices`,
`ui`, `tap`, `paste`, `type`, `gesture`, `keyboard-state` and `screenshot` all
ran from the Nix store executable.

In the first normal-size session, `keyboard-state` returned `visible:true`
after tapping Display name and Email, and the screenshot showed the Japanese
software keyboard. Editing changed the AX field values; the focus underline
moved from Display name to Email. Tapping the native Toggle's displayed thumb
changed its AX value from `1` to `0` and back to `1`. In the error fixture,
Workspace remained disabled with value `Field notes` and tapping it did not
show a keyboard. Correcting Email from `invalid` to `valid@example.com`
removed the error and enabled Save; replacing the value with text without `@`
restored the error and disabled Save. The fixture action is empty, so no save
result was asserted.

The checked-in [operation PNGs](images/pr2-sim-use/) are captures from
`sim-use screenshot`, taken on the working tree based on checkout
`0c978bb13c1431ab3c1bcd0cbedc611aafe386c0` with the two development
fixture routes in this change. They are **Simulator operation evidence**, not
snapshot baselines or CI-rendered images. They show the [normal Form](images/pr2-sim-use/normal-light.png),
[Display name with the software keyboard](images/pr2-sim-use/display-focused-keyboard.png),
[Email with the software keyboard](images/pr2-sim-use/email-focused-keyboard.png),
[initial error and disabled Save](images/pr2-sim-use/error-disabled.png),
and [corrected Email with enabled Save](images/pr2-sim-use/error-corrected-save-enabled.png).
The [dark focused error](images/pr2-sim-use/dark-error-focused.png) and
[long Japanese error](images/pr2-sim-use/japanese-error.png) show the other
inspected appearances. The [large-text Save capture](images/pr2-sim-use/large-save-reached-without-keyboard.png)
proves reachability after a scroll **without** the software keyboard; its name
and this limitation are intentional.

The large-text scene displayed full labels, values and hints. After a
`sim-use gesture scroll-up`, the Save button's frame moved into the visible
scene and a screenshot showed it fully. The Japanese error and dark error
were visually inspected; the Japanese error was fully readable at 402 pt.
The outlined detail Title accepted an edit without changing its default
appearance.

The software keyboard stopped appearing in later sessions, although taps
still focused fields and hardware-key input changed text. An initial Cloud
operation run could read the UI and observe the software keyboard but failed
because the iOS paste menu did not appear. The repeatable script now uses
`sim-use type` and Backspace; local trials completed the `normal` value and
Toggle changes and, with a temporary en-US setting, the `error` transitions.
Both still failed their `visible:true`
checks. `large` failed the same keyboard check, while `japanese-dark` and
`outlined` completed. The local automated full run failed at that point;
the Cloud verification below later completed the keyboard-visible large-text
scroll. On this host, opening Device Hub,
relaunching the app, restarting the target Simulator, and temporarily setting
the legacy Simulator `ConnectHardwareKeyboard=false` preference did not
restore it. A temporary simulator language change to English also did not
restore it; both temporary preferences were reverted. This is an observed host
state, not a diagnosed Evoloom or sim-use defect. On a host where the software
keyboard appears, rerun `just verify-settings-interaction` and review its
fresh PNG and UI evidence before closing that gap. Do not use the earlier
normal-size keyboard screenshot to claim the large-text combination passed.

The [2026-10-05 Cloud operation run](https://github.com/9uiLe/evoloom/actions/runs/37226649166)
captured the accessibility-medium Email field with the **software keyboard
visible**, confirmed by both `keyboard-state` and a Simulator PNG. Its generic
`gesture scroll-up` left the field at the same screen coordinate; the review
correctly failed rather than reporting Save reachability. The next run uses a
swipe explicitly inside the Form above the keyboard. This is a test gesture
change, later verified in the runs below, not a product layout change. That run also showed
the email keyboard inserting an extra `@` during `sim-use type`; the review
now checks the fixture's actual condition and removes the suffix observed in
the UI. Each scenario relaunches its initial screen to avoid inheriting the
previous keyboard and scroll state. The Cloud run's
[Artifact](https://github.com/9uiLe/evoloom/actions/runs/37226649166/artifacts/11313410024)
contains the image, UI JSON, command times and failure details.

The [following Cloud run](https://github.com/9uiLe/evoloom/actions/runs/37228513283)
timed out while retrieving the accessibility tree immediately after focusing
Email at accessibility-medium size, before the explicit Form swipe could run.
Its normal edit and Toggle checks passed; the error condition cleared and
returned, but the software keyboard was absent in that later scenario.
The next review observes keyboard state before requesting the full UI tree,
allows a bounded 45 seconds for that query, and reuses the already built
host in the manual CI job. The captured failure remains available in that
run's [Artifact](https://github.com/9uiLe/evoloom/actions/runs/37228513283/artifacts/11312909879).

The [Cloud run on 12956fa](https://github.com/9uiLe/evoloom/actions/runs/37230154630)
completed the `large` scenario. At accessibility-medium size, the
[focused Email and software keyboard](images/pr2-sim-use/large-cloud-email-focused-keyboard.png)
were visible. A `sim-use swipe` within the Form moved Email from y=421 to
y=151 while `keyboard-state` remained `visible:true`; the
[post-scroll PNG](images/pr2-sim-use/large-cloud-after-scroll-keyboard.png)
shows the focused value, hint, lower settings and keyboard. After an Escape
key event, the [Save control was reachable](images/pr2-sim-use/large-cloud-save-reached.png)
within the 402×874 pt scene. These three PNGs are the actual `sim-use screenshot`
outputs from that run, copied unchanged from its
[Artifact](https://github.com/9uiLe/evoloom/actions/runs/37230154630/artifacts/11313253961).
The overall manual job still failed: a later normal keyboard visibility check
and separate UI queries timed out. The successful large scenario is evidence
for that combination only; the run is not reported as a passing full review.

The [Cloud run on 515cb3d](https://github.com/9uiLe/evoloom/actions/runs/37231341735)
completed `large` and `normal`. The error scenario observed
`invalid→invalid@example.com→invalid`, with Save enabled then disabled, before
its extra Escape command timed out. The subsequent Simulator appearance
command also timed out. Those commands are not required to test the error
state: `large` already dismisses the keyboard and reaches Save. The review
therefore checks Japanese/dark before the error edit and ends the error
scenario after its final screenshot. The run's
[Artifact](https://github.com/9uiLe/evoloom/actions/runs/37231341735/artifacts/11313999117)
preserves the observed values, images, command exit and timeouts. This order
change does not alter the product screen or weaken the large-case keyboard
assertion.

The [final Cloud operation run on 2b3ed8f](https://github.com/9uiLe/evoloom/actions/runs/37232909641)
completed all four scenarios (`large`, `normal`, `japanese-dark`, `error`) and
the full CI job succeeded. Its
[Artifact](https://github.com/9uiLe/evoloom/actions/runs/37232909641/artifacts/11313679782)
contains 14 current `sim-use screenshot` PNGs, 39 UI JSON observations,
`actions.jsonl`, environment metadata and no failure marker. In that run,
Email moved from y=421 to y=61 during the Form swipe while the software
keyboard remained visible; after native Escape, Save was inside the actual
402×874 pt scene. Normal field values changed independently, the Toggle
returned to its original value after off/on, and the error fixture changed
`invalid→invalid@example.com→invalid` with the matching Save enabled/disabled
states. The manual sim-use step took 4m44s in this one run; the ordinary PR
CI does not run that step. The same head also passed the Package, host,
strict PNG comparison and copied-source checks in the
[normal PR run](https://github.com/9uiLe/evoloom/actions/runs/37232906912).

Visual snapshots remain strict RGBA comparisons and unchanged by this
operation review. A passing snapshot or readable accessibility tree is not a
VoiceOver test or evidence of persisted settings.
