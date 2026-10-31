import streamlit as st

st.markdown("# 📚 Resources & Tips")
st.markdown("Learn how to optimize your resume for ATS systems")
st.markdown("# 🎯 ATS Optimization Tips")
left,rigth=st.columns(2)

with left:
    st.markdown(
        """
### ✅ Do's:
- Use standard section headings
- Include relevant keywords from job description
- Use simple, clean formatting
- List skills explicitly
- Quantify achievements with numbers
- Use standard fonts (Arial, Calibri, Times New Roman)
- Save as PDF or DOCX
""")

with rigth:
    st.markdown(
        """
### ❌ Don'ts:
- Avoid tables and text boxes
- Don't use headers/footers for important info
- Avoid images and graphics
- Don't use unusual fonts
- Avoid columns (use single column layout)
- Don't keyword stuff
- Avoid abbreviations without spelling out first
""")
st.markdown("---")
st.markdown("# 🔑 Common ATS Keywords by Industry")
tab1,tab2,tab3=st.tabs(["💻 Tech","🎨 Creative","💼 Business"])
with tab1:
    st.markdown("""
### Software Development:
- Programming languages (Python, Java, JavaScript)
- Frameworks (React, Django, Spring)
- Tools (Git, Docker, Kubernetes)
- Methodologies (Agile, Scrum, CI/CD)
""")
with tab2:
    st.markdown("""
### Creative & Design:
- Adobe Creative Suite
- UI/UX Design
- Wireframing & Prototyping
- Brand identity
- Visual communication
""")
with tab3   :
    st.markdown("""
### Business & Management:
- Project management
- Stakeholder engagement
- Budget management
- Strategic planning
- Team leadership
""")