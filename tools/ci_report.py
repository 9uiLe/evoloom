"""Write concise Xcode evidence without changing test outcomes."""

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "TestResults"


def test_cases(nodes):
    for node in nodes:
        if node.get("nodeType") == "Test Case":
            yield node
        yield from test_cases(node.get("children", []))


def action_cases(section):
    if section.get("title", "").startswith("Run test case "):
        yield section
    for child in section.get("subsections", []):
        yield from action_cases(child)


def result_summary(path):
    def read(section):
        return json.loads(
            subprocess.check_output(
                [
                    "xcrun",
                    "xcresulttool",
                    "get",
                    "test-results",
                    section,
                    "--path",
                    str(path),
                    "--format",
                    "json",
                ],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=15,
            )
        )

    summary = read("summary")
    cases = list(test_cases(read("tests").get("testNodes", [])))
    action = json.loads(
        subprocess.check_output(
            [
                "xcrun",
                "xcresulttool",
                "get",
                "log",
                "--type",
                "action",
                "--path",
                str(path),
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
    )
    timed_cases = list(action_cases(action))
    first_case = min((case["startTime"] for case in timed_cases), default=None)
    last_case = max(
        (case["startTime"] + case["duration"] for case in timed_cases), default=None
    )
    return {
        "count": summary["totalTestCount"],
        "passed": summary["passedTests"],
        "failed": summary["failedTests"],
        "test_phase_seconds": round(summary["finishTime"] - summary["startTime"], 2),
        "case_seconds": round(
            sum(case.get("durationInSeconds", 0) for case in cases), 2
        ),
        "action_to_first_case_seconds": round(first_case - action["startTime"], 2)
        if first_case
        else None,
        "last_case_to_action_end_seconds": round(
            action["startTime"] + action["duration"] - last_case, 2
        )
        if last_case
        else None,
        "device": read("tests").get("devices", []),
    }


def report():
    baseline_count = len(json.loads((ROOT / "tools/snapshots.json").read_text()))
    metrics = []
    metrics_file = RESULTS / "metrics.jsonl"
    if metrics_file.exists():
        metrics = [json.loads(line) for line in metrics_file.read_text().splitlines()]
    preparation = None
    if (RESULTS / "preparation.json").exists():
        preparation = json.loads((RESULTS / "preparation.json").read_text())
    results = {}
    for name in ("ios", "unit", "snapshot"):
        path = RESULTS / f"{name}.xcresult"
        if path.exists():
            try:
                results[name] = result_summary(path)
            except (
                OSError,
                ValueError,
                subprocess.CalledProcessError,
                subprocess.TimeoutExpired,
            ) as error:
                results[name] = {"error": str(error)}
    document = {
        "checkout": os.environ.get("GITHUB_SHA", "local working tree"),
        "baseline_pngs": baseline_count,
        "preparation": preparation,
        "xcode_actions": metrics,
        "tests": results,
        "xcode_cache": os.environ.get("EVOLOOM_XCODE_CACHE", "disabled"),
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "ci-report.json").write_text(json.dumps(document, indent=2) + "\n")
    lines = [
        "### iOS evidence",
        f"Checkout: `{document['checkout']}`; baseline PNGs: {baseline_count}; Xcode cache: {document['xcode_cache']}",
    ]
    if preparation:
        lines.append(
            f"Nix-fixed source preparation: {'reused' if preparation['reused'] else 'copied'} "
            f"in {preparation['seconds']}s"
        )
    for item in metrics:
        lines.append(
            f"- {item['scheme']} {item['action']}: {item['seconds']}s ({item['result']})"
        )
    for name, result in results.items():
        if "error" in result:
            lines.append(f"- {name} xcresult unreadable: {result['error']}")
            continue
        lines.append(
            f"- {name}: {result['passed']}/{result['count']} passed, "
            f"{result['failed']} failed; xcresult test phase {result['test_phase_seconds']}s, "
            f"first case after {result['action_to_first_case_seconds']}s, "
            f"case sum {result['case_seconds']}s, "
            f"after last case {result['last_case_to_action_end_seconds']}s"
        )
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as file:
            file.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    report()
