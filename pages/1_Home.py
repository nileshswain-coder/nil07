import streamlit as st
from backend.database import add_project
from datetime import datetime
import os
import shutil

st.set_page_config(page_title="New Study", layout="wide")

st.title("🆕 New study")
st.markdown("---")

project_name = st.text_input("Project Name")

wave_type = st.radio(
    "Wave Type",
    ["Single Wave", "Multiple Wave"],
    horizontal=True
)

survey_file = st.file_uploader(
    "Upload Survey File",
    type=["csv", "xlsx"]
)

quota_file = st.file_uploader(
    "Upload Quota File",
    type=["xlsx"]
)

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        "Download Quota Template",
        data=b"",
        file_name="Quota_Template.xlsx"
    )

with col2:
    if st.button("Create Project"):
        if project_name == "":
            st.error("Enter Project Name")
        elif survey_file is None:
            st.error("Upload Survey File")
        elif quota_file is None:
            st.error("Upload Quota File")
        else:
            project_folder = os.path.join("uploads", project_name)
            os.makedirs(project_folder, exist_ok=True)
            
            survey_path = os.path.join(project_folder, survey_file.name)
            with open(survey_path, "wb") as f:
                f.write(survey_file.getbuffer())
                
            quota_path = os.path.join(project_folder, quota_file.name)
            with open(quota_path, "wb") as f:
                f.write(quota_file.getbuffer())
                
            add_project(
                project_name,
                wave_type,
                0,
                survey_path,
                quota_path,
                datetime.now().strftime("%Y-%m-%d")
            )
            
            st.session_state["current_project"] = project_name
            st.success("Project Created Successfully!")
            
            # Fixed to match 4_Project_Config.py in your sidebar
            st.switch_page("pages/4_Project_Config.py")