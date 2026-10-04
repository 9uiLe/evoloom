#!/usr/bin/env bash
set -euo pipefail

# Unknown paths and unavailable Git history run the complete suite.
quality=false
cli=false
unit=false
copy=false
snapshot=false

mark_full() {
    quality=true
    cli=true
    unit=true
    copy=true
    snapshot=true
}

mark_path() {
    case "$1" in
        README.md | DESIGN.md | AGENTS.md | CONTRIBUTING.md | LICENSE | NOTICE | docs/*.md | .github/pull_request_template.md) ;;
        Sources/* | Package.swift | flake.nix | flake.lock | justfile | .github/workflows/*)
            mark_full
            ;;
        Testing/Package.swift)
            mark_full
            ;;
        Tests/* | Testing/Tests/EvoloomSnapshotTests/DesignTokensTests.swift | Testing/Tests/EvoloomSnapshotTests/InteractionTests.swift)
            quality=true
            unit=true
            ;;
        Testing/Tests/EvoloomSnapshotTests/ComponentSnapshots.swift)
            quality=true
            snapshot=true
            ;;
        Testing/Tests/EvoloomSnapshotTests/*.swift)
            quality=true
            unit=true
            snapshot=true
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
        tools/pr_images.py)
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

diff_base=""
if [[ "${GITHUB_EVENT_NAME:-}" == "pull_request" ]] &&
    [[ "${CI_BASE_SHA:-}" =~ ^[0-9a-f]{40}$ && "${CI_HEAD_SHA:-}" =~ ^[0-9a-f]{40}$ ]]; then
    diff_base=$(git merge-base "$CI_BASE_SHA" "$CI_HEAD_SHA" || true)
elif [[ "${GITHUB_EVENT_NAME:-}" == "push" ]] &&
    [[ "${CI_VERIFIED_BASE_SHA:-}" =~ ^[0-9a-f]{40}$ && "${CI_HEAD_SHA:-}" =~ ^[0-9a-f]{40}$ ]] &&
    git merge-base --is-ancestor "$CI_VERIFIED_BASE_SHA" "$CI_HEAD_SHA"; then
    diff_base=$CI_VERIFIED_BASE_SHA
fi

if [[ -n "$diff_base" ]]; then
    changed_paths=$(mktemp)
    trap 'rm -f "$changed_paths"' EXIT
    if git diff --name-only --no-renames -z "$diff_base" "$CI_HEAD_SHA" >"$changed_paths"; then
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
if [[ "$unit" == true || "$snapshot" == true ]]; then
    prepare=true
fi
ios=false
if [[ "$unit" == true || "$copy" == true || "$snapshot" == true ]]; then
    ios=true
fi
run_checks=false
if [[ "$quality" == true || "$cli" == true || "$ios" == true ]]; then
    run_checks=true
fi
full=false
if [[ "$quality" == true && "$cli" == true && "$unit" == true && "$copy" == true && "$snapshot" == true ]]; then
    full=true
fi

{
    printf 'base_used=%s\n' "$diff_base"
    printf 'run_checks=%s\n' "$run_checks"
    printf 'quality=%s\n' "$quality"
    printf 'cli=%s\n' "$cli"
    printf 'prepare=%s\n' "$prepare"
    printf 'ios=%s\n' "$ios"
    printf 'unit=%s\n' "$unit"
    printf 'copy=%s\n' "$copy"
    printf 'snapshot=%s\n' "$snapshot"
    printf 'full=%s\n' "$full"
} | tee -a "$GITHUB_OUTPUT"
