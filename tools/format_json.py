"""Format and validate the checked-in JSON manifests."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = (ROOT / "tools/registry.json", ROOT / "tools/snapshots.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = []
    for path in FILES:
        value = json.loads(path.read_text())
        formatted = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        if path.read_text() != formatted:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(formatted)
    if changed:
        print("JSON formatting changed: " + ", ".join(changed))
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
