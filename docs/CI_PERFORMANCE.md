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
uses one old, two uncached combined-configuration and one cache miss/hit pair
on the same fixed Apple host class. It is evidence for these runs, not a
stable percentile.

| Run | First static/CLI feedback after creation | Complete after creation | Aggregate runner time | Mac runner time | Queue or pending before first job |
| --- | ---: | ---: | ---: | ---: | ---: |
| [Before, 3de4628](https://github.com/9uiLe/evoloom/actions/runs/37180096395) | 183 s, within the sole iOS job | 1063 s | 1053 s | 1053 s | 9 s |
| [Combined tests, ac713ec](https://github.com/9uiLe/evoloom/actions/runs/37182970001) | 366 s observed; 59 s after jobs were created | 732 s observed; 425 s after jobs were created | 460 s | 400 s | 307 s before the detector job was created, following a canceled run |
| [Combined tests, b08f4da](https://github.com/9uiLe/evoloom/actions/runs/37183857742) | 51 s | 489 s | 518 s | 468 s | 2 s to start the detector; 15 s to start iOS |
| [Cache miss, b08f4da](https://github.com/9uiLe/evoloom/actions/runs/37184286785) | 56 s | 416 s | 445 s | 394 s | 5 s to start the detector |
| [Exact cache hit, b08f4da](https://github.com/9uiLe/evoloom/actions/runs/37184653047) | 53 s | 620 s | 643 s | 592 s | 4 s to start the detector |

The ac713ec run's long pending interval is not job execution time. Its Linux
detector took 8 seconds and its static job 47 seconds. The macOS job took 400
seconds: Nix installation 61, environment check 48, combined iOS tests 227,
copied Package build 36, with the remainder in setup, evidence and cleanup.
The former macOS job took 1053 seconds; its separate unit, copy and image
steps took 360, 248 and 201 seconds respectively. The iOS runner saving in
this observation comes mainly from fewer XCTest sessions and replacing the
copy's one runtime assertion with an all-source compile. The former spacing
assertion remains in the unit target. The b08f4da run took 304 seconds for
combined tests and 33 for the copied Package build. Its xcresult reports 14
passing methods, 18 baselines, 163.33 seconds from action start to first case
and 60.93 seconds summed across cases. The ac713ec run reported 193.84 and
5.05 seconds respectively; the representative-screen case alone took 30.07
seconds in b08f4da. CPU and cloud scheduling vary. The two combined
runs have macOS runner durations of 400 and 468 seconds (median 434, range
68); their total runner usage is 460 and 518 seconds (median 489, range 58).
The sole old-configuration run used 1053 runner seconds. This sample is too
small for a stable percentile or a typical speedup estimate.

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

The fixed iPhone 18 Pro was `Shutdown` after a test that began `Shutdown`,
while a test that began `Booted` left it `Booted`. On the local warm build,
one test from `Shutdown` took 49.57 seconds. An explicit `simctl boot`
request took 0.51 seconds, followed immediately by a 28.18-second test.
The run order and host warmup can affect this one-pair comparison. CI now
requests boot after dependency preparation and before `xcodebuild test`, so
the Simulator can continue starting while Xcode builds. The request and
starting state are recorded in `metrics.jsonl`; a Cloud run is needed to
evaluate end-to-end benefit and confirm its final state.

## Experiments and cache boundary

Apple's [build-for-testing and test-without-building commands](https://developer.apple.com/library/archive/technotes/tn2339/_index.html)
generated an `.xctestrun` for this Swift Package,
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

The same-SHA Cloud trial saved a 4.48 MB archive in about 2 seconds; its next
run restored it in about 2 seconds. Nix-prepared source verification reported
`reused: true` on the hit, versus `false` on the miss. The Xcode test steps
lasted 242 and 378 seconds, and the whole runs 416 and 620 seconds. The
hit's first-case wait was 217.91 seconds versus 151.18 on the miss; case
durations summed to 88.33 versus 41.86 seconds. This is one miss/hit pair,
so the longer hit is not proof that the cache itself caused the delay, but
there is no observed end-to-end gain. Normal push CI therefore leaves this
cache disabled. The 4.48 MB Cloud archive and 97 MB local compression trial
had different host/build footprints; neither predicts another host's transfer
cost. A source-change trial is still needed before deciding whether to retain
the manual cache option for diagnostics.

The workflow-level concurrency group cancels older push or PR runs on the same
ref, while manual full runs use their own run ID. Push selection is cumulative
from a successful full-validation ancestor; an unavailable GitHub API or
unavailable history selects full. The local tests cover a code push followed
by documentation, PR merge-base, deletion, rename, unknown paths, lock changes
and unrelated ancestry. This guards the canceled-code / documentation-only
case. [GitHub's concurrency semantics](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
allow a canceled run to take time to clean up; record that time as queueing for
the next run, not as its runner execution.
