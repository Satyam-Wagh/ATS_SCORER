#https://share.streamlit.io/user/kcodess2807 demo #pass 123456789
import streamlit as st

#set page configuration
st.set_page_config(
    page_title="ATS Resume Scorer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)
#defines pages
main_page=st.Page("pages/home.py",title="Main Page", icon="🏠")
ats_page=st.Page("pages/ats_scorer.py",title="ATS Scorer Page", icon="🎯")
resource_page=st.Page("pages/resources.py",title="Resources Page", icon="📚")

pg=st.navigation([main_page,ats_page,resource_page])

pg.run()