import streamlit as st
import pandas as pd
import os

from backend.database import get_question_mapping, get_project
from backend.file_handler import load_project_survey, load_project_quota
from backend.qa_engine import (
    build_project_overview,
    run_duplicate_id_check,
    run_missing_values_check,
    run_quota_compliance,
    run_speed_check,
)

st.set_page_config(page_title="QA Checks", layout="wide")

st.title("🛡️ QA Automation Suite")

project = st.session_state.get("current_project")
if project is None:
    st.error("No active project found. Please create or open a project first.")
    st.stop()

project_folder = os.path.join("uploads", project)
if not os.path.isdir(project_folder):
    st.error(f"Project directory uploads/{project} does not exist.")
    st.stop()

try:
    survey = load_project_survey(project_folder)
except Exception as exc:
    st.error(f"Could not load survey data: {exc}")
    st.stop()

quota_df = load_project_quota(project_folder)
project_config = get_question_mapping(project) or {}

if st.session_state.get("qa_project") != project:
    st.session_state["qa_run"] = False
    st.session_state["qa_project"] = project

st.markdown(f"### QA sweep for **{project}**")
st.info(f"Loaded dataset with {len(survey):,} rows and {len(survey.columns)} columns.")

id_col = st.selectbox(
    "Respondent ID column for duplicate validation:",
    survey.columns.tolist(),
    index=survey.columns.tolist().index(project_config.get("respondent_id")) if project_config.get("respondent_id") in survey.columns else 0,
)

numeric_columns = survey.select_dtypes(include=["number"]).columns.tolist()
duration_col = st.selectbox(
    "Duration / LOI column (optional):",
    ["None"] + numeric_columns,
    index=( ["None"] + numeric_columns).index(project_config.get("duration")) if project_config.get("duration") in numeric_columns else 0,
)

st.markdown("---")

if "qa_run" not in st.session_state:
    st.session_state["qa_run"] = False

if st.button("🚀 Run QA Automation Suite"):
    st.session_state["qa_run"] = True

if st.session_state["qa_run"]:
    st.markdown("### 📊 QA Report Summary")

    overview = build_project_overview(survey)
    duplicates = run_duplicate_id_check(survey, id_col)
    missing_counts = run_missing_values_check(survey)
    missing_total = int(missing_counts.sum())

    speed_data = None
    if duration_col != "None":
        speed_data = run_speed_check(survey, duration_col)

    quota_results = run_quota_compliance(survey, quota_df)

    m1, m2, m3 = st.columns(3)
    m1.metric("Interviews Reviewed", f"{overview['total_rows']:,}")
    m2.metric("Duplicate rows found", f"{len(duplicates):,}")
    m3.metric("Missing values", f"{missing_total:,}")

    if speed_data is not None:
        m4, m5 = st.columns(2)
        m4.metric("Median duration", f"{speed_data['median_duration']:.1f}")
        m5.metric("Speeder count", f"{len(speed_data['speeders']):,}")

    with st.expander("Duplicate records detail", expanded=True):
        if len(duplicates) > 0:
            st.warning(f"{len(duplicates)} records share the same Respondent ID.")
            st.dataframe(duplicates)
            duplicates_csv = duplicates.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download duplicate record list",
                data=duplicates_csv,
                file_name=f"{project}_duplicates.csv",
                mime="text/csv",
            )
        else:
            st.success("No duplicate Respondent ID entries detected.")

    with st.expander("Missing values matrix", expanded=False):
        if missing_total > 0:
            missing_df = missing_counts[missing_counts > 0].reset_index()
            missing_df.columns = ["Column", "Missing count"]
            st.dataframe(missing_df)
            missing_csv = missing_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download missing values summary",
                data=missing_csv,
                file_name=f"{project}_missing_values.csv",
                mime="text/csv",
            )
        else:
            st.success("No missing values found in the selected dataset.")

    if speed_data is not None:
        with st.expander("Speeder / Duration threshold analysis", expanded=True):
            st.write(f"Median duration: **{speed_data['median_duration']:.2f}**")
            st.write(f"Speeder threshold (40% of median): **{speed_data['threshold']:.2f}**")
            if len(speed_data["speeders"]) > 0:
                st.error(f"{len(speed_data['speeders']):,} interviews completed faster than expected.")
                st.dataframe(speed_data["speeders"])
                speed_csv = speed_data["speeders"].to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download speeders list",
                    data=speed_csv,
                    file_name=f"{project}_speeders.csv",
                    mime="text/csv",
                )
            else:
                st.success("No speeders were detected in the selected duration field.")

    with st.expander("Quota compliance review", expanded=True):
        if quota_df is None:
            st.info("No quota file found in the current project folder.")
        else:
            st.write(quota_results.get("message"))
            quota_table = quota_results.get("compliance_table")
            if quota_table is not None:
                st.dataframe(quota_table)
                quota_csv = quota_table.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download quota compliance summary",
                    data=quota_csv,
                    file_name=f"{project}_quota_compliance.csv",
                    mime="text/csv",
                )

    st.markdown("---")
    if st.button("Proceed to Data Dashboard ➡️"):
        st.switch_page("pages/6_Dasboard.py")
