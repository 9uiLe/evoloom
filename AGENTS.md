# Agent rules

Follow `CONTRIBUTING.md` and `DESIGN.md`. Do not add an App target, Xcode
project, global tool install, unpinned remote SwiftPM dependency, or floating
Simulator selection. Keep normal Package use independent of `.prepared`, and
use Nix-fixed local dependency sources for development and CI. Run format-check,
lint, CLI tests, Package tests, copy verification and snapshots through the
Nix `just` commands. Report exact evidence and any unrun checks.
