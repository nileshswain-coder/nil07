import streamlit as st
import os

from backend.database import get_question_mapping, save_question_mapping, get_project
from backend.file_handler import load_project_survey

st.set_page_config(page_title="Project Configuration", layout="wide")

st.title("Project Configuration")

project = st.session_state.get("current_project")
if project is None:
    st.error("No active project. Please create or open a project first.")
    st.stop()

project_meta = get_project(project)

if project_meta:
    st.markdown(
        f"**Project:** {project_meta['project_name']}  \n"
        f"**Wave type:** {project_meta['wave_type']}  \n"
        f"**Created:** {project_meta['created_date']}"
    )

project_folder = os.path.join("uploads", project)
if not os.path.isdir(project_folder):
    st.error(f"Project folder uploads/{project} was not found.")
    st.stop()

try:
    survey = load_project_survey(project_folder)
except Exception as exc:
    st.error(f"Could not load survey data: {exc}")
    st.stop()

questions = survey.columns.tolist()
existing_mapping = get_question_mapping(project) or {}

st.subheader("Map important survey columns for QA")

respondent = st.selectbox(
    "Respondent ID column",
    questions,
    index=questions.index(existing_mapping.get("respondent_id")) if existing_mapping.get("respondent_id") in questions else 0,
)

duration = st.selectbox(
    "Duration / LOI column",
    ["None"] + questions,
    index=( ["None"] + questions).index(existing_mapping.get("duration")) if existing_mapping.get("duration") in questions else 0,
)

awareness = st.selectbox(
    "Awareness question column",
    questions,
    index=questions.index(existing_mapping.get("awareness")) if existing_mapping.get("awareness") in questions else 0,
)

consideration = st.selectbox(
    "Consideration question column",
    questions,
    index=questions.index(existing_mapping.get("consideration")) if existing_mapping.get("consideration") in questions else 0,
)

purchase = st.selectbox(
    "Purchase intent question column",
    questions,
    index=questions.index(existing_mapping.get("purchase")) if existing_mapping.get("purchase") in questions else 0,
)

usage = st.selectbox(
    "Usage or category question column",
    questions,
    index=questions.index(existing_mapping.get("usage")) if existing_mapping.get("usage") in questions else 0,
)

if st.button("Save Configuration"):
    save_question_mapping(
        project,
        respondent,
        duration if duration != "None" else "",
        awareness,
        consideration,
        purchase,
        usage,
    )
    st.success("Configuration saved successfully.")
    st.info("Proceed to the automated QA sweep for this project.")
    st.switch_page("pages/5_QA_Checks.py")
