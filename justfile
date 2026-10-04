set shell := ["/bin/bash", "-eu", "-c"]

doctor:
    python3 tools/tasks.py doctor

prepare-deps:
    python3 tools/prepare_deps.py

format:
    swiftformat Package.swift Sources Tests Testing --config .swiftformat
    ruff format tools
    nixfmt flake.nix
    shfmt -i 4 -ci -w tools/ci_changes.sh
    python3 tools/format_json.py
    just --fmt

format-check:
    swiftformat Package.swift Sources Tests Testing --config .swiftformat --lint
    ruff format --check tools
    nixfmt --check flake.nix
    shfmt -i 4 -ci -d tools/ci_changes.sh
    python3 tools/format_json.py --check
    just --fmt --check

lint:
    swiftlint lint --strict --config .swiftlint.yml
    ruff check tools
    yamllint -c .yamllint.yml .swiftlint.yml .yamllint.yml .github/actionlint.yaml
    actionlint .github/workflows/ci.yml
    shellcheck tools/ci_changes.sh

build-package:
    python3 tools/tasks.py build-package

test-unit:
    python3 tools/tasks.py test-unit

test-snapshot:
    python3 tools/tasks.py test-snapshot

record-snapshots:
    python3 tools/tasks.py record-snapshots

verify-copy-install:
    python3 tools/tasks.py verify-copy-install

check: doctor format-check lint
    python3 -m unittest discover -s tools -p 'test_*.py'
    just build-package
    just test-unit
    just verify-copy-install
    just test-snapshot
