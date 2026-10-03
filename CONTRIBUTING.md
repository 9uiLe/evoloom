# Contributing

Read `DESIGN.md`, `docs/ENVIRONMENT.md` and `docs/TESTING.md`. Keep iOS 17
compatibility, native control semantics, copyable sources, and the root
Package's dependency-free manifest. Update `tools/registry.json` when adding
a component. Include a Preview example, unit/CLI checks where behavior can
regress, and a visually reviewed PNG baseline for a new visual state.

Run `nix develop -c just format`, repeat it to check idempotence, then
`nix develop -c just check`. CI runs only `format-check`, never `format`.
When an image changes, record intentionally and explain the observed change
in the review. Never call an unrun simulator test successful.
