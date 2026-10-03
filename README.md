# ShadcnIOS

An independent SwiftUI component foundation for iOS 26+. It supplies a calm
neutral design tokens and source-owned components, while leaving navigation and system
interactions to SwiftUI. It is not an official shadcn/ui or Apple project.

## Requirements

- Apple Silicon macOS with Xcode 27.0 build 27A266a selected at
  `/Applications/Xcode-27.0.0.app/Contents/Developer`.
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

Add this package to an iOS 26+ Xcode project, choose its `ShadcnIOS` library
product, then:

```swift
import ShadcnIOS
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

The root Package manifest pins `swift-app-macros` to an exact commit for normal
SwiftPM consumers. Xcode may request approval to run the package's macro
plugin on first use; review the pinned source and approve it in Xcode. In the
Nix development shell the manifest uses the locally prepared,
Nix-fixed source instead. Run `just prepare-deps` before opening the Package
in Xcode from that shell. The snapshot test harness is a separate Package
under `Testing/`.

## Own the source

```sh
nix develop -c python3 tools/shadcn_ios.py list
mkdir -p /tmp/my-ios-package
nix develop -c python3 tools/shadcn_ios.py dry-run --init --destination /tmp/my-ios-package button input
nix develop -c python3 tools/shadcn_ios.py init --destination /tmp/my-ios-package button input
```

Copied files live under `Sources/ShadcnIOSCopied`; use `ShadcnIOSCopied` as
the target name in a Swift Package, or add the files to your app target in
Xcode. Copied source imports `AppMacros`, but not `ShadcnIOS`; add the pinned
`AppMacros` product to the target. Existing files are
protected unless `--overwrite` is explicit. See [distribution](docs/DISTRIBUTION.md).

## Preview

Open `Package.swift` in Xcode, select the iPhone 18 Pro destination and
`Sources/ShadcnIOS/Preview/ComponentCatalog.swift`. Its `#Preview` entries
show light, dark, adjusted design tokens, and a native navigation/list/search/sheet
example. The fixture views are internal to the library target. The package
compilation verifies the preview source. The Xcode 27.0 canvas rendered the
light, dark, Collection and adjusted token previews in the stated Simulator.
Image tests provide visual verification when the canvas is unavailable.

## Documents

[Design rules](DESIGN.md) · [Components](docs/COMPONENTS.md) ·
[Distribution](docs/DISTRIBUTION.md) · [Environment](docs/ENVIRONMENT.md) ·
[Testing](docs/TESTING.md) · [AI review prompt](docs/AI_REVIEW_PROMPT.md)
· [Validation record](docs/VALIDATION.md)

The working directory name is `shadcn-ios-native` because `shadcn-ios` was
already an unrelated Git checkout on the development host. The GitHub
repository is independent of that checkout.

Known limits: the Nix shell does not install Xcode or Simulator. The test
harness supports the fixed Apple Silicon environment above. Source copies
do not edit Xcode Target Membership. Snapshot tests detect pixel changes but
do not verify VoiceOver, keyboard flow or double submission.
