from fastapi import Request,APIRouter,File,UploadFile,HTTPException,Form,Depends
from models.schemas import AnalysisResponse,JDComparison,SkillValidationDetails,ComponentScores
from services.resume_file_parser import resume_parser
from services.groq_parser import parse_resume
from services.analyse_full_resume import analyse_resume
import logging
# ==========================================
# LOGGING CONFIGURATION
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
    handlers=[
        logging.FileHandler("analysis_rout.log", encoding="utf-8"),
        logging.StreamHandler()  # Keeps terminal streaming active for dev console visibility
    ]
)
logger = logging.getLogger("analysis_route_logger")

router=APIRouter(prefix="/api/v1")


#main part
@router.post("/analyse_resume", response_model=AnalysisResponse)
async def analyse_resumes(
    request: Request,
    resume_file: UploadFile = File(..., description="Uploade your pdf file to anylisis"),
    jd = Form('', description="Job description text (optional)")
):
    logger.info("--- NEW RESUME ANALYSIS REQUEST RECEIVED ---")
    logger.info(f"Target Filename: {resume_file.filename or 'Untitled'} | Content-Type: {resume_file.content_type}")
    logger.info(f"Job Description Provided: {'Yes' if jd and jd.strip() else 'No'} (Length: {len(jd) if jd else 0} chars)")

    # 1. Parsing Document Tier
    try:
        logger.info("Reading raw upload payload from stream...")
        file = await resume_file.read()
        file_name = resume_file.filename or "Untitle"
        
        logger.info(f"Executing extraction pipeline wrapper 'resume_parser' for: {file_name}")
        text = resume_parser(file=file)
        
        extracted_len = len(text) if text else 0
        logger.info(f"Document parser execution completed successfully. Extracted text length: {extracted_len} chars")
        if extracted_len == 0:
            logger.warning("Extracted text stream from the uploaded document is entirely empty.")
            
    except Exception as exce:
        logger.error(f"Critical execution error during file ingestion/parsing sequence: {str(exce)}", exc_info=True)
        raise HTTPException(
            status_code=422,
            detail="could not read the your document"
        )

    # 2. Pipeline Extraction & AI Inference Tier
    logger.info("Retrieving localized app-state NLP pipeline and vector embedding instances...")
    nlp = request.app.state.nlp
    embedder = request.app.state.embedder
    
    try:
        logger.info("Dispatching text payload to core logic handler: 'analyse_resume'...")
        result = analyse_resume(resume_text=text, nlp=nlp, embedder=embedder, job_descripation=jd)
        logger.info("Core analysis pipeline returned result dictionary successfully.")
    except Exception as exce:
        logger.error(f"Critical exception raised during NLP/Embedding evaluation layer: {str(exce)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analisis pipeline fail :{exce}")

    # 3. Job Description Cross-Matching Transformation Tier
    jd_comparision_result = None
    if result.get("jd_comparison"):
        logger.info("Found valid 'jd_comparison' sub-data matrix. Commencing mapping alignment...")
        jd_data = result["jd_comparison"]
        
        raw_match_pct = jd_data.get("match_percentege", 0.0)
        raw_semantic = jd_data.get("semantic_similarity", 0.0)
        
        logger.debug(f"Raw incoming validation values -> match_pct: {raw_match_pct}, semantic: {raw_semantic}")
        
        jd_comparision_result = JDComparison(
            match_percentage=round(raw_match_pct),
            matched_keywords=jd_data.get("match_words", []),
            missing_keywords=jd_data.get("miss_word", []),
            semantic_similarity=round(raw_semantic)
        )
        logger.info(f"JDComparison mapping completed: Rounded Match -> {jd_comparision_result.match_percentage}%")
    else:
        logger.info("No 'jd_comparison' metrics found in the payload result. Skipping JD structure parsing.")

    # 4. Parsing Feedback & Validation Elements
    logger.info("Processing ancillary details: Detailed Feedback arrays & Skill Validation counts...")
    detail_feedback = result.get("detailed_feedback", [])
    skv = result.get("skill_validation_details", {})
    
    logger.debug(f"Extracted feedback entries: {len(detail_feedback)} | Found skill validation metadata key subset.")
    
    skv_detail = SkillValidationDetails(
        validated=skv.get("validated", []),
        unvalidated=skv.get("unvalidated", []),
        total=skv.get("total", 0),
        validated_count=skv.get("validated_count", 0),
        validation_pct=skv.get("validation_pct", 0)
    )

    # 5. Target Response Schema Alignment Block
    logger.info("Compiling final 'AnalysisResponse' data structure wrapper...")
    try:
        comp_scores_raw = result.get("component_scores", {})
        logger.debug(f"Target instantiation payload structure for ComponentScores: {comp_scores_raw}")
        
        responce = AnalysisResponse(
            ATS_score=result.get("ats_score"),
            component_scores=ComponentScores(**comp_scores_raw),
            issues_summary=result.get("issues_summary"),
            detailed_feedback=detail_feedback,
            jd_match_analysis=jd_comparision_result,
            skill_validation_details=skv_detail,
            ats_score=result.get("ats_score"),
            keyword_match=jd_comparision_result.match_percentage if jd_comparision_result else 0.0,
            missing_keywords=result.get("missing_keywords", []),
            matched_keywords=result.get("matched_keywords", []),
            skills=result.get("skills", []),
            jd_comparison=jd_comparision_result,
            interpretation=result.get("interpretation",""),
            experience_months=result.get("experience_months",0)
        )
        logger.info(f"Successfully serialized AnalysisResponse. Output ATS Score: {responce.ATS_score}")
    except Exception as serialization_err:
        logger.error(f"Data type conversion error during Response Model parsing constraint check: {str(serialization_err)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server data mapping schema constraint mismatch.")

    logger.info("--- ROUTE WORKFLOW DISPATCH COMPLETED SUCCESSFULLY ---")
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

