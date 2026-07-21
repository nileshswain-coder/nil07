import streamlit as st
from datetime import datetime
import os

from backend.database import get_projects, get_project, update_project_files, save_upload_log

st.set_page_config(page_title="Existing Study", layout="wide")

st.title("📂 Open Existing Study")
st.markdown("---")

projects = get_projects()
if not projects:
    st.warning("No existing projects are available. Start a new study first.")
    if st.button("Create New Study"):
        st.switch_page("pages/1_Home.py")
    st.stop()

project = st.selectbox("Select Project", projects)
project_info = get_project(project)

if project_info:
    st.info(f"Loaded metadata for project **{project_info['project_name']}** (Wave: {project_info['wave_type']}).")
    if project_info.get("created_date"):
        st.write(f"Created: {project_info['created_date']}")
    if project_info.get("sample_size"):
        st.write(f"Sample size target: {project_info['sample_size']}")

survey = st.file_uploader(
    "Upload Current Survey Dataset (optional)",
    type=["csv", "xlsx"],
)

if survey is not None:
    if st.button("Save Uploaded Data"):
        sanitized_project = project.strip()
        project_folder = os.path.join("uploads", sanitized_project)
        os.makedirs(project_folder, exist_ok=True)
        survey_path = os.path.join(project_folder, survey.name)
        with open(survey_path, "wb") as f:
            f.write(survey.getbuffer())
        update_project_files(project, survey_file=survey_path)
        save_upload_log(project, survey.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        st.success(f"Survey data uploaded and linked to {project}.")
        st.info("Use Open Project below to continue with the latest dataset.")

if st.button("Open Project"):
    st.session_state["current_project"] = project
    st.success(f"Project {project} is now active.")
    st.switch_page("pages/4_Project_Config.py")
