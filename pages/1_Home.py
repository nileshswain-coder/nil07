import streamlit as st
from backend.database import add_project, project_exists
from datetime import datetime
import os

st.set_page_config(page_title="New Study", layout="wide")

st.title("🆕 New Study")
st.markdown("---")

project_name = st.text_input("Project Name")

wave_type = st.radio(
    "Wave Type",
    ["Single Wave", "Multiple Wave"],
    horizontal=True,
)

survey_file = st.file_uploader(
    "Upload Survey File",
    type=["csv", "xlsx"],
    help="Upload the latest survey dataset for QA processing.",
)

quota_file = st.file_uploader(
    "Upload Quota File",
    type=["xlsx"],
    help="Upload a quota template or actual quota sheet for the study.",
)

col1, col2 = st.columns(2)

with col1:
    quota_path = os.path.join("templates", "quota_template.xlsx")
    if os.path.exists(quota_path):
        with open(quota_path, "rb") as f:
            quota_bytes = f.read()
        st.download_button(
            "Download Quota Template",
            data=quota_bytes,
            file_name="Quota_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.write("Quota template unavailable.")

with col2:
    if st.button("Create Project"):
        sanitized_name = project_name.strip()
        if sanitized_name == "":
            st.error("Please enter a project name before creating a study.")
        elif project_exists(sanitized_name):
            st.error("A project with this name already exists. Choose a different name or open the existing study.")
        elif survey_file is None:
            st.error("Please upload a survey file to continue.")
        elif quota_file is None:
            st.error("Please upload a quota file to continue.")
        else:
            project_folder = os.path.join("uploads", sanitized_name)
            os.makedirs(project_folder, exist_ok=True)

            survey_path = os.path.join(project_folder, survey_file.name)
            with open(survey_path, "wb") as f:
                f.write(survey_file.getbuffer())

            quota_path = os.path.join(project_folder, quota_file.name)
            with open(quota_path, "wb") as f:
                f.write(quota_file.getbuffer())

            add_project(
                sanitized_name,
                wave_type,
                0,
                survey_path,
                quota_path,
                datetime.now().strftime("%Y-%m-%d"),
            )

            st.session_state["current_project"] = sanitized_name
            st.success("Project created successfully — you can now configure QA mapping.")
            st.info("Project files have been saved to uploads and registered for additional QA steps.")
            st.switch_page("pages/4_Project_Config.py")
