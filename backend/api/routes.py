from fastapi import Request,APIRouter,File,UploadFile,HTTPException,Form,Depends
from models.schemas import is_server_on,Text_extractor,AnalysisResponse,JDComparison,SkillValidationDetails,ComponentScores
from services.resume_file_parser import resume_parser
from services.groq_parser import parse_resume
from services.analyse_full_resume import analyse_resume

router=APIRouter(prefix="/api/v1")


#main part
@router.post("/analyse_resume",response_model=AnalysisResponse)
async def analyse_resumes(request:Request,resume_file:UploadFile=File(...,description="Uploade your pdf file to anylisis"),jd=Form('',description="Job description text (optional)")):
    #parsing
    try:
        file=await resume_file.read()
        file_name=resume_file.filename or "Untitle"
        text=resume_parser(file=file)
    except Exception as exce:
        raise HTTPException(
            status_code=422,
            detail="could not read the your document"
        )
    #FUll Anyalisis
    nlp=request.app.state.nlp
    embedder=request.app.state.embedder
    try:
        result=analyse_resume(resume_text=text,nlp=nlp,embedder=embedder,job_descripation=jd)
    except Exception as exce:
        raise HTTPException(status_code=500,detail=f"Analisis pipeline fail :{exce}")
    #jd comparission
    jd_comparision_result=None
    if result.get("jd_comparison"):
        jd_comparision_result=JDComparison(
            match_percentage=round(result["jd_comparison"].get("match_percentege",0.0)),
            matched_keywords=result["jd_comparison"].get("match_words",[]),
            missing_keywords=result["jd_comparison"].get("miss_word",[]),
            semantic_similarity=round(result["jd_comparison"].get("semantic_similarity",0.0))
        )

    detail_feedback=result.get("detailed_feedback",[])
    skv=result.get("skill_validation_details",{})
    skv_detail=SkillValidationDetails(
        validated=skv.get("validated",[]),
        unvalidated=skv.get("unvalidated",[]),
        total=skv.get("total",0),
        validated_count=skv.get("validated_count",0),
        validation_pct=skv.get("validation_pct",0)
    )

    responce=AnalysisResponse(
        ATS_score=result.get("ats_score"),
        component_scores=ComponentScores(**result["component_scores"]),
        issues_summary=result["issues_summary"],
        detailed_feedback=detail_feedback,
        jd_match_analysis=jd_comparision_result,
        skill_validation_details=skv_detail,
        ats_score=result.get("ats_score"),
        keyword_match=jd_comparision_result.match_percentage if jd_comparision_result else 0.0,
        missing_keywords=result.get("missing_keywords",[]),
        matched_keywords=result.get("matched_keywords",[]),
        skills=result.get("skills",[]),
        jd_comparison=jd_comparision_result
    )

    return responce
#learning part
@router.post("/extract_json")
async def extract_json(request:Request,resume:UploadFile=File(...,description="Uploade your pdf file to extract json")):
    file=await resume.read()
    text=resume_parser(file=file)
    res=parse_resume(raw_text=text)
    return res
@router.post("/sum")
async def test(a,b):
    return a+b
@router.post("/tesing",response_model=is_server_on)
async def testing(resume:UploadFile=File(...,description="Resume File")):
    res=is_server_on(status=True)
    return res

@router.post("/extract",response_model=Text_extractor)
async def extract(resume:UploadFile=File(...,description="Upload the file to extract the texts")):
    file=await resume.read()
    result=resume_parser(file=file)
    return Text_extractor(text=result)

@router.get("/test_life")
async def test_life(req:Request):
    A=req.app
    return A

