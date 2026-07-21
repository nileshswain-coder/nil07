import streamlit as st
from backend.database import initialize_database

st.set_page_config(
    page_title="QA Automation Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

initialize_database()

# -----------------------------
# Custom CSS (Keeping your button styles)
# -----------------------------
st.markdown("""
<style>

/* Custom styling for full-width theme buttons */
.stButton>button {
    width: 100%;
    height: 60px;
    font-size: 20px;
    border-radius: 10px;
    background: #0F4C81;
    color: white;
}

.stButton>button:hover {
    background: #1E6BB8;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("QA Automation Engine")
st.write("")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    # Using a native Streamlit container to act as a clean card wrapper
    with st.container(border=True):
        st.subheader("🆕 New Study")
        st.write("Create a brand new project.")
        
        if st.button("Create New Study", key="new_study_btn"):
            st.switch_page("pages/1_Home.py")

with col2:
    # Using a native Streamlit container to act as a clean card wrapper
    with st.container(border=True):
        st.subheader("📂 Existing Study")
        st.write("Open an existing project.")
        
        if st.button("Open Existing Study", key="exist_study_btn"):
            st.switch_page("pages/3_Existing_Study.py")