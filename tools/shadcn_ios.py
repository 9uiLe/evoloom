"""Source-owning distribution CLI. Uses only Python's standard library."""

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "tools" / "registry.json").read_text())
COPY_ROOT = Path("Sources/ShadcnIOSCopied")


class InstallError(Exception):
    pass


def resolve(names, registry=REGISTRY):
    """Topological order; errors on unknown names and cycles."""
    ordered = []
    visiting = set()
    visited = set()

    def visit(name):
        if name not in registry:
            raise InstallError(f"Unknown component: {name}")
        if name in visiting:
            raise InstallError(f"Dependency cycle at {name}")
        if name in visited:
            return
        visiting.add(name)
        for dependency in registry[name]["dependencies"]:
            visit(dependency)
        visiting.remove(name)
        visited.add(name)
        ordered.append(name)

    for name in names:
        visit(name)
    return ordered


def source_for(name):
    relative = Path(REGISTRY[name]["source"])
    source = (ROOT / relative).resolve()
    if not source.is_relative_to(ROOT) or not source.is_file() or source.is_symlink():
        raise InstallError(f"Unsafe or missing source: {relative}")
    return source


def safe_destination(root, relative):
    if relative.is_absolute() or ".." in relative.parts:
        raise InstallError(f"Unsafe path: {relative}")
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise InstallError(f"Symlink path rejected: {current}")
    if not current.resolve().is_relative_to(root.resolve()):
        raise InstallError(f"Path escapes destination: {relative}")
    return current


def plan(root, names, initialize=False, overwrite=False):
    if root.is_symlink():
        raise InstallError("Destination symlink rejected")
    if not root.is_dir():
        raise InstallError(f"Destination directory missing: {root}")
    files = {}
    for name in resolve(["theme", *names] if initialize else names):
        source = source_for(name)
        relative = (
            COPY_ROOT / ("Theme" if name == "theme" else "Components") / source.name
        )
        if (
            not initialize
            and name not in names
            and safe_destination(root, relative).is_file()
        ):
            continue
        files[relative] = source.read_bytes()
    if initialize:
        files[Path(".shadcn-ios.json")] = (
            b'{"source": "shadcn-ios", "copyRoot": "Sources/ShadcnIOSCopied"}\n'
        )
        files[Path("SHADCN-IOS-LICENSE")] = (ROOT / "LICENSE").read_bytes()
        files[Path("SHADCN-IOS-NOTICE")] = (ROOT / "NOTICE").read_bytes()
        files[Path("SHADCN-IOS-DESIGN.md")] = (ROOT / "DESIGN.md").read_bytes()
    for relative in files:
        target = safe_destination(root, relative)
        if target.exists() and not overwrite:
            raise InstallError(
                f"Conflict: {target}; use --overwrite only after reviewing changes"
            )
        if target.exists() and not os.access(target, os.W_OK):
            raise InstallError(f"Unwritable file: {target}")
        parent = target.parent
        while parent != root.parent:
            if parent.exists() and not os.access(parent, os.W_OK):
                raise InstallError(f"Unwritable directory: {parent}")
            parent = parent.parent
    return files


def install(root, files):
    """Stage files and restore old bytes if any replacement fails."""
    stage = Path(tempfile.mkdtemp(prefix=".shadcn-stage-", dir=root))
    old = {}
    written = []
    try:
        for relative, contents in files.items():
            staged = stage / relative
            staged.parent.mkdir(parents=True, exist_ok=True)
            staged.write_bytes(contents)
        for relative in files:
            target = safe_destination(root, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            old[relative] = target.read_bytes() if target.exists() else None
            os.replace(stage / relative, target)
            written.append(relative)
    except Exception:
        for relative in reversed(written):
            target = safe_destination(root, relative)
            if old[relative] is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(old[relative])
        raise
    finally:
        shutil.rmtree(stage)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Copy owned SwiftUI component sources")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    for command in ("init", "add", "dry-run"):
        entry = sub.add_parser(command)
        entry.add_argument("components", nargs="*")
        entry.add_argument("--destination", type=Path, required=True)
        entry.add_argument("--overwrite", action="store_true")
        if command == "dry-run":
            entry.add_argument("--init", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "list":
        for name, data in REGISTRY.items():
            print(f"{name}: {data['description']}")
        return 0
    try:
        initialize = args.command == "init" or (args.command == "dry-run" and args.init)
        if args.command == "add" and not args.components:
            raise InstallError("add requires at least one component")
        files = plan(args.destination, args.components, initialize, args.overwrite)
        for relative in files:
            print(
                f"{'Would write' if args.command == 'dry-run' else 'Write'} {relative}"
            )
        if args.command != "dry-run":
            install(args.destination, files)
    except InstallError as error:
        parser.exit(2, f"error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
