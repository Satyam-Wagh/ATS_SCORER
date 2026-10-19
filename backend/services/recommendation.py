import re
from backend.models.schemas import IssueDetails

def analyse_issue(parsed_resume:dict,text:str,skill_validation:dict,projetcs:list,contact_info=None):
    detected=[]
    #unpack the frquently used structured fields
    exp_entries=[i for i in parsed_resume.get("experience",[]) if isinstance(i,dict)]
    edu_entries=[i for i in parsed_resume.get("education",[]) if isinstance(i,dict)]
    pro_entries=[i for i in parsed_resume.get("projects",[])if isinstance(i,dict)]

    summary=parsed_resume.get("professional_summary",'').strip() #Handle None to prevent string concatenation errors

    #create the experince text for re pattern
    experience_text=""
    for i in parsed_resume.get("experience",''):
        experience_text+=i+'\n'
    experience_text=experience_text.strip()

    #1) missing projects
    resume_lower=text.strip()
    has_project_signal=any(i in resume_lower for i in [
        'project', 'github.com', 'deployed', 'built a', 'developed a',
        'created a', 'implemented a', 'live demo', 'tech stack',
    ])

    if not pro_entries and len(projetcs)==0 and not has_project_signal:
        detected.append(IssueDetails(issue_title="Missing Projects Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                "Your resume does not have a dedicated Projects section. "
                "ATS systems and recruiters look for concrete projects to validate "
                "that your listed skills have been applied in practice."
            ),

            where_it_appears="Resume structure — no 'Projects' header was detected",

            how_to_fix=(
                "Add a 'Projects' section with 2–3 significant projects. "
                "For each project, include the title, technologies used, "
                "what you built, and a measurable outcome."
            ),

            action_items=[
                "Add a 'PROJECTS' section heading after your Experience section",
                "Include 2–3 projects (personal, academic, or open-source)",
                "For each project: write the title, tech stack used, what you built, and a measurable result",
                "Example: 'E-Commerce Platform — React, Node.js, MongoDB. Handled 500+ transactions/month'",
                "Link to GitHub or a live demo if available (e.g., github.com/yourname/project)",
            ],

            example_improvement=(
                "Add:\n"
                "PROJECTS\n"
                "• E-Commerce Platform — Built a full-stack shopping site using "
                "React, Node.js, and MongoDB. Implemented payment processing with "
                "Stripe, handling 500+ transactions/month.\n"
                "• ML Sentiment Analyzer — Trained a BERT model on 10K reviews "
                "achieving 92% accuracy. Deployed as a REST API with FastAPI."
            ),
        ))

    #2) experirnce sections
    has_signal_experince=any(i in resume_lower for i in [
        'intern', 'internship', 'employed', 'worked at', 'working at',
        'company', 'organization', 'job', 'role', 'position', 'designation',
        'manager', 'engineer', 'developer', 'analyst', 'consultant',
    ])
    if not has_project_signal and not exp_entries:
        detected.append(IssueDetails(issue_title="Missing Work Experience Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                "No work experience section was detected. Even for freshers, "
                "internships, freelance work, or volunteer experience help "
                "demonstrate professional capability."
            ),
            where_it_appears="Resume structure — no 'Experience' or 'Work History' header found",
            how_to_fix=(
                "Add an 'Experience' section. If you lack formal employment, "
                "include internships, freelance projects, open-source contributions, "
                "or relevant volunteer work."
            ),
            action_items=[
                "Add an 'EXPERIENCE' or 'INTERNSHIPS' section to your resume",
                "List each role with: Job Title — Company Name (Month Year – Month Year)",
                "Add 2–4 bullet points per role describing what you did and its impact",
                "If no formal job: include internships, freelance work, open-source, or college clubs",
                "Start every bullet with a past-tense action verb (Developed, Built, Led, etc.)",
            ],
            example_improvement=(
                "Add:\n"
                "EXPERIENCE\n"
                "Software Engineering Intern — XYZ Corp (Jun 2025 – Aug 2025)\n"
                "• Developed REST APIs with FastAPI serving 10K requests/day\n"
                "• Reduced page load time by 40% through caching optimization"
            ),
        ))
    #3)missing education section
    has_edu_signal=any(i in resume_lower for i in [
        'b.tech', 'btech', 'b.e.', 'b.sc', 'bsc', 'm.tech', 'mtech', 'm.sc',
        'bachelor', 'master', 'phd', 'university', 'college',
        'institute of technology', 'cgpa', 'gpa', 'graduated', 'diploma',
        'class of', '20', 'batch of',
    ])
    if not has_edu_signal and not edu_entries:
        detected.append(IssueDetails(issue_title="Missing Education Section",
            severity_level="Moderate",
            ats_impact="Medium",
            explanation=(
                "No education section was found. Most ATS systems expect an "
                "Education section with at least your degree and institution."
            ),
            where_it_appears="Resume structure — no 'Education' header detected",
            how_to_fix=(
                "Add an 'Education' section listing your degree, university, "
                "graduation year, and optionally your GPA or relevant coursework."
            ),
            action_items=[
                "Add an 'EDUCATION' section (usually at the bottom for experienced candidates, top for freshers)",
                "Include: Degree name — Institution name (Start Year – End Year)",
                "Add your CGPA or percentage if it is 7.0+ or 70%+",
                "Optionally list 3–5 relevant courses (e.g., Data Structures, DBMS, ML)",
            ],
            example_improvement=(
                "Add:\n"
                "EDUCATION\n"
                "B.Tech in Computer Science — IIT Delhi (2021–2025)\n"
                "CGPA: 8.5 | Relevant Coursework: Data Structures, ML, DBMS"
            )))
    #4. Missing Skills Section 
    if not parsed_resume.get("education") and not len(parsed_resume.get("education"))<3:#also flag when user add few skills
        detected.append(IssueDetails(issue_title="Missing or Weak Skills Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                f"Only {len(skills)} skill(s) were detected. ATS systems "
                "rely heavily on keyword matching from a dedicated Skills section. "
                "Without clear skills listed, your resume may fail automated filters."
            ),
            where_it_appears="Skills section — either missing or contains very few items",
            how_to_fix=(
                "Add a clear 'Skills' section organized by category. "
                "Include programming languages, frameworks, tools, and soft skills "
                "that match your target role."
            ),
            action_items=[
                "Add a 'TECHNICAL SKILLS' or 'SKILLS' section",
                "Organize by category: Languages, Frameworks, Tools, Databases, Cloud",
                "List at least 10–15 skills relevant to your target role",
                "Use the exact names that appear in job descriptions (e.g., 'React.js' not just 'React')",
                "Include tools you use daily: Git, VS Code, Postman, Docker, etc.",
            ],
            example_improvement=(
                "Add:\n"
                "TECHNICAL SKILLS\n"
                "Languages: Python, JavaScript, TypeScript, SQL\n"
                "Frameworks: React, FastAPI, Django, Express.js\n"
                "Tools: Docker, Git, AWS, PostgreSQL, MongoDB"
            )))
        #5 skills lack of supporting evidances
        