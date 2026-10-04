# Agent rules

The library Package, product and import module are named `Evoloom`. Keep
shadcn/ui references only for attribution and design context, and preserve
the original copyright notice in `LICENSE`.

Follow `CONTRIBUTING.md` and `DESIGN.md`. `Testing/Host/` contains the sole
development-only app and Xcode project definition for scene-backed visual
tests; keep it out of the library product and copied sources. Do not add a
distribution app, global tool install, unpinned remote SwiftPM dependency, or floating
Simulator selection. Keep normal Package use independent of `.prepared`, and
use Nix-fixed local dependency sources for development and CI. Run format-check,
lint, CLI tests, Package tests, copy verification and snapshots through the
Nix `just` commands. Report exact evidence and any unrun checks.
