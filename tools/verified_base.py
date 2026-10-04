"""Find a successful full validation ancestor for cumulative push diffs."""

import json
import os
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def api(path):
    request = Request(
        f"{os.environ.get('GITHUB_API_URL', 'https://api.github.com')}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(request, timeout=10) as response:
        return json.load(response)


def is_full_validation(jobs):
    for job in jobs:
        if job.get("conclusion") != "success":
            continue
        if job.get("name") == "validation" and any(
            step.get("name") == "Mark full validation"
            and step.get("conclusion") == "success"
            for step in job.get("steps", [])
        ):
            return True
        if job.get("name") == "ios":
            successful = {
                step["name"]
                for step in job.get("steps", [])
                if step.get("conclusion") == "success"
            }
            if {
                "Run Package unit tests",
                "Verify copied source Package",
                "Compare iOS snapshots",
            } <= successful:
                return True
    return False


def verified_base(repo, head, current_run):
    runs = api(
        f"/repos/{repo}/actions/workflows/ci.yml/runs"
        "?branch=master&status=success&per_page=100"
    )["workflow_runs"]
    for run in runs:
        candidate = run.get("head_sha", "")
        if str(run.get("id")) == current_run or len(candidate) != 40:
            continue
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", candidate, head], check=False
        ).returncode:
            continue
        jobs = api(f"/repos/{repo}/actions/runs/{run['id']}/jobs?per_page=100")["jobs"]
        if is_full_validation(jobs):
            return candidate, run["html_url"]
    return "", ""


def main():
    base = ""
    url = ""
    if os.environ.get("GITHUB_EVENT_NAME") == "push":
        try:
            base, url = verified_base(
                os.environ["GITHUB_REPOSITORY"],
                os.environ["GITHUB_SHA"],
                os.environ["GITHUB_RUN_ID"],
            )
        except (HTTPError, URLError, KeyError, ValueError) as error:
            print(
                f"Verified base unavailable; full validation required: {error}",
                file=sys.stderr,
            )
    output = f"verified_base={base}\nverified_run={url}\n"
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as file:
        file.write(output)
    print(f"Verified full-validation ancestor: {base or 'none; use full suite'}")


if __name__ == "__main__":
    main()
