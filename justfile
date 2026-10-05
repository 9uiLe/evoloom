set shell := ["/bin/bash", "-eu", "-c"]

doctor:
    python3 tools/tasks.py doctor

prepare-simulator:
    python3 tools/tasks.py prepare-simulator

prepare-deps:
    python3 tools/prepare_deps.py

format:
    swiftformat Package.swift Sources Testing --config .swiftformat
    ruff format tools
    nixfmt flake.nix nix/sim-use.nix
    shfmt -i 4 -ci -w tools/ci_changes.sh
    python3 tools/format_json.py
    just --fmt

format-check:
    swiftformat Package.swift Sources Testing --config .swiftformat --lint
    ruff format --check tools
    nixfmt --check flake.nix nix/sim-use.nix
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

prepare-host:
    python3 tools/tasks.py prepare-host

build-host:
    python3 tools/tasks.py build-host

run-host screen="collection" state="normal" appearance="light":
    EVOLOOM_SCREEN="{{ screen }}" EVOLOOM_STATE="{{ state }}" EVOLOOM_APPEARANCE="{{ appearance }}" python3 tools/tasks.py run-host

verify-settings-interaction:
    python3 tools/sim_use_review.py

verify-detail-interaction:
    python3 tools/sim_use_detail_button.py --scenario detail

verify-button-transition:
    python3 tools/sim_use_detail_button.py --scenario button

test-unit:
    python3 tools/tasks.py test-unit

test-ios:
    python3 tools/tasks.py test-ios

test-snapshot:
    python3 tools/tasks.py test-snapshot

record-snapshots:
    python3 tools/tasks.py record-snapshots

verify-copy-install:
    python3 tools/tasks.py verify-copy-install

check-fast: format-check lint
    python3 -m unittest discover -s tools -p 'test_*.py'

check: doctor check-fast
    just test-ios
    just verify-copy-install

check-full: check
