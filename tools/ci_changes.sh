#!/usr/bin/env bash
set -euo pipefail

# Unknown paths and unavailable Git history run the complete suite.
quality=false
cli=false
build=false
unit=false
copy=false
snapshot=false

mark_full() {
    quality=true
    cli=true
    build=true
    unit=true
    copy=true
    snapshot=true
}

mark_path() {
    case "$1" in
        README.md | DESIGN.md | AGENTS.md | CONTRIBUTING.md | LICENSE | NOTICE | docs/*.md) ;;
        Sources/* | Package.swift | flake.nix | flake.lock | justfile | .github/workflows/*)
            mark_full
            ;;
        Tests/*)
            quality=true
            unit=true
            ;;
        Testing/*)
            snapshot=true
            case "$1" in
                *.swift) quality=true ;;
            esac
            ;;
        tools/evoloom.py | tools/registry.json)
            quality=true
            cli=true
            copy=true
            ;;
        tools/test_*.py)
            quality=true
            cli=true
            ;;
        tools/snapshots.json)
            quality=true
            snapshot=true
            ;;
        tools/format_json.py)
            quality=true
            ;;
        .swiftformat | .swiftlint.yml | .yamllint.yml | .github/actionlint.yaml)
            quality=true
            ;;
        *) mark_full ;;
    esac
}

if [[ "${GITHUB_EVENT_NAME:-}" == "push" || "${GITHUB_EVENT_NAME:-}" == "pull_request" ]] &&
    [[ "${CI_BASE_SHA:-}" =~ ^[0-9a-f]{40}$ && "${CI_HEAD_SHA:-}" =~ ^[0-9a-f]{40}$ ]]; then
    changed_paths=$(mktemp)
    trap 'rm -f "$changed_paths"' EXIT

    if [[ "$GITHUB_EVENT_NAME" == "pull_request" ]]; then
        diff_base=$(git merge-base "$CI_BASE_SHA" "$CI_HEAD_SHA" || true)
    else
        diff_base=$CI_BASE_SHA
    fi

    if [[ -n "$diff_base" ]] && git diff --name-only --no-renames -z "$diff_base" "$CI_HEAD_SHA" >"$changed_paths"; then
        while IFS= read -r -d '' path; do
            mark_path "$path"
        done <"$changed_paths"
    else
        mark_full
    fi
else
    mark_full
fi

prepare=false
if [[ "$build" == true || "$unit" == true || "$copy" == true || "$snapshot" == true ]]; then
    prepare=true
fi
run_checks=false
if [[ "$quality" == true || "$cli" == true || "$prepare" == true ]]; then
    run_checks=true
fi

{
    printf 'run_checks=%s\n' "$run_checks"
    printf 'quality=%s\n' "$quality"
    printf 'cli=%s\n' "$cli"
    printf 'prepare=%s\n' "$prepare"
    printf 'build=%s\n' "$build"
    printf 'unit=%s\n' "$unit"
    printf 'copy=%s\n' "$copy"
    printf 'snapshot=%s\n' "$snapshot"
} | tee -a "$GITHUB_OUTPUT"
