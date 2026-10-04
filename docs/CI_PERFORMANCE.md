# CI throughput and measurement

## Current validation path

The root Package is a dependency-free library. `Testing/` is the development
Package with one XCTest target for six unit methods and eight image methods.
Those eight methods compare 18 committed PNGs. A full CI run starts a Linux
static job and an ARM64 macOS iOS job after a lightweight change detector. The
iOS job runs one combined XCTest session and builds all copied source as a
separate iOS library Package. It does not start a copy test runner. A required
`validation` job rejects any failed or canceled selected job. Manual
`workflow_dispatch` always selects the full suite.

For daily local feedback, run `nix develop -c just check-fast`. Before a
change is complete, run `nix develop -c just prepare-deps check` (or
`check-full`). `just build-package`, `test-unit`, `test-snapshot`, and
`verify-copy-install` remain separate diagnostic commands. Only
`record-snapshots` may replace reference PNGs.

## Evidence and comparison

Step durations below come from GitHub Jobs API timestamps. Wall time includes
queueing; runner usage sums job start-to-completion intervals. The comparison
uses one successful full run of each configuration on the same fixed Apple
host class. It is evidence for these runs, not a stable percentile.

| Run | First static/CLI feedback after creation | Complete after creation | Aggregate runner time | Mac runner time | Queue or pending before first job |
| --- | ---: | ---: | ---: | ---: | ---: |
| [Before, 3de4628](https://github.com/9uiLe/evoloom/actions/runs/37180096395) | 183 s, within the sole iOS job | 1063 s | 1053 s | 1053 s | 9 s |
| [Combined tests, ac713ec](https://github.com/9uiLe/evoloom/actions/runs/37182970001) | 366 s observed; 59 s after jobs were created | 732 s observed; 425 s after jobs were created | 460 s | 400 s | 307 s before the detector job was created, following a canceled run |

The second run's long pending interval is not job execution time. Its Linux
detector took 8 seconds and its static job 47 seconds. The macOS job took 400
seconds: Nix installation 61, environment check 48, combined iOS tests 227,
copied Package build 36, with the remainder in setup, evidence and cleanup.
The former macOS job took 1053 seconds; its separate unit, copy and image
steps took 360, 248 and 201 seconds respectively. The iOS runner saving in
this observation comes mainly from fewer XCTest sessions and replacing the
copy's one runtime assertion with an all-source compile. The former spacing
assertion remains in the unit target. CPU and cloud scheduling vary; two more
similar runs are needed before estimating typical improvement or variance.

The [new run's xcresult](https://github.com/9uiLe/evoloom/actions/runs/37182970001)
reports 14 passing methods, 0 failed, an iPhone 18 Pro on iOS 27.0 build
24A434, and 18 unchanged baselines. `ci-report.json` in `ios-test-evidence`
records the checkout SHA, action wall time, dependency preparation and test
counts. The combined Xcode action took 218.47 seconds inside its 227-second
workflow step. Its xcresult test phase lasted 199.12 seconds, while case
durations summed to 5.05 seconds. The first case began 193.84 seconds after
the action log started. This is observed wait across Simulator and test runner
setup; it cannot all be assigned to boot, testmanagerd or a debugger. A
diagnostic local cold `build-for-testing -showBuildTimingSummary` took about
24 seconds of wall time and reported 23 `SwiftCompile` tasks totaling 44.25
task-seconds across parallel work. It compiled Evoloom and SnapshotTesting,
with no SwiftSyntax or AppMacros target. The total task-seconds are not wall
time.

## Experiments and cache boundary

Apple's `build-for-testing` generated an `.xctestrun` for this Swift Package,
and `test-without-building` then passed all 14 methods. On a warm local host
the two commands took 14.29 and 15.22 seconds, compared with about 27 seconds
for one `test` action. Splitting is available for diagnostics but is not the
default because it added an invocation without observed speedup.

The optional manual `use_xcode_cache` input trials a cache of
`DerivedData/Visual/Build` and the Nix-prepared SnapshotTesting source. Its key
includes macOS build, architecture, Xcode, SDK, Simulator runtime, Debug
settings, `flake.lock`, both Package manifests and preparation code. A source
change gets a new commit key while restoring the latest compatible earlier
cache; Xcode still rebuilds changed inputs and all tests still execute.
Prepared source hashes must match the locked Nix source or preparation
regenerates it. A missing cache never skips a test. On the local host, 513 MB
of Visual `Build` data plus prepared source compressed to 97 MB with the
Nix-fixed zstd package at level 3 in about 5 seconds. This excludes cloud
transfer and unpack time, so it is not a speedup claim. Keep the cache in
normal CI only if miss, exact hit and source-change runs show a net improvement
including restore and save time. GitHub's [cache matching and branch scope](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
apply; eviction or a lock change causes a safe miss.

The workflow-level concurrency group cancels older push or PR runs on the same
ref, while manual full runs use their own run ID. Push selection is cumulative
from a successful full-validation ancestor; an unavailable GitHub API or
unavailable history selects full. The local tests cover a code push followed
by documentation, PR merge-base, deletion, rename, unknown paths, lock changes
and unrelated ancestry. This guards the canceled-code / documentation-only
case. [GitHub's concurrency semantics](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
allow a canceled run to take time to clean up; record that time as queueing for
the next run, not as its runner execution.
