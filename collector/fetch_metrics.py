"""
fetch_metrics.py

Extract KPI metrics from GitHub Actions workflow runs.
"""

from github_api import get_workflow_runs


# Only keep workflows that belong to this project
ALLOWED_WORKFLOWS = [
    "CI Pipeline",
    "KPI Dashboard"
]


def extract_metrics():
    """
    Fetch workflow runs from GitHub and extract useful KPI metrics.
    """

    data = get_workflow_runs()

    if not data:
        print("No workflow data found.")
        return []

    workflow_runs = data.get("workflow_runs", [])

    # Filter only project workflows
    workflow_runs = [
        run for run in workflow_runs
        if run.get("name") in ALLOWED_WORKFLOWS
    ]

    metrics = []

    for run in workflow_runs:

        metric = {

            "workflow_name": run.get("name"),

            "run_number": run.get("run_number"),

            "status": run.get("status"),

            "conclusion": run.get("conclusion"),

            "branch": run.get("head_branch"),

            "event": run.get("event"),

            "actor": run.get("actor", {}).get("login"),

            "commit_sha": run.get("head_sha"),

            "created_at": run.get("created_at"),

            "updated_at": run.get("updated_at")
        }

        metrics.append(metric)

    return metrics


def calculate_summary(metrics):
    """
    Calculate KPI summary.
    """

    total_runs = len(metrics)

    successful_runs = sum(
        1 for metric in metrics
        if metric["conclusion"] == "success"
    )

    failed_runs = sum(
        1 for metric in metrics
        if metric["conclusion"] == "failure"
    )

    success_rate = (
        successful_runs / total_runs * 100
        if total_runs > 0 else 0
    )

    return {
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "failed_runs": failed_runs,
        "success_rate": round(success_rate, 2)
    }


def display_metrics(metrics):

    print("\n")
    print("=" * 70)
    print("             GitHub Actions KPI Metrics")
    print("=" * 70)

    for metric in metrics:

        print("\n" + "-" * 70)

        print(f"Workflow     : {metric['workflow_name']}")
        print(f"Run Number   : {metric['run_number']}")
        print(f"Status       : {metric['status']}")
        print(f"Result       : {metric['conclusion']}")
        print(f"Branch       : {metric['branch']}")
        print(f"Event        : {metric['event']}")
        print(f"Triggered By : {metric['actor']}")
        print(f"Commit SHA   : {metric['commit_sha'][:7]}")
        print(f"Created At   : {metric['created_at']}")
        print(f"Updated At   : {metric['updated_at']}")

    print("\n" + "=" * 70)


def display_summary(summary):

    print("\n")
    print("=" * 70)
    print("                 KPI SUMMARY")
    print("=" * 70)

    print(f"Total Workflow Runs : {summary['total_runs']}")
    print(f"Successful Runs     : {summary['successful_runs']}")
    print(f"Failed Runs         : {summary['failed_runs']}")
    print(f"Success Rate        : {summary['success_rate']} %")

    print("=" * 70)


if __name__ == "__main__":

    metrics = extract_metrics()

    display_metrics(metrics)

    summary = calculate_summary(metrics)

    display_summary(summary)