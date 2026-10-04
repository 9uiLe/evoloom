"""Print SHA-pinned baseline images for an Evoloom UI review PR."""

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = "Testing/Tests/EvoloomSnapshotTests/__Snapshots__/ComponentSnapshots"
PAIRS = (
    (
        "Components · controls",
        "review-components-controls-light",
        "review-components-controls-dark",
    ),
    (
        "Components · feedback",
        "review-components-feedback-light",
        "review-components-feedback-dark",
    ),
    ("Settings", "review-settings-light", "review-settings-dark"),
    ("List", "collection-light", "collection-dark"),
    ("Detail / edit", "review-detail-light", "review-detail-dark"),
)


def markdown(sha, ci_url=None):
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Use a full 40-character lowercase commit SHA")
    lines = [
        "These are **committed baseline PNGs**, not images downloaded from this CI run.",
        f"Image commit: `{sha}`. Capture: Xcode 27.0 (27A266a), iOS 27.0 Simulator (24A434),",
        "iPhone 18 Pro, arm64; 390 pt width, 3× scale, en_US, UTC, standard Dynamic Type.",
    ]
    if ci_url:
        lines.append(f"CI comparison for this SHA: {ci_url}")
    else:
        lines.append(
            "CI comparison: pending; do not describe these baselines as verified actuals yet."
        )
    lines.extend(
        ("", "| Screen | Light baseline | Dark baseline |", "| --- | --- | --- |")
    )
    for label, light, dark in PAIRS:
        urls = []
        for name in (light, dark):
            path = f"{SNAPSHOTS}/components.{name}.png"
            if not (ROOT / path).is_file():
                raise FileNotFoundError(
                    f"Missing baseline: {path}; run just record-snapshots"
                )
            url = f"https://raw.githubusercontent.com/9uiLe/evoloom/{sha}/{path}"
            urls.append(f"![{label} {name}]({url})")
        lines.append(f"| {label} | {urls[0]} | {urls[1]} |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sha", help="Full commit SHA containing the baselines; defaults to HEAD"
    )
    parser.add_argument(
        "--ci-url", help="Successful comparison run URL for that exact SHA"
    )
    args = parser.parse_args()
    sha = (
        args.sha
        or subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    )
    print(markdown(sha, args.ci_url), end="")


if __name__ == "__main__":
    main()
