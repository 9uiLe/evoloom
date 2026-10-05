# CI throughput and measurement

## Current validation path

The root Package is a dependency-free library. `Testing/` contains one
development XCTest target with six unit methods and ten fixed-image methods.
Those ten methods compare 33 PNGs; the app-host target adds five collection
methods and five PNGs. The current manifest therefore lists 38 images, while
the two XCTest sessions execute 21 methods in total. These are separate counts:
one method can compare several images. The app-host capture exits before its
five exact RGBA comparisons run in `tools/compare_host_images.py`.

A full CI run starts a Linux static job and an ARM64 macOS iOS job after a
lightweight change detector. The iOS job runs the Package and app-host XCTest
sessions serially on the same fixed Simulator, then builds all copied source
as a separate iOS library Package. It does not start a copy test runner. A
required `validation` job rejects any failed or canceled selected job. Manual
`workflow_dispatch` always selects the full suite and can additionally run
Settings, Detail or Button sim-use operation checks with the already built
host. Normal PR CI does not run those interaction scenarios.

For daily local feedback, run `nix develop -c just check-fast`. Before a
change is complete, run `nix develop -c just prepare-deps check` (or
`check-full`). `just build-package`, `test-unit`, `test-snapshot`, and
`verify-copy-install` remain separate diagnostic commands. Only
`record-snapshots` may replace reference PNGs.

## Evidence and comparison

