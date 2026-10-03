# ShadcnIOS

An independent SwiftUI component foundation for iOS 26+. It supplies a calm
neutral theme and source-owned components, while leaving navigation and system
interactions to SwiftUI. It is not an official shadcn/ui or Apple project.

## Requirements

- Apple Silicon macOS with Xcode 27.0 build 27A266a selected at
  `/Applications/Xcode-27.0.0.app/Contents/Developer`.
- iOS Simulator SDK 27.0 build 24A430, runtime 27.0 build 24A434, and an
  available iPhone 18 Pro simulator. The commands verify these exact values.
- Nix with flakes enabled. Nix supplies the development tools and fixed
  SnapshotTesting source; Apple supplies Xcode, the SDK and Simulator.

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
        IOSCard {
            IOSInput("Name", text: $name, hint: "Shown to your team")
        }
    }
}
```

The root Package manifest has no external dependencies or generated local
paths. The snapshot test harness is a separate Package under `Testing/`.

## Own the source

```sh
nix develop -c python3 tools/shadcn_ios.py list
mkdir -p /tmp/my-ios-package
nix develop -c python3 tools/shadcn_ios.py dry-run --init --destination /tmp/my-ios-package button input
nix develop -c python3 tools/shadcn_ios.py init --destination /tmp/my-ios-package button input
```

Copied files live under `Sources/ShadcnIOSCopied`; use `ShadcnIOSCopied` as
the target name in a Swift Package, or add the files to your app target in
Xcode. No library import is needed in copied source. Existing files are
protected unless `--overwrite` is explicit. See [distribution](docs/DISTRIBUTION.md).

## Preview

Open `Package.swift` in Xcode, select the iPhone 18 Pro destination and
`Sources/ShadcnIOS/Preview/ComponentCatalog.swift`. Its `#Preview` entries
show light, dark, adjusted theme, and a native navigation/list/search/sheet
example. The fixture views are internal to the library target. The package
compilation verifies the preview source. The Xcode 27.0 canvas rendered the
light, dark, Collection and adjusted theme previews in the stated Simulator.
Image tests provide visual verification when the canvas is unavailable.

## Documents

[Design rules](DESIGN.md) · [Components](docs/COMPONENTS.md) ·
[Distribution](docs/DISTRIBUTION.md) · [Environment](docs/ENVIRONMENT.md) ·
[Testing](docs/TESTING.md) · [AI review prompt](docs/AI_REVIEW_PROMPT.md)
· [Validation record](docs/VALIDATION.md)

The working directory name is `shadcn-ios-native` because `shadcn-ios` was
already an unrelated Git checkout on the development host. This repository
has its own Git history and no remote.

Known limits: the Nix shell does not install Xcode or Simulator. The test
harness supports the fixed Apple Silicon environment above. Source copies
do not edit Xcode Target Membership. Snapshot tests detect pixel changes but
do not verify VoiceOver, keyboard flow or double submission.
