# Distribution and migration

## Use the library or own the source

The root `Package.swift` provides the `Evoloom` library product for iOS 26+.
The repository URL is `https://github.com/9uiLe/evoloom`. The library has no
external Swift dependency for ordinary SwiftPM consumers. Internal Preview
fixtures compile with the library but are not public API. The separate
`Testing` package uses Nix-prepared SnapshotTesting for visual tests.

To copy source, run `nix develop -c python3 tools/evoloom.py list`, then use
`dry-run --init --destination DIR button`, `init --destination DIR button`, or
`add --destination DIR input` with the same CLI prefix. `init` creates
`Sources/EvoloomCopied`, `.evoloom.json`, `EVOLOOM-LICENSE`,
`EVOLOOM-NOTICE`, and `EVOLOOM-DESIGN.md`. `add` requires the new config and
resolves dependencies from `tools/registry.json`. A copied component includes
the shared design tokens when needed. Existing files are protected unless
`--overwrite` is explicit.

Copied Swift files import SwiftUI, not `Evoloom` or `AppMacros`. The target
containing copies needs no package dependency from Evoloom. Existing copies
from the macro-based version retain `import AppMacros` until the owner reviews
and replaces those files. The CLI will not overwrite edited files by default;
compare local customizations with the current source before explicitly using
`--overwrite` or migrating edits manually.
After migrating all copied components, remove the `AppMacros` product and
`swift-app-macros` package reference only if no other code in the integrating
target uses them. The new `cardMutedForeground` initializer parameter is
optional; existing palette construction remains source-compatible. Set it
explicitly when a custom Card needs a distinct supporting text color.

This source simplification changes two public implementation-facing contracts:
`equatableBody` is now `body`, and the five display-only component types no
longer conform to `Equatable` or `EquatableBodyView`. Calls to a component's
`equatableBody`, comparisons such as `IOSBadge(...) == IOSBadge(...)`, or
`.equatable()` applied directly to those components need migration. Compare
the product's own state where equality matters, or add a locally measured
comparison boundary around its composed View. Normal component construction,
Bindings, actions, token injection and iOS 26 availability are unchanged.

For an app project, add the copied Swift files to the app target with Xcode's
Target Membership inspector. The CLI does not edit `.xcodeproj` files. For a
standalone copied Package, name its library target `EvoloomCopied`. The
repository's `just verify-copy-install` creates such a temporary iOS Package
from every registry component and builds its library for the iOS Simulator
without an app target. Python tests cover the CLI plan, source selection and
customization protection; the copied Package build covers Swift compilation,
not runtime interaction.

## Move from the former package or a former copy

This unreleased package makes a breaking rename. Existing library consumers
must select the `Evoloom` product and replace `import ShadcnIOS` with
`import Evoloom`; the public `IOS…` type names are unchanged. Update the
SwiftPM repository URL from `9uiLe/shadcn-ios-native` to `9uiLe/evoloom` in
the integrating project. GitHub may redirect the former URL, but the new URL
is the documented dependency identity.

| Before | Now |
| --- | --- |
| Package, product and module `ShadcnIOS` | `Evoloom` |
| Test targets `ShadcnIOSTests`, `ShadcnIOSSnapshotTests` | `EvoloomTests`, `EvoloomSnapshotTests` |
| CLI `tools/shadcn_ios.py` | `tools/evoloom.py` |
| `.shadcn-ios.json`, `Sources/ShadcnIOSCopied` | `.evoloom.json`, `Sources/EvoloomCopied` |

The new CLI refuses a destination containing `.shadcn-ios.json` or
`Sources/ShadcnIOSCopied`, including when `.evoloom.json` also exists or
`--overwrite` is supplied. It does not reinterpret the old config, reset
tokens, copy into a second target, or delete customized files. To migrate:

1. Back up the old config and copied source **outside** the destination.
   Compare customized tokens and components with the current source.
2. Remove `Sources/ShadcnIOSCopied` from Xcode Target Membership, then move
   that directory and `.shadcn-ios.json` out of the destination. Keep the
   existing `SHADCN-IOS-LICENSE` and `SHADCN-IOS-NOTICE` as provenance records.
3. Run `dry-run --init` and `init` with `tools/evoloom.py` on the destination.
   Reapply desired changes to the new copied files, review the diff, and add
   the new files to Target Membership. Do not compile both copies together.
4. Build the integrating Package or app and verify its behavior before
   discarding the backup. Retain `LICENSE`, `NOTICE`, and all applicable
   copied notices when distributing the result.

The CLI also refuses unknown components, dependency cycles, unsafe paths,
symlinks on the destination path, and unwritable paths. It stages content
before replacement and restores previous file bytes after a caught failure;
empty directories may remain. An OS crash between replacements may leave a
partial install. Inspect the printed plan and files before retrying with
explicit `--overwrite`.
