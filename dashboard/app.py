import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

DB_PATH = "database/metrics.db"


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)

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
        updated_at
    FROM workflow_metrics
    ORDER BY id DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


st.set_page_config(
    page_title="CI/CD KPI Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 KPI-Driven CI/CD Dashboard")
st.markdown("---")

df = load_data()

if df.empty:
    st.warning("No workflow data found.")
    st.stop()

# ==========================
# Sidebar Filters
# ==========================

st.sidebar.header("Filters")

workflow = st.sidebar.multiselect(
    "Workflow",
    options=df["workflow_name"].unique(),
    default=df["workflow_name"].unique()
)

branch = st.sidebar.multiselect(
    "Branch",
    options=df["branch"].unique(),
    default=df["branch"].unique()
)

df = df[
    (df["workflow_name"].isin(workflow)) &
    (df["branch"].isin(branch))
]

# ==========================
# KPI Cards
# ==========================

total_runs = len(df)
successful_runs = len(df[df["conclusion"] == "success"])
failed_runs = len(df[df["conclusion"] == "failure"])

success_rate = (
    successful_runs / total_runs * 100
    if total_runs > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("📊 Total Runs", total_runs)
col2.metric("✅ Successful", successful_runs)
col3.metric("❌ Failed", failed_runs)
col4.metric("📈 Success Rate", f"{success_rate:.2f}%")

st.markdown("---")

# ==========================
# Charts
# ==========================

left, right = st.columns(2)

with left:

    pie_data = pd.DataFrame({
        "Result": ["Success", "Failure"],
        "Count": [successful_runs, failed_runs]
    })

    pie = px.pie(
        pie_data,
        values="Count",
        names="Result",
        title="Workflow Result Distribution",
        hole=0.45
    )

    st.plotly_chart(pie, width="stretch")

with right:

    workflow_chart = (
        df.groupby("workflow_name")
        .size()
        .reset_index(name="Runs")
    )

    bar = px.bar(
        workflow_chart,
        x="workflow_name",
        y="Runs",
        title="Workflow Runs"
    )

    st.plotly_chart(bar, width="stretch")

st.markdown("---")

# ==========================
# Recent Runs
# ==========================

st.subheader("📋 Workflow History")

st.dataframe(
    df,
    width="stretch",
    hide_index=True
)