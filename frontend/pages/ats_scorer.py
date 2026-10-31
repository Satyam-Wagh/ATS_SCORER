import streamlit as st
import requests
import time

def show_anylisis_result(data):
    st.markdown("---")
    st.success("Anylisis Completed")
    _,middle,_=st.columns([1,2,1])
    with middle:
        st.markdown("# 📊 Analysis Result")
        with st.container(border=True):
            st.title(data.get("ATS_score"))
            st.write("Overall ATS score")
    #bonuses
    st.success(f"bonuses {data["component_scores"]["bonuses"]["perfact_grammer"]}")
    st.error(f"Penelties ")#get bonus
    st.markdown("---")

def show_score_breakdown(score):
    st.markdown("#### 📈 Score Breakdown")
    left,right=st.columns(2)
    with left:
       st.subheader(f"Formating:")
       st.progress(score.get("formatting")/20)
       st.subheader(f"keywords:")
       st.progress(score.get("keywords")/25)
       st.subheader(f"ATS compatibility:")
       st.progress(score.get("ats_compatibility")/15)
    with right:
       st.subheader(f"content:")
       st.progress(score.get("content")/25)
       st.subheader(f"skill validation:")
       st.progress(score.get("skill_validation")/15)     
    st.markdown("---")   
#line 3
def show_strength(strenghts):
    st.markdown("### 💪 Strengths")
    if not strenghts:
        st.info("Keep improving your resume to unlock strengths!")
    for i in strenghts:
        st.markdown(f"- ✅{i}")
    st.markdown("---")
#line 4
def show_issues(issue,issu_summary):
    st.markdown("### 🚨 Critical Issues")
    st.error("These issues should be addressed first for better ATS performance.")
    if not issue:
        st.success("Congratulations no any issu found..")
    for i in issu_summary:
        st.markdown(f"🔴 {i}")
    with st.expander("View detail break down of Issues"):
        for item in issue:
    # Outer box to isolate each issue cleanly
            with st.container(border=True):
                st.subheader(item["issue_title"])
                col1, col2 = st.columns(2)
                with col1:
                    st.caption("Severity Level")
                    st.write(f"**{item['severity_level']}**")
                with col2:
                    st.caption("ATS Impact")
                    st.write(f"**{item['ats_impact']}**")
                    
                st.write(item["explanation"])
                with st.expander("🛠️ View Breakdown & Action Items"):
                    st.write(f"**Location:** `{item['where_it_appears']}`")
                    st.write(f"**Recommendation:** {item['how_to_fix']}")
                    
                    # Action sub-list
                    st.write("**Next Steps:**")
                    for action in item["action_items"]:
                        st.write(f"- {action}")
                    st.info(f"**Example Template Improvement:**\n\n{item['example_improvement']}")
#line 5
def skill_validation(skill_vall):
    left,middle,right=st.columns(3)
    validate=skill_vall.get("validated_count")
    unval=len(skill_vall.get("unvalidated"))
    with left:
        st.metric(label="Totle Skill",value=skill_vall.get("total",0))
    with middle:
        st.metric(label="Validated skills",value=skill_vall.get("validated_count"),delta=str(skill_vall.get("validation_pct"))+"%")
    with right:
        st.metric(label="Unvalidated skills",value=len(skill_vall.get("unvalidated")),delta=-len(skill_vall.get("unvalidated")))
    if validate<unval:
        st.error(f"Only {validate} % skills are validated.Add a projects to demonstrating your skills.")
    #expander for validated skills
    with st.expander(f"Validated Skills ({validate})"):
        for i in skill_vall.get("validated"):
            st.write(f" 🟢 {i["skill"]}:")
            pro=""
            for j in i["projects"]:
                pro=pro+","+j
            pro_list=list(pro)
            pro_list[0]=""
            pro = "".join(pro_list)
            st.write(f"- Demonstreated in: {pro}")
    #expander for validated skills
    with st.expander(f"Unvalidated Skills ({unval})"):
        for skill in skill_vall.get("unvalidated"):
            st.write(f"🔴 {skill}")
    st.markdown("---")
def validate(resume,jd=None)->bool:
    if not resume:
        st.error("Please upload the resume..")
        return False
    if select_option=="Job Description comparision" and len(job_description)==0:
        st.error("Please paste your JD..")
        return False
    return True
#line 6
def intrepretation(string):
    st.info(string)
    st.markdown("---")
def send_request_resume_file_only(resume_file,job_description=None):
    url="http://127.0.0.1:8000/api/v1/analyse_resume"
    files={"resume_file":(resume_file.name,resume_file.getvalue(),resume_file.type),"jd":job_description}
    
    responce=requests.post(url=url,files=files)
    return responce.json()

st.markdown("# 🎯 ATS scorer")
st.markdown("Upload your resume — and optionally a job description — for a comprehensive analysis.")
st.markdown("---")
select_option=st.radio(label="Select Analysis mode",options=["General ATS score","Job Description comparision"],index=0)
st.markdown("---")
left,right=st.columns(2)
with left:
    st.markdown("""
## 📄 Upload Resume
Choose your resume file
""")
    resume=st.file_uploader(label="5MB per file • PDF",type="pdf" )
with right:
    st.markdown("""
## 📋 Job Description
""")
    job_description=None
    if select_option=="Job Description comparision":
        job_description=st.text_area(label="Paste here your job Description...",placeholder="Type or paste the job requirements here...")
    else:
        st.info("Switch to 'Job Description Comparison' mode to enable JD matching.")
if st.button("🚀 Analyze Your Resume", use_container_width=True,type="primary"):
    if validate(resume,job_description):
        #send request
        with st.spinner("Please wait your anaylisis will processing"):
            try:
                data=send_request_resume_file_only(resume_file=resume,job_description=None)
                print(data)
            except requests.exceptions.ConnectionError:
                st.error("Cheak your internet connection...")
            if "detail" not in data:
                #line 1
                show_anylisis_result(data=data)
                #line 2
                show_score_breakdown(score=data.get("component_scores"))
                #line 3
                show_strength(data.get("strengths"))
                #line 4
                show_issues(issue=data.get("detailed_feedback"),issu_summary=data.get("issues_summary"))
                #line 5
                skill_validation(
                skill_vall=data.get("skill_validation_details")
                )
                if "experience_months" in data:
                    st.markdown("experience Section")
                    st.info(f"You have {data.get("experience_months",0)} months of experience in industry")
                    st.markdown("---")
                if "interpretation" in data:
                    st.markdown("# interpretation")
                    intrepretation(data.get("interpretation"))
                #line 6
            elif ("detail" in data) and ("detail"=="could not read the your document"):
                st.error(data["detail"])    
            else:
                st.error("Sorry your server is bussy or somthing wents wrong at server side ")
                st.info("Please contact to support!")