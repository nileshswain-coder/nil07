import streamlit as st
import pandas as pd
import os

from backend.database import get_project
from backend.file_handler import load_project_survey, load_project_quota
from backend.qa_engine import build_project_overview, summarize_field

st.set_page_config(page_title="Project Dashboard", layout="wide")

st.title("📊 Project Insights & Analytics Dashboard")

project = st.session_state.get("current_project")
if project is None:
    st.error("No active project found. Please create or open a project first.")
    st.stop()

project_meta = get_project(project)
if project_meta is None:
    st.error(f"Project metadata for {project} could not be loaded.")
    st.stop()

project_folder = os.path.join("uploads", project)
if not os.path.isdir(project_folder):
    st.error(f"Project directory uploads/{project} does not exist.")
    st.stop()

try:
    survey = load_project_survey(project_folder)
except Exception as exc:
    st.error(f"Unable to load survey dataset: {exc}")
    st.stop()

st.markdown(
    f"**Project:** {project_meta['project_name']}  \n"
    f"**Wave type:** {project_meta['wave_type']}  \n"
    f"**Created:** {project_meta['created_date']}"
)

overview = build_project_overview(survey)

m1, m2, m3 = st.columns(3)

m1.metric("Completed Interviews", f"{overview['total_rows']:,}")
m2.metric("Tracked Variables", overview['total_columns'])
m3.metric("Numeric Metrics", len(overview['numeric_columns']))

st.markdown("---")

st.subheader("🎯 Variable Profiling")
selected_column = st.selectbox(
    "Choose a column to profile:",
    survey.columns.tolist(),
)

if selected_column:
    if pd.api.types.is_numeric_dtype(survey[selected_column]) and survey[selected_column].nunique() > 20:
        st.caption(f"Numeric distribution summary for {selected_column}")
        st.line_chart(survey[selected_column].dropna())
    else:
        st.caption(f"Frequency distribution for {selected_column}")
        st.bar_chart(survey[selected_column].value_counts())

    stats = summarize_field(survey, selected_column)["summary"]
    st.dataframe(stats, use_container_width=True)

st.markdown("---")

st.subheader("📋 Raw Data Explorer")
with st.expander("View the full survey dataset", expanded=False):
    st.dataframe(survey, use_container_width=True)

csv_data = survey.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Cleaned Project Dataset (.CSV)",
    data=csv_data,
    file_name=f"{project}_Cleaned_Data.csv",
    mime="text/csv",
)

st.markdown("---")

quota_df = load_project_quota(project_folder)
if quota_df is not None:
    st.subheader("📑 Quota Sheet Preview")
    st.dataframe(quota_df, use_container_width=True)

if st.button("Back to QA Checks"):
    st.switch_page("pages/5_QA_Checks.py")
