# Evoloom

Evoloom (エヴォルーム, from Evolve + Loom) is a SwiftUI component collection for
iOS 26+. It starts with consistent design decisions and lets you own and edit
the component source as your product grows. Compose screens with shared tokens
and native SwiftUI navigation and controls. The public `IOS…` component names
remain unchanged.

## Requirements

- Apple Silicon macOS 27.0 build 26A428 with Xcode 27.0 build 27A266a.
  Locally, Nix defaults `DEVELOPER_DIR` to
  `/Applications/Xcode-27.0.0.app/Contents/Developer`; CI sets the equivalent
  path on GitHub's `xcode-27` runner.
- iOS Simulator SDK 27.0 build 24A430, runtime 27.0 build 24A434, and an
  available iPhone 18 Pro simulator. The commands verify these exact values.
- Nix with flakes enabled. Nix supplies the development tools and fixed
  SnapshotTesting, AppMacros and swift-syntax sources; Apple supplies Xcode,
  the SDK and Simulator.

## Start

```sh
nix develop
just doctor
just prepare-deps
just check
```

`just check` checks formatting, lint, CLI, iOS Package builds, unit tests,
copied source and image snapshots. Run `just record-snapshots` only to update
image baselines; review every PNG in `Testing/Tests/.../__Snapshots__/` and
the `TestResults/record.xcresult` before committing. Normal comparison refuses
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

The root Package manifest pins `swift-app-macros` 0.4.0 to its release commit
for normal SwiftPM consumers. Xcode may request approval to run the package's
macro plugin on first use; review the pinned source and approve it in Xcode. In the
Nix development shell the manifest uses the locally prepared,
Nix-fixed source instead. Run `just prepare-deps` before opening the Package
in Xcode from that shell. The snapshot test harness is a separate Package
under `Testing/`.

## Own the source

```sh
nix develop -c python3 tools/evoloom.py list
mkdir -p /tmp/my-ios-package
nix develop -c python3 tools/evoloom.py dry-run --init --destination /tmp/my-ios-package button input
nix develop -c python3 tools/evoloom.py init --destination /tmp/my-ios-package button input
```

Copied files live under `Sources/EvoloomCopied`; use `EvoloomCopied` as
the target name in a Swift Package, or add the files to your app target in
Xcode. Copied source imports `AppMacros`, but not `Evoloom`; add the pinned
`AppMacros` product to the target. Existing files are
protected unless `--overwrite` is explicit. See [distribution and migration](docs/DISTRIBUTION.md).

## Preview

Open `Package.swift` in Xcode, select the iPhone 18 Pro destination and
`Sources/Evoloom/Preview/ComponentCatalog.swift`. Its `#Preview` entries
show light, dark, adjusted design tokens, and a native navigation/list/search/sheet
example. The fixture views are internal to the library target. The package
compilation verifies the preview source. Before this rename, the Xcode 27.0
canvas rendered the light, dark, Collection and adjusted token previews in the
stated Simulator.
Image tests provide visual verification when the canvas is unavailable.

## Documents

[Design rules](DESIGN.md) · [Components](docs/COMPONENTS.md) ·
[Distribution](docs/DISTRIBUTION.md) · [Environment](docs/ENVIRONMENT.md) ·
[Testing](docs/TESTING.md) · [AI review prompt](docs/AI_REVIEW_PROMPT.md)
· [Validation record](docs/VALIDATION.md)

## Inspiration and repository status

Evoloom takes inspiration from [shadcn/ui](https://ui.shadcn.com/docs): open
component code, composition, and source ownership. It is an independent
SwiftUI project, with no affiliation or endorsement by shadcn/ui or Apple.
The public GitHub repository is `9uiLe/evoloom`. GitHub-hosted Actions run the
same Nix preparation and `just check` commands on the `xcode-27` runner; the
doctor fails if the Apple versions or Simulator differ from the baselines.

The module rename is a breaking change: replace `import ShadcnIOS` with
`import Evoloom` and select the `Evoloom` product. Existing copied source is
not automatically migrated or overwritten. Follow the migration steps in the
[distribution guide](docs/DISTRIBUTION.md).

Known limits: the Nix shell does not install Xcode or Simulator. The test
harness supports the fixed Apple Silicon environment above. Source copies
do not edit Xcode Target Membership. Snapshot tests detect pixel changes but
do not verify VoiceOver, keyboard flow or double submission.
