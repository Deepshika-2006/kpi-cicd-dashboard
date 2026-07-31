"""
fetch_metrics.py

Extract KPI metrics from GitHub Actions workflow runs.
"""

from datetime import datetime
from collector.github_api import get_workflow_runs

ALLOWED_WORKFLOWS = [
    "CI Pipeline",
    # ".github/workflows/ci.yml"
]


def calculate_duration(created_at, updated_at):
    """
    Calculate workflow duration in seconds.
    """

    if not created_at or not updated_at:
        return None

    try:
        start = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        end = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")

        return int((end - start).total_seconds())

    except ValueError:
        return None


def extract_metrics():
    """
    Fetch workflow runs from GitHub and
    return KPI metrics.
    """

    data = get_workflow_runs()

    if not data:
        return []

    workflow_runs = data.get("workflow_runs", [])

    workflow_runs = [
    run for run in workflow_runs
    if run.get("name") == "CI Pipeline"
    or (
        run.get("name") == ".github/workflows/ci.yml"
        and run.get("conclusion") == "failure"
    )
]

    metrics = []

    for run in workflow_runs:

        created = run.get("created_at")
        updated = run.get("updated_at")

        metric = {

            "run_id": run.get("id"),
            "workflow_name": run.get("name"),
            "run_number": run.get("run_number"),
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "branch": run.get("head_branch"),
            "event": run.get("event"),
            "actor": run.get("actor", {}).get("login"),
            "commit_sha": run.get("head_sha"),
            "created_at": created,
            "updated_at": updated,
            "duration": calculate_duration(created, updated)

        }

        metrics.append(metric)

    return metrics
