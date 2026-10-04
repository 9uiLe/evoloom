# Contributing

Use `Evoloom` for the Package, module and CLI. The public `IOS…` component
names describe the platform and are not part of the brand rename. Fresh
copies use `.evoloom.json`; never overwrite a legacy copy to migrate it.

Read `DESIGN.md`, `docs/ENVIRONMENT.md` and `docs/TESTING.md`. Keep iOS 26
compatibility, native control semantics, copyable sources, and the root
Package's normal SwiftPM consumer path. Keep product and copied source free
of test-only dependencies; Nix prepares SnapshotTesting for the visual test
Package. Preserve ordinary SwiftUI updates for actions, Bindings, child Views
and environment values. Measure an integrating screen before adding an update
suppression boundary. Update `tools/registry.json` when adding
a component. Include a Preview example, unit/CLI checks where behavior can
regress, and a visually reviewed PNG baseline for a new visual state.

Run `nix develop -c just format`, repeat it to check idempotence, then
`nix develop -c just check`. CI runs only `format-check`, never `format`.
When an image changes, record intentionally and explain the observed change
in the review. Never call an unrun simulator test successful.