The [2026-10-05 PR run of the 38-image path](https://github.com/9uiLe/evoloom/actions/runs/37257495357)
finished in 8m27s from creation to completion. Its Linux static job took
49s, iOS job 8m05s, and the four job durations summed to 9m05s of runner
time. `ci-report.json` records 16 passing Package methods, five passing app
host methods, 38/38 actual PNGs and five exact hosted RGBA matches. Its PR
head was `33345ad6147b13ff4c0d25058588b2f9c6f05821`; Actions tested
synthetic merge checkout `295365df51a7d1b021fdc8c6cb61b8f4eaea314b`.
This is one observation under the current case count, not a stable throughput
estimate. The earlier table below retains its original commits and matrices.

The measurements below are historical runs of earlier test matrices and
host arrangements; they are not measurements of the current 38-image path.
Step durations come from GitHub Jobs API timestamps. Wall time includes
queueing; runner usage sums job start-to-completion intervals. The comparison
uses one old, four uncached combined-configuration, one cache miss/hit pair,
one source-change cache trial, and two Simulator preboot trials on the same
fixed Apple host class. It is evidence for these runs, not a stable percentile.

| Run | First static/CLI feedback after creation | Complete after creation | Aggregate runner time | Mac runner time | Queue or pending before first job |
| --- | ---: | ---: | ---: | ---: | ---: |
| [Before, 3de4628](https://github.com/9uiLe/evoloom/actions/runs/37180096395) | 183 s, within the sole iOS job | 1063 s | 1053 s | 1053 s | 9 s |
| [Combined tests, ac713ec](https://github.com/9uiLe/evoloom/actions/runs/37182970001) | 366 s observed; 59 s after jobs were created | 732 s observed; 425 s after jobs were created | 460 s | 400 s | 307 s before the detector job was created, following a canceled run |
| [Combined tests, b08f4da](https://github.com/9uiLe/evoloom/actions/runs/37183857742) | 51 s | 489 s | 518 s | 468 s | 2 s to start the detector; 15 s to start iOS |
| [Cache miss, b08f4da](https://github.com/9uiLe/evoloom/actions/runs/37184286785) | 56 s | 416 s | 445 s | 394 s | 5 s to start the detector |
| [Exact cache hit, b08f4da](https://github.com/9uiLe/evoloom/actions/runs/37184653047) | 53 s | 620 s | 643 s | 592 s | 4 s to start the detector |
| [Cumulative code plus docs, 33c616a](https://github.com/9uiLe/evoloom/actions/runs/37185289540) | 159 s, including canceled-run wait | 724 s | 659 s | 604 s | 103 s before the detector started |
| [Boot and test in one shell, e05b3a4](https://github.com/9uiLe/evoloom/actions/runs/37186022746) | 50 s | 726 s | 753 s | 704 s | 2 s to start the detector |
| [Uncached path, b3bb469](https://github.com/9uiLe/evoloom/actions/runs/37186769382) | 54 s | 639 s | 668 s | 616 s | 2 s to start the detector |
| [Uncached after diagnostic fix, d2deee6](https://github.com/9uiLe/evoloom/actions/runs/37187648221) | 51 s | 621 s | 643 s | 594 s | 4 s to start the detector |
| [Source-change cache restore, d2deee6](https://github.com/9uiLe/evoloom/actions/runs/37188223954) | 57 s | 528 s | 557 s | 503 s | 4 s to start the detector |

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
seconds in b08f4da. CPU and cloud scheduling vary. The four uncached
combined runs have macOS runner durations of 400, 468, 594 and 616 seconds
(median 531, range 216); their total runner usage is 460, 518, 643 and 668
seconds (median 580.5, range 208).
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
The run order and host warmup can affect this one-pair comparison. The
optional `nix develop -c just prepare-simulator` command records the fixed
device's starting state and boot request time in `metrics.jsonl`.

The first Cloud preboot run, [33c616a](https://github.com/9uiLe/evoloom/actions/runs/37185289540),
recorded `Shutdown` and a 5.51-second boot request. The Xcode action itself
took 151.91 seconds, with 118.08 seconds to the first case and 9.59 seconds
across cases. Yet its workflow test step took 378 seconds: the log has about
220 seconds between step start and the first `just test-ios` output. The
separate `nix develop` invocation for the boot step had already completed.
Concurrent Simulator startup may have contributed, but the log does not prove
the cause of this delay. The [one-shell trial](https://github.com/9uiLe/evoloom/actions/runs/37186022746)
started `just` in about 2 seconds but then took about 246 seconds between the
boot request and the Xcode command, during the second environment check. Its
Xcode action took 230.05 seconds and the whole test step 493 seconds. These
two Cloud trials show no overall gain from prebooting; normal CI and local
`check` therefore leave Simulator startup to Xcode. The optional command
remains available for diagnosis. The measured delay cannot be assigned to a
specific Simulator service without lower-level tracing.

The subsequent [normal run without preboot](https://github.com/9uiLe/evoloom/actions/runs/37186769382)
passed 14 tests and all 18 baselines. Its 402-second workflow test step
contained a 396.75-second Xcode action, with 250.96 seconds from action start
to first case and 83.59 seconds summed across cases. The earlier 220-to-246
second gap outside the Xcode action did not recur. The remaining variation
is inside Xcode's build and test action; the available timestamps do not
isolate simulator boot, testmanagerd, debugger and compilation costs further.

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
cost. The manual cache remains useful for diagnosis; normal CI leaves it off
because the trials do not show a consistent net benefit.

The first [source-change diagnostic attempt](https://github.com/9uiLe/evoloom/actions/runs/37187328202)
restored the compatible cache and reused the verified Nix-prepared source,
then failed before starting a test. The optional non-quiet build flag was
inserted between `-scheme` and its value, and Xcode rejected the command.
The aggregate validation failed, with zero executed tests. The command builder
now positions test flags relative to `-scheme` and has a test for quiet and
diagnostic modes. A real local diagnostic-mode unit run then passed six tests.

The [successful rerun after a small Card source change](https://github.com/9uiLe/evoloom/actions/runs/37188223954)
restored the compatible earlier cache in about 1 second and saved the new
commit key in about 1 second. Nix preparation reused its verified source.
Xcode's diagnostic log shows `SwiftCompile` for `IOSCard.swift` and other
Evoloom files; the copied Package also compiled `IOSCard.swift` and recorded
one `Ld` task. All 14 test methods and 18 PNGs passed. This run took 528
seconds overall versus 621 seconds for the uncached run on the same SHA, but
it also enabled verbose build diagnostics and is one observation. Together
with the slower exact-hit trial, it is insufficient evidence to enable the
build cache for normal pushes.

The workflow-level concurrency group cancels older push or PR runs on the same
ref, while manual full runs use their own run ID. Push selection is cumulative
from a successful full-validation ancestor; an unavailable GitHub API or
unavailable history selects full. The local tests cover a code push followed
by documentation, PR merge-base, deletion, rename, unknown paths, lock changes
and unrelated ancestry. This guards the canceled-code / documentation-only
case. [GitHub's concurrency semantics](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
allow a canceled run to take time to clean up; record that time as queueing for
the next run, not as its runner execution.

The initial [refactor run](https://github.com/9uiLe/evoloom/actions/runs/37182851785)
failed static validation because the formatter still named a removed `Tests/`
directory; a clean checkout exposed it. The next commit corrected that path.
The [deliberately superseded code run](https://github.com/9uiLe/evoloom/actions/runs/37185270482)
ended canceled and its aggregate validation failed. The following
[documentation-only push](https://github.com/9uiLe/evoloom/actions/runs/37185289540)
selected full checks from the earlier validated SHA and passed them. Its
detector began 103 seconds after creation while the canceled run cleaned up.
These were a fixed implementation error and an expected cancellation, not
automatic retries accepted as success.

## Scene-backed review host (local trial, 2026-10-04)

The collection's native search and toolbar need an app scene for a trustworthy
image. Five collection cases moved to a small development app test target;
the other 23 fixed-size images and six unit tests remain in the development
Package. A one-session alternative was compiled and run, but its app context
changed seven old fixed-size cases, including settings, detail and the narrow
collection layout. Preserving those baselines was preferred to an unrelated
mass re-record. Both sessions run serially on the same pinned simulator;
neither duplicates a collection case. The first warm local passing `test-ios`
measured 26.902 seconds for the Package session and 20.668 seconds for the
app-host session (47.570 seconds of Xcode actions); 15 and 5 XCTest methods
passed, with 28 actual PNGs. This single warm local sample excludes shell and
Nix setup and does not predict GitHub-hosted duration or a cold build. The
trial cache now includes both derived build directories and remains manual
opt-in; normal CI has no explicit Xcode build cache. A post-change CI run and
transfer-inclusive comparison are still needed before any speed claim.

## Hosted mismatch exit (local trial, 2026-10-04)

A one-case in-XCTest mismatch saved the diff 42.1 seconds after starting
xcodebuild, then remained running for another 60 seconds; it was terminated
after diagnostic sampling. With hosted capture and post-process RGBA
comparison, a targeted changed-copy run took 19.5 seconds through fixture
change, host preparation and hosted xcodebuild exit, then detected the
mismatch about 0.25 seconds later. A full warm
`test-snapshot` run with one altered hosted case returned nonzero in 47.5
seconds, with all 28 actuals and the three diff PNGs. The next normal run
passed. These trials differ in code, warm build state and scope; they establish
an ordinary mismatch exit, not a stable speedup. The Xcode action timeout
remains 600 seconds as an abnormal-stop limit, with only its launched process
group terminated and available logs and images retained.

The first Cloud normal run of this change
([37209628472](https://github.com/9uiLe/evoloom/actions/runs/37209628472))
took 11m22s from creation to completion. Its combined iOS test step took
8m10s; the hosted RGBA comparison took 0.577s of that step. The previous
[successful run](https://github.com/9uiLe/evoloom/actions/runs/37204472776)
took 8m48s overall and 5m47s for the combined step. The observed increases
were 2m34s and 2m23s respectively, while Package and host Xcode actions
together increased about 2m14s. This is one run per configuration under
different commits and cloud conditions; it does not establish that the
external comparator caused the increase. The deliberate [failure run](https://github.com/9uiLe/evoloom/actions/runs/37209665511)
took 5m40s for its combined step, including two successful Xcode actions and
a 1.926s failing comparison. It uploaded the diff artifact and failed the
required validation job. No new test session or simulator launch was added.
