import streamlit as st

st.markdown("# 🏠 Home")

st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 3rem 2rem;
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #9333EA 100%);
            color: white;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(79, 70, 229, 0.3);
        }
        .main-header h1 {
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

#hero section
st.markdown("""<div class="main-header">
        <h1>🎯 ATS Resume Scorer</h1>
        <h3>Optimize Your Resume for Applicant Tracking Systems</h3>
        <p>Get instant feedback on your resume's ATS compatibility with AI-powered analysis</p>
    </div>
    """, unsafe_allow_html=True)

if st.button("🚀 Start Analyzing Your Resume", use_container_width=True,type="primary"):
    st.switch_page("pages/ats_scorer.py")
st.markdown("---")
st.markdown("# ✨ Key Features")

left,middle,right=st.columns([2,2,1])
with left:
    st.markdown("""
    ### 📊 Comprehensive Scoring

    Get detailed scores across 5 key dimensions:
    - Formatting (20%)
    - Keywords & Skills (25%)
    - Content Quality (25%)
    - Skill Validation (15%)
    - ATS Compatibility (15%)    
""")
with middle:
    st.markdown("""
    ### 🔍 Skill Validation

    Verify that your claimed skills are demonstrated in your projects and experience using AI-powered semantic analysis.
    

    **No more empty claims!**
""")
with right:
    st.markdown("""
    ### 🔒 Privacy First

    All analysis runs locally with no external API calls. Your resume data never leaves your system.

    **100% Private & Secure
""")
st.markdown("---")
st.markdown("# 🚀 How It Works")
left,middle,right=st.columns([2,2,1])
with left:
    st.markdown("""
    ### 1️⃣ Upload Your Resume
    support .pdf files
""")
with middle:
    st.markdown(
        """
 #### 2️⃣ AI Analysis
    Our local AI models analyze your resume across multiple dimensions
""")
with right:
    st.markdown(
        """
        #### 3️⃣ Get Actionable Feedback

        Receive detailed recommendations to improve your resume
        """
    )