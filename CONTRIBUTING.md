# Contributing

Use `Evoloom` for the Package, module and CLI. The public `IOS…` component
names describe the platform and are not part of the brand rename. Fresh
copies use `.evoloom.json`; never overwrite a legacy copy to migrate it.

Read `DESIGN.md`, `docs/ENVIRONMENT.md` and `docs/TESTING.md`. Keep iOS 26
compatibility, native control semantics, copyable sources, and the root
Package's normal SwiftPM consumer path. Pin macro revisions; materialize the
same sources through Nix local paths for development and CI. Use
`@AutoEquatableView` on component Views and reserve its equality boundary for
comparable parent inputs. Do not mark actions, Bindings, or arbitrary child
Views as safe to skip without a test showing changed inputs remain current.
Update `tools/registry.json` when adding
a component. Include a Preview example, unit/CLI checks where behavior can
regress, and a visually reviewed PNG baseline for a new visual state.

Run `nix develop -c just format`, repeat it to check idempotence, then
`nix develop -c just check`. CI runs only `format-check`, never `format`.
When an image changes, record intentionally and explain the observed change
in the review. Never call an unrun simulator test successful.
