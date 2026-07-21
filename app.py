import streamlit as st
from backend.database import initialize_database

st.set_page_config(
    page_title="QA Automation Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_database()

st.markdown(
    """
    <style>
        .stButton>button {
            width: 100%;
            height: 60px;
            font-size: 18px;
            border-radius: 10px;
            background: #0F4C81;
            color: white;
        }

        .stButton>button:hover {
            background: #1E6BB8;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("QA Automation Engine")
st.write("Empower your Nielsen research operations with fast project setup, automated survey QA sweeps, and executive dashboards.")
st.markdown("---")

with st.sidebar:
    st.markdown("## Quick links")
    if st.button("New Study"):
        st.switch_page("pages/1_Home.py")
    if st.button("Open Existing Study"):
        st.switch_page("pages/3_Existing_Study.py")
    st.markdown("---")
    project = st.session_state.get("current_project")
    if project:
        st.markdown(f"### Active Project\n**{project}**")
        st.write("Use the quick links above to continue the workflow.")
    else:
        st.write("Start with a new project or open an existing one.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🆕 New Study")
    st.write("Create a brand-new QA automation project with survey and quota files.")
    if st.button("Create New Study", key="home_create_new"):
        st.switch_page("pages/1_Home.py")

with col2:
    st.subheader("📂 Existing Study")
    st.write("Open an active project, refresh the dataset, and continue QA.")
    if st.button("Open Existing Study", key="home_open_existing"):
        st.switch_page("pages/3_Existing_Study.py")
