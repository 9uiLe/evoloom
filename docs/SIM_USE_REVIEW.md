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
Japanese/dark appearance, and an outlined input edit. Each scenario follows
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

`--reuse-built-host` assumes the current source was already built and installed
with `just run-host`; omit it for an independently reproducible run. Scenarios
are `normal`, `error`, `large`, `japanese-dark`, and `outlined`. The manual GitHub Actions
`workflow_dispatch` input `verify_settings_interaction` runs this command in
the existing iOS job after the image tests and uploads the resulting evidence
with the usual `ios-test-evidence` artifact. Ordinary PR CI keeps its current
snapshot and Package checks without the extra operation session.

The `normal` and `error` scenarios check Display name and Email editing,
focus movement, native Toggle value `1→0→1`, initial error and disabled Save,
disabled Workspace, error removal for a value containing `@`, and error return
when the value no longer contains `@`. They deliberately check the fixture's current
condition, not business-grade email validation. Paste can show the iOS
permission bubble or edit menu; the script checks the resulting field value.
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
still focused fields and hardware-key input changed text. A subsequent full
script run reported `normal` and `error` failures because the iOS paste menu
did not produce the required exact values; `large` also failed its
`visible:true` requirement. `japanese-dark` and `outlined` completed. The
first manual operation session above did establish the normal-size state
transitions, but the automated full run is **not passing** and keyboard-visible
large-text scrolling remains unverified. On this host, opening Device Hub,
relaunching the app, restarting the target Simulator, and temporarily setting
the legacy Simulator `ConnectHardwareKeyboard=false` preference did not
restore it. A temporary simulator language change to English also did not
restore it; both temporary preferences were reverted. This is an observed host
state, not a diagnosed Evoloom or sim-use defect. On a host where the software
keyboard appears, rerun `just verify-settings-interaction` and review its
fresh PNG and UI evidence before closing that gap. Do not use the earlier
normal-size keyboard screenshot to claim the large-text combination passed.

Visual snapshots remain strict RGBA comparisons and unchanged by this
operation review. A passing snapshot or readable accessibility tree is not a
VoiceOver test or evidence of persisted settings.
