"""Compare scene-backed captures after the hosted XCTest process has exited."""

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

from PIL import Image, ImageChops, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
HOST_DIRECTORY = "Testing/Host/Tests/__Snapshots__/HostedCollectionTests/"


def manifest_cases(root):
    paths = json.loads((root / "tools/snapshots.json").read_text())
    cases = {
        Path(path).stem.removeprefix("components."): root / path
        for path in paths
        if path.startswith(HOST_DIRECTORY)
    }
    allowed_names = {Path(path).name for path in paths}
    if len(cases) != 5 or len(allowed_names) != len(paths):
        raise ValueError("Snapshot manifest has duplicate or missing hosted cases")
    return cases, allowed_names


def normalized_pixels(path):
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError(f"Expected PNG at {path}, got {image.format}")
        image.load()
        return image.convert("RGBA")


def write_difference(expected, actual, destination):
    if expected.size != actual.size:
        image = Image.new(
            "RGBA",
            (max(expected.width, actual.width), max(expected.height, actual.height)),
            (255, 0, 80, 255),
        )
    else:
        channels = ImageChops.difference(expected, actual).split()
        changed = channels[0]
        for channel in channels[1:]:
            changed = ImageChops.lighter(changed, channel)
        changed = changed.point([0] + [255] * 255)
        image = Image.new("RGBA", expected.size, (255, 255, 255, 255))
        image.paste((255, 0, 80, 255), mask=changed)
    image.save(destination)


def compare(cases, rendered, differences, report_path, allowed_names=None):
    started = time.monotonic()
    results = []
    for name, baseline in sorted(cases.items()):
        actual = rendered / f"components.{name}.png"
        item = {"case": name, "baseline": str(baseline), "actual": str(actual)}
        if not baseline.is_file():
            item.update(status="missing_baseline")
        elif not actual.is_file():
            item.update(status="missing_actual")
        else:
            try:
                old = normalized_pixels(baseline)
                new = normalized_pixels(actual)
                if old.size == new.size and old.tobytes() == new.tobytes():
                    item.update(status="matched", size=list(old.size))
                else:
                    folder = differences / name
                    folder.mkdir(parents=True, exist_ok=True)
                    old.save(folder / "expected.png")
                    new.save(folder / "actual.png")
                    write_difference(old, new, folder / "diff.png")
                    item.update(
                        status="dimension_mismatch"
                        if old.size != new.size
                        else "pixel_mismatch",
                        expected_size=list(old.size),
                        actual_size=list(new.size),
                        difference=str(folder),
                    )
            except (OSError, ValueError, UnidentifiedImageError) as error:
                item.update(status="invalid_image", error=str(error))
        results.append(item)
    if allowed_names is not None:
        for path in sorted(rendered.glob("*.png")):
            if path.name not in allowed_names:
                results.append(
                    {
                        "case": path.stem,
                        "actual": str(path),
                        "status": "unexpected_actual",
                    }
                )
    report = {
        "passed": all(item["status"] == "matched" for item in results),
        "case_count": len(cases),
        "seconds": round(time.monotonic() - started, 3),
        "cases": results,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    return report


def record(cases, rendered):
    missing = [
        name for name in cases if not (rendered / f"components.{name}.png").is_file()
    ]
    if missing:
        raise RuntimeError(f"Cannot record missing hosted images: {missing}")
    for name in cases:
        normalized_pixels(rendered / f"components.{name}.png")
    for name, baseline in cases.items():
        actual = rendered / f"components.{name}.png"
        baseline.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(actual, baseline)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="Compare one hosted case for diagnosis")
    arguments = parser.parse_args()
    cases, allowed_names = manifest_cases(ROOT)
    if arguments.case:
        if arguments.case not in cases:
            parser.error(f"Unknown hosted case: {arguments.case}")
        cases = {arguments.case: cases[arguments.case]}
    report = compare(
        cases,
        ROOT / "TestResults/Rendered",
        ROOT / "TestResults/SnapshotDiffs",
        ROOT / "TestResults/host-image-comparison.json",
        allowed_names,
    )
    for item in report["cases"]:
        print(f"{item['case']}: {item['status']}", flush=True)
    print(
        f"Hosted image comparison: {'passed' if report['passed'] else 'failed'}",
        flush=True,
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
