"""
github_api.py

This module connects to the GitHub REST API and fetches
GitHub Actions workflow run data.
"""

import os
import requests

# ==========================================
# GitHub Repository Configuration
# ==========================================

OWNER = "Deepshika-2006"
REPO = "kpi-cicd-dashboard"

BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"

# ==========================================
# GitHub Personal Access Token (Optional)
# ==========================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# ==========================================
# Request Headers
# ==========================================

headers = {
    "Accept": "application/vnd.github+json"
}

if GITHUB_TOKEN:
    headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"


# ==========================================
# Fetch Workflow Runs
# ==========================================

def get_workflow_runs():
    """
    Fetch all GitHub Actions workflow runs.

    Returns:
        dict: Workflow run data if successful
        None: If request fails
    """

    url = f"{BASE_URL}/actions/runs"

    try:
        response = requests.get(url, headers=headers)

        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")

    except requests.exceptions.ConnectionError:
        print("Connection Error")

    except requests.exceptions.Timeout:
        print("Request Timed Out")

    except requests.exceptions.RequestException as err:
        print(f"Request Failed: {err}")

    return None


# ==========================================
# Display Workflow Runs
# ==========================================

def display_workflow_runs(data):
    """
    Display basic workflow information.
    """

    if not data:
        print("No data received.")
        return

    print("\n========== GitHub Actions ==========\n")

    print(f"Total Workflow Runs : {data['total_count']}")

    workflow_runs = data.get("workflow_runs", [])

    if not workflow_runs:
        print("\nNo workflow runs found.")
        return

    print("\nRecent Workflow Runs\n")

    for run in workflow_runs[:5]:

        print("-" * 50)

        print("Workflow :", run.get("name"))

        print("Status   :", run.get("status"))

        print("Result   :", run.get("conclusion"))

        print("Branch   :", run.get("head_branch"))

        print("Event    :", run.get("event"))

        print("Created  :", run.get("created_at"))

        print("Updated  :", run.get("updated_at"))

    print("-" * 50)


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    data = get_workflow_runs()

    display_workflow_runs(data)