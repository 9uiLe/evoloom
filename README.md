# Evoloom

Evoloom (エヴォルーム, from Evolve + Loom) is a SwiftUI component collection for
iOS 26+. It starts with consistent design decisions and lets you own and edit
the component source as your product grows. Compose screens with shared tokens
and native SwiftUI navigation and controls. The public `IOS…` component names
remain unchanged.

Evoloom owns recurring visual choices and component semantics. The integrating
product owns screen structure, user flow, contextual accessibility and final
VoiceOver validation. See [design rules](DESIGN.md).

## Requirements

- Apple Silicon macOS 27.0 build 26A428 with Xcode 27.0 build 27A266a.
  Locally, Nix defaults `DEVELOPER_DIR` to
  `/Applications/Xcode-27.0.0.app/Contents/Developer`; CI sets the equivalent
  path on GitHub's `xcode-27` runner.
- iOS Simulator SDK 27.0 build 24A430, runtime 27.0 build 24A434, and an
  available iPhone 18 Pro simulator. The commands verify these exact values.
- Nix with flakes enabled. Nix supplies the development tools and fixed
  SnapshotTesting source; Apple supplies Xcode, the SDK and Simulator.

## Start

```sh
nix develop
just doctor
just prepare-deps
just check-fast
just check
```

`just check-fast` runs formatting, lint and Python/CLI tests without Xcode.
`just check` runs those checks plus package unit/fixed-size image tests and a
scene-backed collection image session, then builds a Package from all copied
components. The iOS test builds compile the library, Preview fixtures and
development-only app host; `just build-package`
remains an independent product build command. Run `just record-snapshots` only to update
image baselines; review PNGs in both `Testing/Tests/.../__Snapshots__/` and
`Testing/Host/Tests/__Snapshots__/` plus the two record xcresults before committing. Normal comparison refuses
missing baselines or changed baseline files. See [testing](docs/TESTING.md).

## Use as a library

Add `https://github.com/9uiLe/evoloom` to an iOS 26+ Xcode project,
choose its `Evoloom` library product, then:

```swift
import Evoloom
import SwiftUI

struct Example: View {
    @State private var name = ""
    var body: some View {
        var tokens = IOSDesignTokens.neutral
        tokens.light.primary = .indigo
        tokens.light.primaryForeground = .white
        return IOSCard {
            IOSInput("Name", text: $name, hint: "Shown to your team")
        }
        .iosDesignTokens(tokens)
    }
}
```

The library has no external Swift dependency. Normal SwiftPM consumers can
read the root manifest without `.prepared`. Development and CI use Nix to
prepare the test-only SnapshotTesting source for the separate Package under
`Testing/`; run `just prepare-deps` before its tests.

## Own the source

```sh
nix develop -c python3 tools/evoloom.py list
mkdir -p /tmp/my-ios-package
nix develop -c python3 tools/evoloom.py dry-run --init --destination /tmp/my-ios-package button input
nix develop -c python3 tools/evoloom.py init --destination /tmp/my-ios-package button input
```

Copied files live under `Sources/EvoloomCopied`; use `EvoloomCopied` as
the target name in a Swift Package, or add the files to your app target in
Xcode. Copied source imports SwiftUI without requiring `Evoloom` or a macro
product. Existing files are protected unless `--overwrite` is explicit. See
[distribution and migration](docs/DISTRIBUTION.md).

## Preview

Open `Testing/Package.swift` in Xcode, select the fixed iPhone 18 Pro
destination, and open `Testing/Sources/EvoloomReviewFixtures/` for the
component pages, Settings Form, collection List, detail/edit screen, simulated
Button state transitions and
their named `#Preview` entries. These fixtures are in the development Package,
not the consumer library. `just test-ios` compiles them and compares their
fixed real-render images; opening Canvas is a separate manual check.
Run `nix develop -c just run-host collection normal light` to see the same
fixture in the development-only app with a real scene. The checked-in host
project definition is JSON; `just prepare-host` generates its ignored Xcode
project through Nix-pinned XcodeGen. This is separate from Xcode's native
`project.xcproj` JSON format, which the pinned Xcode 27.0 could not generate.
See [visual review and PR images](docs/VISUAL_REVIEW.md).
For Simulator taps, editing, Toggle and scrolling, run
`nix develop -c just verify-settings-interaction`,
`nix develop -c just verify-detail-interaction` or
`nix develop -c just verify-button-transition`. Read the
[Settings operation guide](docs/SIM_USE_REVIEW.md) and
[Detail/Button review](docs/DETAIL_BUTTON_REVIEW.md). The Nix shell supplies
sim-use; these optional operation checks are separate from normal snapshot CI.

## Documents

[Design rules](DESIGN.md) · [Components](docs/COMPONENTS.md) ·
[Distribution](docs/DISTRIBUTION.md) · [Environment](docs/ENVIRONMENT.md) ·
[Testing](docs/TESTING.md) · [CI timing](docs/CI_PERFORMANCE.md) ·
[Visual review](docs/VISUAL_REVIEW.md) ·
[Settings operation review](docs/SIM_USE_REVIEW.md) ·
[Detail/Button review](docs/DETAIL_BUTTON_REVIEW.md) ·
[AI review prompt](docs/AI_REVIEW_PROMPT.md)
· [Validation record](docs/VALIDATION.md)

## Inspiration and repository status

Evoloom takes inspiration from [shadcn/ui](https://ui.shadcn.com/docs): open
component code, composition, and source ownership. It is an independent
SwiftUI project, with no affiliation or endorsement by shadcn/ui or Apple.
The public GitHub repository is `9uiLe/evoloom`. GitHub-hosted Actions select
checks from the cumulative change since the last fully validated ancestor;
static checks use Linux and iOS checks use the fixed `xcode-27` runner.
Documentation-only changes after a full validation skip Nix and tests; manual
runs execute the complete suite. The doctor fails if the Apple versions or
Simulator differ from the baselines. See the [CI matrix](docs/TESTING.md).

The module rename is a breaking change: replace `import ShadcnIOS` with
`import Evoloom` and select the `Evoloom` product. Existing copied source is
not automatically migrated or overwritten. Follow the migration steps in the
[distribution guide](docs/DISTRIBUTION.md).

Known limits: the Nix shell does not install Xcode or Simulator. The test
harness supports the fixed Apple Silicon environment above. Source copies
do not edit Xcode Target Membership. Snapshot tests detect pixel changes but
do not verify VoiceOver, keyboard flow or double submission.
