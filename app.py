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
# Custom CSS
# -----------------------------

st.markdown("""
<style>
.main{
    background-color:#F6F8FC;
}
h1{
    color:#0F4C81;
    text-align:center;
}
.card{
    padding:25px;
    border-radius:15px;
    background:white;
    box-shadow:0px 2px 12px rgba(0,0,0,0.08);
}
.stButton>button{
    width:100%;
    height:60px;
    font-size:20px;
    border-radius:10px;
    background:#0F4C81;
    color:white;
}
.stButton>button:hover{
    background:#1E6BB8;
    color:white;
}
</style>
""", unsafe_allow_html=True)

st.title("QA Automation Engine")
st.write("")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🆕 New Study")
    st.write("Create a brand new project.")
    
    if st.button("Create New Study"):
        # Fixed to point to 1_Home.py where your form is located
        st.switch_page("pages/1_Home.py")
        
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📂 Existing Study")
    st.write("Open an existing project.")
    
    if st.button("Open Existing Study"):
        # Fixed to match 3_Existing_Study.py in your sidebar
        st.switch_page("pages/3_Existing_Study.py")
        
    st.markdown("</div>", unsafe_allow_html=True)