@router.get("/json")
async def test_json(request:Request):
    text='''
  Satyam Anil Wagh \n\nsatyamwagh2006@gamil.com |  9373410917 |  Pune, Maharashtra \nLinkedIn  | \n\n|GitHub \n\nEDUCATION \n\nB.E. Computer Engineering, TSSM's Bhivarabai Sawant College of \nEngineering and Research, Pune \nSGPA: 8.32 (IV Sem)   \n\nHSC – 69%, D.M.J.C. Ale Tal:Junnar Dist:Pune \n\nSSC – 83%, D.M.H Ale Tal:Junnar Dist:Pune \n\nSKILLS \n\nLanguages: Python, JavaScript \nWeb: HTML5, CSS3, Bootstrap \n\nFrameworks:FastApi,sklearn,Flask,Straml\nit \n\nTools: Git and github ,Dockers \n\nSpoken: English (fluent) \n\nMAJOR PROJECT \n\n2024 – 2028\n\n2024\n\n2022\n\nATS_SCORER | (https://github.com/Satyam-Wagh/ATS_SCORER) \nTechnologies: HTML5, CSS3, JavaScript,Python, FastApi, sklearn, Git and github \n\n  Developed a full-stack web application that extracts skills and experience from uploaded resumes \n\n(PDF/DOCX) and evaluates job description alignment using semantic similarity.  \n\n  Engineered the backend API using FastAPI and spaCy to handle asynchronous file parsing, and implemented \n\nSentence Transformers (all-MiniLM-L6-v2) for advanced NLP matching.  \n\n \n\n \n\nIntegrated the Groq API (Llama 3) to generate dynamic, LLM-driven optimization feedback and structural \nsuggestions for users.  \n\nImplemented secure user authentication (Email/Password & Google OAuth) and database persistence using \nSupabase to save analysis histories. \n\n  Designed an intuitive frontend dashboard with Streamlit and added custom PDF report exporting via \n\nWeasyPrint and Jinja2 templating \n\nMINOR PROJECTS \n\nCreaditWise_Loan_System | (https://github.com/Satyam-Wagh/CreaditWise_Loan_System) \n\nTechnologies HTML5, CSS3,javscript,Flask,python, Git and github \n\n  Engineered an end-to-end intelligent loan approval system that automates the verification process \n\nby predicting applicant risk to eliminate human bias and accelerate processing speeds. \n\n  Developed and trained a binary classification model using Logistic Regression over historical \ncustomer data, achieving optimized predictions for loan eligibility (Approved vs. Rejected). \n\n  Built a scalable backend API engine using Python and Flask (app.py) to handle live HTTP scoring \n\nrequests and load pickled machine learning artifacts (scaler.pkl, model.pkl). \n\n  Optimized system latency by executing preprocessing steps (Label Encoding and One-Hot \nEncoding) on the client side using asynchronous JavaScript, effectively minimizing server \noverhead. \n\nCERTIFICATES \n\nAI Fundamentals: Foundations for Understanding AI – IBM  |  AI Literacy – IBM \n\n \n \n \n \n \n \n \n \n \n \n \n \n\f'''
    data={
  "name": "Satyam Anil Wagh",
  "email": "satyamwagh2006@gamil.com",
  "phone": "9373410917",
  "linkedin": None,
  "github": None,
  "professional_summary": "",
  "skills": [
    "Python",
    "JavaScript",
    "HTML5",
    "CSS3",
    "Bootstrap",
    "FastApi",
    "sklearn",
    "Flask",
    "Streamlit",
    "Git",
    "GitHub",
    "Docker",
    "English (fluent)"
  ],
  "experience": [],
  "education": [
    {
      "degree": "B.E. Computer Engineering",
      "institution": "TSSM's Bhivarabai Sawant College of Engineering and Research, Pune",
      "year": ""
    },
    {
      "degree": "HSC",
      "institution": "D.M.J.C. Ale Tal:Junnar Dist:Pune",
      "year": ""
    },
    {
      "degree": "SSC",
      "institution": "D.M.H Ale Tal:Junnar Dist:Pune",
      "year": ""
    }
  ],
  "certifications": [
    "AI Fundamentals: Foundations for Understanding AI – IBM",
    "AI Literacy – IBM"
  ],
  "projects": [
    {
      "title": "ATS_SCORER",
      "description": "Developed a full‑stack web application that extracts skills and experience from uploaded resumes (PDF/DOCX) and evaluates job description alignment using semantic similarity. Engineered the backend API using FastAPI and spaCy to handle asynchronous file parsing, and implemented Sentence Transformers (all‑MiniLM‑L6‑v2) for advanced NLP matching. Integrated the Groq API (Llama 3) to generate dynamic, LLM‑driven optimization feedback and structural suggestions for users. Implemented secure user authentication (Email/Password & Google OAuth) and database persistence using Supabase to save analysis histories. Designed an intuitive frontend dashboard with Streamlit and added custom PDF report exporting via WeasyPrint and Jinja2 templating.",
      "technologies": [
        "HTML5",
        "CSS3",
        "JavaScript",
        "Python",
        "FastApi",
        "sklearn",
        "Git",
        "GitHub",
        "spaCy",
        "Sentence Transformers",
        "all-MiniLM-L6-v2",
        "Groq API",
        "Llama 3",
        "Supabase",
        "Streamlit",
        "WeasyPrint",
        "Jinja2"
      ]
    },
    {
      "title": "CreaditWise_Loan_System",
      "description": "Engineered an end‑to‑end intelligent loan approval system that automates the verification process by predicting applicant risk to eliminate human bias and accelerate processing speeds. Developed and trained a binary classification model using Logistic Regression over historical customer data, achieving optimized predictions for loan eligibility. Built a scalable backend API engine using Python and Flask to handle live HTTP scoring requests and load pickled machine learning artifacts. Optimized system latency by executing preprocessing steps (Label Encoding and One‑Hot Encoding) on the client side using asynchronous JavaScript, effectively minimizing server overhead.",
      "technologies": [
        "HTML5",
        "CSS3",
        "JavaScript",
        "Flask",
        "Python",
        "Git",
        "GitHub",
        "Logistic Regression",
        "Machine Learning",
        "Label Encoding",
        "One‑Hot Encoding"
      ]
    }
  ],
  "action_verbs": [
    "Developed",
    "Engineered",
    "Implemented",
    "Integrated",
    "Designed",
    "Built",
    "Optimized",
    "Trained",
    "Handled",
    "Loaded",
    "Executed"
  ],
  "keywords": [
    "resume parsing",
    "skill extraction",
    "experience extraction",
    "semantic similarity",
    "job description alignment",
    "NLP",
    "FastAPI",
    "spaCy",
    "Sentence Transformers",
    "all-MiniLM-L6-v2",
    "LLM",
    "Groq API",
    "Llama 3",
    "authentication",
    "Google OAuth",
    "Supabase",
    "Streamlit",
    "WeasyPrint",
    "Jinja2",
    "loan approval",
    "risk prediction",
    "Logistic Regression",
    "machine learning",
    "Flask",
    "Docker",
    "Git",
    "GitHub",
    "HTML5",
    "CSS3",
    "JavaScript",
    "Python",
    "sklearn",
    "Bootstrap"
  ]
}
    nlp=request.app.state.nlp
    embedder=request.app.state.embedder
    responce=analyse_resume(resume_text=text,nlp=nlp,embedder=embedder,parsed_resume=data,job_descripation=None)
    return responce