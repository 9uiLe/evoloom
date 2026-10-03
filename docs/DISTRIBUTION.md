# Distribution

The root `Package.swift` is a normal iOS library dependency. Outside the Nix
development shell it fetches the pinned `swift-app-macros` commit through
SwiftPM and needs no generated local path to load. The library includes the internal Preview
fixtures but does not expose them as public API. The separate `Testing` package
is only for visual tests.

Use `tools/shadcn_ios.py list`, `dry-run --destination DIR --init button`,
`init --destination DIR button`, or `add --destination DIR input`. Run the CLI
with `nix develop -c python3 ...` so Python comes from the fixed Nix shell.
`init` creates the common design tokens, config, license, notice and design rules. `add`
requires that initialization marker and resolves dependencies from
`tools/registry.json`. Copied Swift files import SwiftUI and `AppMacros`, but
do not import `ShadcnIOS`. Add the exact `swift-app-macros` commit recorded in
the root `Package.swift` as a package dependency, and attach its `AppMacros`
product to the target containing the copies. Nix development and copy
verification use the same source through local fixed paths. Macro code is a
compile-time dependency, while `EquatableBodyView` is a small runtime protocol
used by display-only components. The copied files own their UI source and can
be customized, but retain this macro dependency while using `@AutoEquatableView`.
Xcode may ask for approval before executing the macro plugin, including after
its source changes. Review the pinned revision and approve it in Xcode for an
interactive project. The package build check for a clean noninteractive
consumer used Xcode's `-skipMacroValidation` flag only after the fixed source
and revision were reviewed; this flag bypasses Xcode's approval prompt.

The CLI refuses unknown components, dependency cycles, existing files, unsafe
relative paths, symlinks on the destination path and unwritable paths. It
stages all content before replacing files, then restores previous file bytes
and removes newly written files if a replacement fails. Empty directories may
remain after an interrupted install and can be removed manually. An OS crash
between replacements can leave a partial install; inspect the printed plan,
compare with the registry and retry only with explicit `--overwrite` after
review. The CLI never silently updates customized tokens or components.
Copies made before the token refactor contain `Theme/Theme.swift`. The CLI
detects that file and stops. Back up your custom values, copy
`Sources/ShadcnIOS/Tokens/DesignTokens.swift` from this repository into the
copied target's `Tokens` directory, then apply your values there. Remove the
old file from Target Membership and disk before adding components. Compiling
both files together would duplicate public names. Compare the neutral values
before deleting the old file.

For an app project, add the copied Swift files to the app target with Xcode's
Target Membership inspector. The CLI does not edit `.xcodeproj` files. When
updating, diff the upstream component, your modified file and the new design
tokens; use `--overwrite` only after saving your edits. Retain `LICENSE`,
`NOTICE` and the copied `SHADCN-IOS-LICENSE` and `SHADCN-IOS-NOTICE`. The copy verification command
builds a temporary iOS Swift Package and runs a test without an app target.
