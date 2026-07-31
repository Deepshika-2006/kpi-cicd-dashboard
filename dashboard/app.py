import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

from collector.store_metrics import sync_database

# ------------------------------------------------
# Database Path
# ------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "metrics.db"


def load_data():

    conn = sqlite3.connect(str(DB_PATH))

    query = """
    SELECT
        workflow_name,
        run_number,
        status,
        conclusion,
        branch,
        event,
        actor,
        commit_sha,
        created_at,
        updated_at,
        duration
    FROM workflow_metrics
    ORDER BY created_at DESC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# ------------------------------------------------
# Streamlit Page Config
# ------------------------------------------------

st.set_page_config(
    page_title="KPI-Driven CI/CD Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 KPI-Driven CI/CD Dashboard")

st.markdown("---")

# ------------------------------------------------
# Refresh Button
# ------------------------------------------------

if st.button("🔄 Refresh & Sync"):

    inserted = sync_database()

    st.cache_data.clear()

    st.success(f"{inserted} new workflow(s) added.")

    st.rerun()

# ------------------------------------------------
# Load Data
# ------------------------------------------------

df = load_data()

if df.empty:
    st.warning("No workflow data found.")
    st.stop()

# ------------------------------------------------
# Sidebar Filters
# ------------------------------------------------

st.sidebar.header("Filters")

workflow = st.sidebar.multiselect(
    "Workflow",
    options=sorted(df["workflow_name"].unique()),
    default=sorted(df["workflow_name"].unique())
)

branch = st.sidebar.multiselect(
    "Branch",
    options=sorted(df["branch"].unique()),
    default=sorted(df["branch"].unique())
)

df = df[
    (df["workflow_name"].isin(workflow))
    &
    (df["branch"].isin(branch))
]

# ------------------------------------------------
# KPI Calculations
# ------------------------------------------------

completed = df[df["status"] == "completed"]

total_runs = len(df)

completed_runs = len(completed)

successful_runs = len(
    completed[completed["conclusion"] == "success"]
)

failed_runs = len(
    completed[completed["conclusion"] == "failure"]
)

running_runs = len(
    df[df["status"] != "completed"]
)

success_rate = (
    successful_runs / completed_runs * 100
    if completed_runs > 0
    else 0
)

# Only successful builds for timing metrics
successful = completed[
    completed["conclusion"] == "success"
]

valid_duration = successful["duration"].dropna()

average_build = (
    round(valid_duration.mean(), 2)
    if not valid_duration.empty
    else 0
)

fastest_build = (
    valid_duration.min()
    if not valid_duration.empty
    else 0
)

slowest_build = (
    valid_duration.max()
    if not valid_duration.empty
    else 0
)

# ------------------------------------------------
# KPI Cards
# ------------------------------------------------

row1 = st.columns(6)

row1[0].metric("📊 Total Runs", total_runs)
row1[1].metric("✔ Completed Runs", completed_runs)
row1[2].metric("✅ Successful Runs", successful_runs)
row1[3].metric("❌ Failed Runs", failed_runs)
row1[4].metric("🟡 Running Runs", running_runs)
row1[5].metric("📈 Success Rate", f"{success_rate:.2f}%")

st.markdown("")

row2 = st.columns(3)

row2[0].metric(
    "⏱ Avg Build Time",
    f"{average_build:.2f} sec"
)

row2[1].metric(
    "🚀 Fastest Build",
    f"{fastest_build} sec"
)

row2[2].metric(
    "🐢 Slowest Build",
    f"{slowest_build} sec"
)

st.markdown("---")

# ------------------------------------------------
# Charts
# ------------------------------------------------

left, right = st.columns(2)

with left:

    pie_df = pd.DataFrame({
        "Result": ["Success", "Failure"],
        "Count": [successful_runs, failed_runs]
    })

    pie = px.pie(
        pie_df,
        names="Result",
        values="Count",
        hole=0.55,
        title="Workflow Result Distribution"
    )

    st.plotly_chart(
        pie,
        use_container_width=True
    )

with right:

    workflow_df = (
        df.groupby("workflow_name")
        .size()
        .reset_index(name="Runs")
    )

    bar = px.bar(
        workflow_df,
        x="workflow_name",
        y="Runs",
        text="Runs",
        title="Workflow Runs"
    )

    st.plotly_chart(
        bar,
        use_container_width=True
    )

# ------------------------------------------------
# Build Duration Chart
# ------------------------------------------------

st.markdown("---")

completed_chart = successful.copy()

completed_chart["Run"] = completed_chart["run_number"].astype(str)

duration_chart = px.line(
    completed_chart,
    x="Run",
    y="duration",
    markers=True,
    title="Build Duration per Successful Run",
    labels={
        "duration": "Seconds",
        "Run": "Run Number"
    }
)

st.plotly_chart(
    duration_chart,
    use_container_width=True
)

# ------------------------------------------------
# Workflow History
# ------------------------------------------------

display_df = df.copy()

display_df["commit_sha"] = display_df["commit_sha"].str[:7]

display_df = display_df.rename(
    columns={
        "workflow_name": "Workflow",
        "run_number": "Run",
        "status": "Status",
        "conclusion": "Result",
        "branch": "Branch",
        "event": "Event",
        "actor": "Actor",
        "commit_sha": "Commit",
        "duration": "Duration (sec)",
        "created_at": "Created",
        "updated_at": "Updated"
    }
)

st.markdown("---")

st.subheader("📋 Workflow History")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)