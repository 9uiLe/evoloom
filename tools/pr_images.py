"""Print SHA-pinned baseline images for an Evoloom UI review PR."""

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = "Testing/Tests/EvoloomSnapshotTests/__Snapshots__/ComponentSnapshots"
HOSTED_SNAPSHOTS = "Testing/Host/Tests/__Snapshots__/HostedCollectionTests"
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


def _git_object_type(root, object_name):
    result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-t", object_name],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def markdown(sha, ci_url=None, root=None):
    root = root or ROOT
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Use a full 40-character lowercase commit SHA")
    if _git_object_type(root, sha) != "commit":
        raise ValueError(
            f"Commit {sha} is unavailable locally or is not a commit object; "
            "fetch that exact commit (including in a shallow checkout) and retry"
        )
    names = [name for _, light, dark in PAIRS for name in (light, dark)]
    paths = [snapshot_path(name) for name in names]
    missing = [
        path for path in paths if _git_object_type(root, f"{sha}:{path}") != "blob"
    ]
    if missing:
        raise FileNotFoundError(
            f"Commit {sha} has no image blob at: {', '.join(missing)}; "
            "commit the recorded baselines before generating PR links"
        )
    lines = [
        "These are **committed baseline PNGs**, not images downloaded from this CI run.",
        f"Image commit: `{sha}`. Capture: Xcode 27.0 (27A266a), iOS 27.0 Simulator (24A434),",
        "iPhone 18 Pro, arm64; component/settings/detail: 390 pt fixed host; list: 402 × 874 pt scene-backed app host;",
        "3× scale, en_US, UTC, standard Dynamic Type.",
    ]
    if ci_url:
        lines.append(f"PR CI run for this image commit as head: {ci_url}")
        lines.append(
            "PR CI may validate a synthetic merge commit; report its checkout SHA from ci-report.json separately."
        )
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
            path = snapshot_path(name)
            url = f"https://raw.githubusercontent.com/9uiLe/evoloom/{sha}/{path}"
            urls.append(f"![{label} {name}]({url})")
        lines.append(f"| {label} | {urls[0]} | {urls[1]} |")
    return "\n".join(lines) + "\n"


def snapshot_path(name):
    directory = (
        HOSTED_SNAPSHOTS
        if name in {"collection-light", "collection-dark"}
        else SNAPSHOTS
    )
    return f"{directory}/components.{name}.png"


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
    try:
        body = markdown(sha, args.ci_url)
    except (FileNotFoundError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    print(body, end="")


if __name__ == "__main__":
    main()
