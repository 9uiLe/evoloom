"""Keep prepared Swift sources tied to the Nix inputs selected by the shell."""

import hashlib
import json
import os
from pathlib import Path

SOURCE_WITNESSES = {
    "SNAPSHOT_SOURCE": "Sources/SnapshotTesting",
}
PREPARED_MANIFESTS = ("SnapshotTesting/Package.swift",)
STAMP = "sources.json"


def nix_sources():
    sources = {}
    for name, witness in SOURCE_WITNESSES.items():
        value = os.environ.get(name)
        if not value or not (Path(value) / witness).is_dir():
            raise RuntimeError(f"Nix source {name} is missing; run nix develop")
        sources[name] = str(Path(value).resolve())
    return sources


def record_prepared_sources(directory, sources):
    (directory / STAMP).write_text(
        json.dumps(
            {"sources": sources, "files": prepared_hashes(directory)}, sort_keys=True
        )
        + "\n"
    )


def prepared_hashes(directory):
    root = directory / "SnapshotTesting"
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def verify_prepared_sources(directory):
    missing = [name for name in PREPARED_MANIFESTS if not (directory / name).is_file()]
    if missing:
        raise RuntimeError(
            f"Prepared dependencies missing: {missing}; run just prepare-deps inside nix develop"
        )
    try:
        recorded = json.loads((directory / STAMP).read_text())
    except (OSError, ValueError) as error:
        raise RuntimeError(
            "Prepared source record missing or invalid; run just prepare-deps inside nix develop"
        ) from error
    if not isinstance(recorded, dict) or recorded.get("sources") != nix_sources():
        raise RuntimeError(
            "Prepared sources differ from current Nix inputs; run just prepare-deps inside nix develop"
        )
    if recorded.get("files") != prepared_hashes(directory):
        raise RuntimeError(
            "Prepared source files changed or are incomplete; run just prepare-deps inside nix develop"
        )