#this rout is temporery
@router.post("/test-anylisis")
async def test_json(request:Request,file:UploadFile=File(...,description="This is test route")):
    null=None
    text = """Ms. Abhilasha Wagh
Email (): waghabhilasha2024@gmail.com
Mob. (): +91 8999445209
CAREER OBJECTIVE
To join with a progressive and growing organization where my skills can realize and my knowledge can 
escalate for the benefit of the organization as well as for personal development.
PROFESSIONAL EXPERIENCE
1) Cinetrix Infotech Pvt. Ltd. — Automation Tester
Feb 2020 – September 2022
2) Expleo India Infosystems Pvt. Ltd. — Senior software Engineer
November 2022 – present
4.2+ Years of industry experience in Software Testing (Automation) with proficiency in testing the Web-based 
application.
PROFESSIONAL SUMMARY
 Hands on experience on Automation testing using Selenium WebDriver with Core Java.
 Extensively worked with Cucumber (BDD) framework along with Junit.
 Good knowledge of SDLC, STLC, Defect Life Cycle.
 Expertise in Black Box Testing- Smoke, Sanity, Regression testing.
 Involving in Creating, Reviewing & Executing Test cases.
 Working in Agile- Scrum model.
 Having experience of using a JIRA as project management tool.
 Participate in Scrum ceremonies.
 Using Eclipse IDE to write selenium test scripts with Java.
TECHNICAL SKILLS
 Testing Process : Manual, Automation
 Testing tool : Selenium Web Driver
 Programming languages : Core Java
 Framework : Cucumber BDD with Junit
 IDE : Eclipse
 Bug Tracking tool : JIRA
 Build and Dependencies management tool : Maven
 Version control tool : GIT
 Source code management tool : Github
 Project Management tool : JIRA
 Methodologies: : Agile- Scrum
QUALIFICATION DETAILS
 BE from Smt. Kashibai Navale College of Engineering, Sinhgad Institute, Pune with 72.86% in 2017.
 Diploma from Cusrow Wadia Institute of Technology, Pune with 81.61% in 2014.
 SSC from Subhash Vidya Mandir, Junnar with 89.09% in 2011.
PROJECTS
Project 1:
 Project name : E-commerce Web Application
 Duration : 2 year 7 months (Feb 2020 – September 2022)
 Designation : Automation Tester
 Tools : Selenium WebDriver, Core Java, Cucumber BDD, Junit, Eclipse IDE, GIT, JIRA, Maven
 Testing Process : Manual and Automation
Project Description:
This application is online shopping website where user can search and buy a different products like women’s, 
men’s, kid’s fashion, baby products, home accessories, outdoor and garden furniture, decor etc. Users can search 
a product and select from suggested product list, also can zoom the product view. They can add it to wishlist or 
in my basket. Users can buy the online product. Also, they can view the product reviews and write their own 
reviews.
Responsibilities:
 Automate scenarios using Selenium WebDriver and execute them using Junit.
 Used Page object model and Cucumber Framework concept to organize the automation code.
 Attending daily stand up meetings and scrum review and retrospective meetings.
 Creating, executing and maintaining test cases.
 Generating logs for debugging purpose.
 Execution of smoke test and generating the report using Cucumber.
 Identified bugs during the black box testing, raised them in Jira and resolved them with developers 
within the timeframe.
 Generate & Analyze reports.
Project 2:
 Project name : AWC (Active Workspace)
 Client : Applied Materials 
 Duration : 1.5 year (November 2022 - Present)
 Designation : Senior Software Engineer
 Tools : Selenium WebDriver, Core Java, Cucumber BDD, Junit, Eclipse IDE, GIT, JIRA, Maven
 Testing Process : Automation
Project Description:
AWC Applied Material Inc. is an American corporation that supplies equipment, services and software to enable 
the manufacture of semiconductor, flat panel display, WEB and solar products. This application testing involve 
customized Siemens Teamcenter integration with CAD tools. PLM software allows to manage information 
throughout the entire life cycle of product efficiently and cost effectively, design and manufacture through 
service and disposal.
Responsibilities:
 Analyzed business requirements to understand the application flow
 Involvement in framework upgradation and design like Function development, build reusable and 
customized functions, Automate new test cases, Regression, Defect reporting.
 Designing and execution of test cases as per functionality of web application
 Involve in Framework enhancement to improve the execution speed.
 Experience in Page Object Model design pattern in framework
 Daily status reporting and bug reporting
 Involve in daily standup meeting to report status of project activities
 Involve in QA automation testing and Go Live automation testing 
PERSONAL DETAILS
 Date of Birth : 28th September 1995.
 Gender : Female.
 Nationality : Indian.
 Language Known : English, Hindi, Marathi.
 Permanent Address : At post- Pimpalwandi, Taluka- Junnar, Dist- Pune, Pincode- 412412."""

    data={
  "name": "Abhilasha Wagh",
  "email": "waghabhilasha2024@gmail.com",
  "phone": "+91 8999445209",
  "linkedin": null,
  "github": null,
  "professional_summary": "To join with a progressive and growing organization where my skills can realize and my knowledge can escalate for the benefit of the organization as well as for personal development.",
  "skills": [
    "Manual Testing",
    "Automation Testing",
    "Selenium WebDriver",
    "Core Java",
    "Cucumber BDD",
    "JUnit",
    "Eclipse IDE",
    "JIRA",
    "Maven",
    "GIT",
    "GitHub",
    "Agile Scrum",
    "SDLC",
    "STLC",
    "Defect Life Cycle",
    "Black Box Testing",
    "Smoke Testing",
    "Sanity Testing",
    "Regression Testing",
    "Page Object Model",
    "Test Case Design",
    "Bug Tracking",
    "Project Management",
    "Continuous Integration",
    "Team Collaboration",
    "Communication"
  ],
  "experience": [
    {
      "job_title": "Automation Tester",
      "company": "Cinetrix Infotech Pvt. Ltd.",
      "start_date": "Feb 2020",
      "end_date": "September 2022",
      "duration_months": 31,
      "description": "Created, reviewed, and executed manual and automated test cases for a web‑based e‑commerce application. Automated scenarios using Selenium WebDriver with Java, implemented Page Object Model and Cucumber BDD framework, generated test reports, identified and logged defects in JIRA, and participated in daily Scrum ceremonies."
    },
    {
      "job_title": "Senior Software Engineer",
      "company": "Expleo India Infosystems Pvt. Ltd.",
      "start_date": "November 2022",
      "end_date": "Present",
      "duration_months": 47,
      "description": "Analyzed business requirements for the AWC (Active Workspace) application, enhanced and upgraded the automation framework to improve execution speed, designed and executed automated test cases using Selenium, Java, and Cucumber, maintained Page Object Model, reported daily status and bugs, and performed QA automation and Go‑Live testing."
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Engineering (BE)",
      "institution": "Smt. Kashibai Navale College of Engineering, Sinhgad Institute, Pune",
      "year": "2017"
    },
    {
      "degree": "Diploma",
      "institution": "Cusrow Wadia Institute of Technology, Pune",
      "year": "2014"
    },
    {
      "degree": "SSC",
      "institution": "Subhash Vidya Mandir, Junnar",
      "year": "2011"
    }
  ],
  "certifications": [],
  "projects": [
    {
      "title": "E‑commerce Web Application",
      "description": "Online shopping website allowing users to search, view, add to wishlist, and purchase products across multiple categories. Implemented end‑to‑end test automation covering search, product details, cart, checkout, and review functionalities.",
      "technologies": [
        "Selenium WebDriver",
        "Core Java",
        "Cucumber BDD",
        "JUnit",
        "Eclipse IDE",
        "GIT",
        "JIRA",
        "Maven"
      ]
    },
    {
      "title": "AWC (Active Workspace)",
      "description": "Testing of a PLM application integrating Siemens Teamcenter with CAD tools for semiconductor, flat‑panel display, and solar product manufacturing. Involved in requirement analysis, framework enhancement, and automation of functional and regression test suites.",
      "technologies": [
        "Selenium WebDriver",
        "Core Java",
        "Cucumber BDD",
        "JUnit",
        "Eclipse IDE",
        "GIT",
        "JIRA",
        "Maven"
      ]
    }
  ],
  "action_verbs": [
    "Automate",
    "Execute",
    "Use",
    "Attend",
    "Create",
    "Generate",
    "Identify",
    "Raise",
    "Resolve",
    "Analyze",
    "Involve",
    "Design",
    "Build",
    "Report",
    "Test",
    "Maintain",
    "Debug",
    "Enhance",
    "Upgrade",
    "Develop",
    "Reuse",
    "Customize",
    "Participate"
  ],
  "keywords": [
    "Selenium WebDriver",
    "Core Java",
    "Cucumber BDD",
    "JUnit",
    "Eclipse IDE",
    "GIT",
    "GitHub",
    "Maven",
    "JIRA",
    "Agile Scrum",
    "SDLC",
    "STLC",
    "Defect Life Cycle",
    "Black Box Testing",
    "Smoke Testing",
    "Sanity Testing",
    "Regression Testing",
    "Page Object Model",
    "Test Automation",
    "Manual Testing",
    "QA Automation",
    "PLM",
    "Siemens Teamcenter",
    "CAD tools",
    "Semiconductor",
    "Flat panel display",
    "Solar products",
    "Business Requirements",
    "Framework Enhancement",
    "Test Case Design",
    "Bug Reporting",
    "Continuous Integration",
    "Project Management",
    "Collaboration"
  ]
}
    nlp=request.app.state.nlp
    embedder=request.app.state.embedder
    responce=analyse_resume(resume_text=text,nlp=nlp,embedder=embedder,parsed_resume=data,job_descripation=None)
    return responce