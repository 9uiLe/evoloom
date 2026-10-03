# Distribution

The root `Package.swift` is a normal iOS library dependency. It needs no Nix
path or generated file to load. The library includes the internal Preview
fixtures but does not expose them as public API. The separate `Testing` package
is only for visual tests.

Use `tools/shadcn_ios.py list`, `dry-run --destination DIR --init button`,
`init --destination DIR button`, or `add --destination DIR input`. Run the CLI
with `nix develop -c python3 ...` so Python comes from the fixed Nix shell.
`init` creates the common theme, config, license, notice and design rules. `add`
resolves dependencies from `tools/registry.json`. Copied Swift files import
only SwiftUI; they do not import `ShadcnIOS`.

The CLI refuses unknown components, dependency cycles, existing files, unsafe
relative paths, symlinks on the destination path and unwritable paths. It
stages all content before replacing files, then restores previous file bytes
and removes newly written files if a replacement fails. Empty directories may
remain after an interrupted install and can be removed manually. An OS crash
between replacements can leave a partial install; inspect the printed plan,
compare with the registry and retry only with explicit `--overwrite` after
review. The CLI never silently updates a customized theme or component.

For an app project, add the copied Swift files to the app target with Xcode's
Target Membership inspector. The CLI does not edit `.xcodeproj` files. When
updating, diff the upstream component, your modified file and the new design
tokens; use `--overwrite` only after saving your edits. Retain `LICENSE`,
`NOTICE` and the copied `SHADCN-IOS-LICENSE` and `SHADCN-IOS-NOTICE`. The copy verification command
builds a temporary iOS Swift Package and runs a test without an app target.
