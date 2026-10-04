## Reason and scope

Describe the observed issue or design question, the screens and states affected, and what changed.

## Representative images

Paste the output of `nix develop -c python3 tools/pr_images.py --sha <full-commit-SHA>` for UI changes. Add before and after images for changed cases. Label baseline images separately from actual CI renders. Link the CI run for the same SHA after comparison succeeds. See `docs/VISUAL_REVIEW.md`.

## Verification and review

- Capture environment: Xcode build, Simulator runtime build, device, width, scale, locale, Dynamic Type and appearance.
- Commands and results:
- CI run, PR head/image commit SHA, and actual checkout SHA (which may be a merge commit):
- Visual review findings and remaining questions:

Snapshots protect an accepted appearance from regression; image comparison does not approve design quality or verify VoiceOver behavior.
