import re
from backend.models.schemas import IssueDetails

def analyse_issue(parsed_resume:dict,text:str,skill_validation:dict,projetcs:list,contact_info=None,score=dict):
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
    unvalidate_skills=skill_validation.get('unvalidated_skills')
    validated_skills=skill_validation.get('validated_skills')

    totle_skills=len(unvalidate_skills)+len(validated_skills)

    if totle_skills>0 and len(unvalidate_skills)>len(validated_skills):
        unsupported_list=",".join(unvalidate_skills[:8])
        pct_unsupported=round((len(unvalidate_skills)/totle_skills)*100)
        action_items_list=[f"Mention {i} in your Experince or project section "for i in unvalidate_skills[:5]]
        if len(unvalidate_skills)>5:
            action_items_list.append("Remove the skills which is not demonstrate with any project or experience.")
            detected.append(IssueDetails(
            issue_title="Most Skills Lack Supporting Evidence",
            severity_level="Moderate",
            ats_impact="High",
            explanation=(
                f"{pct_unsupported}% of your listed skills ({len(unvalidate_skills)} out of "
                f"{totle_skills}) are not backed by any mention in your projects or "
                "experience sections. Recruiters and ATS systems cross-reference "
                "skills against actual work to verify credibility."
            ),
            where_it_appears=f"These skills have no supporting context: {unsupported_list}",
            how_to_fix=(
                "For each skill in your Skills section, ensure it appears at least "
                "once in a project description or experience bullet point. "
                "Describe how and where you used that technology."
            ),
            action_items=action_items_list,
            example_improvement=(
                f"Your skill '{unvalidate_skills[0]}' has no supporting evidence.\n\n"
                f"Fix: Add to a project or experience bullet:\n"
                f"'Built a data pipeline using {unvalidate_skills[0]} that processed "
                "10K records daily, reducing manual effort by 60%.'"
            )
            ))
    #6. Weak Action Verbs 
    description_line=[
       line.strip() for i in exp_entries for line in i.get("description",'').split("\n") if line.strip()
    ]

    if len(description_line)>3 and len(parsed_resume.get("action_verbs",[]))<3:
        detected.append(IssueDetails(
            issue_title="Bullet Points Lack Strong Action Verbs",
            severity_level="Moderate",
            ats_impact="Medium",
            explanation=(
                f"Your experience section has {len(description_line)} bullet points but "
                f"only {len(parsed_resume.get("action_verbs",[]))} start with strong action verbs. "
                "ATS systems and recruiters favor bullets that begin with verbs like "
                "'Developed', 'Implemented', 'Designed', 'Optimized'."
            ),
            where_it_appears="Experience section — bullet point openings",
            how_to_fix=(
                "Start every bullet point with a past-tense action verb. "
                "Avoid starting with 'Responsible for', 'Worked on', or 'Helped with'. "
                "Use verbs like: Developed, Built, Designed, Implemented, Led, Automated, Optimized."
            ),
            action_items=[
                "Rewrite every bullet that starts with 'Responsible for', 'Helped', 'Worked on', or 'Assisted'",
                "Use: Developed, Built, Designed, Implemented, Led, Automated, Optimized, Deployed, Reduced, Increased",
                "Make verbs past-tense for previous roles, present-tense for current role",
                f"Review all {len(description_line)} bullet points — at least {len(description_line)} should start with action verbs",
                "Avoid weak openers like 'Was responsible for...' or 'Involved in...'",
            ],
            example_improvement=(
                "Before:\n"
                "• Responsible for building the backend\n"
                "• Worked on the payment feature\n\n"
                "After:\n"
                "• Developed a REST API with FastAPI handling 5K daily requests\n"
                "• Implemented Stripe payment integration reducing checkout time by 30%"
            )
        ))
         #7. No Quantifiable Achievements 
        number_pattern=r'\d+[%+]?|\$\d+'
        has_metrices=bool(re.findall(number_pattern,experience_text)) if experience_text else False

        if experience_text and not has_metrices:
            detected.append(IssueDetails(  issue_title="No Quantifiable Achievements Found",
            severity_level="Moderate",
            ats_impact="Medium",
            explanation=(
                "Your experience section does not contain any measurable outcomes "
                "(numbers, percentages, or dollar amounts). Quantified achievements "
                "make your impact concrete and are strongly preferred by recruiters."
            ),
            where_it_appears="Experience section — bullet point content",
            how_to_fix=(
                "Add numbers to at least 50% of your bullet points. "
                "Include metrics like: users served, response time improved, "
                "revenue generated, lines of code, team size, etc."
            ),
            action_items=[
                "Go through each bullet point and ask: 'How much?', 'How many?', 'By what %?'",
                "Add metrics: users served, requests/day, % improvement, team size, time saved",
                "Examples: '500+ daily users', 'reduced load time by 40%', 'handled 10K API calls/day'",
                "If exact numbers aren't known, use reasonable estimates (e.g., '~200 users')",
                "Aim for numbers in at least 50% of your experience bullets",
            ],
            example_improvement=(
                "Before:\n"
                "• Improved application performance\n"
                "• Managed a team of developers\n\n"
                "After:\n"
                "• Improved API response time by 45% through Redis caching\n"
                "• Led a team of 5 developers delivering 3 features per sprint"
            )))
    #8. Missing Contact Information 
    contact_info={"email":parsed_resume.get("email",None),"phone":parsed_resume.get("phone",None),"linkedin":parsed_resume.get("linkedin",None),"github":parsed_resume.get("github",None)}
    if contact_info:
        missing_contact=[]
        if not contact_info.get("email"):
            missing_contact.append("email")
        if not contact_info.get("phone"):
            missing_contact.append("phone")
        if not contact_info.get("linkedin"):
            missing_contact.append("linkedin Url")

        if len(missing_contact)>=2:
            contact_action_items=[f"Add your {i} in header section "for i in missing_contact]
            contact_action_items += [
                "Format the contact line as: email | phone | linkedin | github",
                "Make sure your LinkedIn URL is a custom short URL (linkedin.com/in/yourname)",
                "Add a GitHub link if you have public projects (github.com/yourname)",]
            detected.append(IssueDetails(
                    issue_title="Incomplete Contact Information",
                severity_level="High",
                ats_impact="High",
                explanation=(
                    f"Your resume is missing: {', '.join(missing_contacts)}. "
                    "Recruiters need reliable ways to reach you. Missing contact "
                    "details can cause your application to be skipped entirely."
                ),
                where_it_appears="Header / Contact section at the top of the resume",
                how_to_fix=(
                    "Add your full name, email, phone number, LinkedIn profile, "
                    "and optionally a GitHub or portfolio link at the top of your resume."
                ),
                action_items=contact_action_items,
                example_improvement=(
                    "Add at top:\n"
                    "John Doe\n"
                    "john.doe@email.com | +91-9876543210\n"
                    "linkedin.com/in/johndoe | github.com/johndoe"
                )
                ))
    # 9. Low Formatting Score
    formating_score=score.get("formating_score",20)
    if formating_score<10:
        detected.append(IssueDetail(
            issue_title="Poor Resume Formatting",
            severity_level="High",
            ats_impact="High",
            explanation=(
                f"Your formatting score is {formatting_score}/20, which indicates "
                "problems like missing section headers, inconsistent structure, "
                "or non-standard layout that ATS parsers struggle with."
            ),
            where_it_appears="Overall document structure and formatting",
            how_to_fix=(
                "Use a clean, single-column layout with standard section headers "
                "(Experience, Education, Skills, Projects). Use consistent bullet "
                "points, standard fonts, and avoid tables, columns, or graphics."
            ),
            action_items=[
                "Switch to a single-column layout (avoid two-column templates for ATS)",
                "Use standard section headers: EXPERIENCE, EDUCATION, SKILLS, PROJECTS",
                "Use bullet points (•) consistently — don't mix with dashes or asterisks",
                "Remove all tables, text boxes, headers/footers, and images — ATS cannot parse them",
                "Use a standard font (Calibri, Arial, Times New Roman) at 10–12pt",
                "Order sections: Contact → Summary → Experience → Projects → Education → Skills",
            ],
            example_improvement=(
                "Use this structure:\n"
                "NAME & CONTACT\n"
                "SUMMARY (2-3 lines)\n"
                "EXPERIENCE (reverse chronological)\n"
                "PROJECTS (2-3 key projects)\n"
                "EDUCATION\n"
                "SKILLS (categorized)"
            )
            ))
    #10. Missing Summary/Objectives
    if not parsed_resume.get("professional_summary"):
        detected.append(IssueDetails(issue_title="Missing Professional Summary",
            severity_level="Low",
            ats_impact="Low",
            explanation=(
                "Your resume does not include a Professional Summary or Objective "
                "section at the top. While not required, a 2-3 line summary helps "
                "recruiters quickly understand your profile and target role."
            ),
            where_it_appears="Top of resume — below contact info",
            how_to_fix=(
                "Add a 2-3 sentence summary highlighting your experience level, "
                "key skills, and career focus. Tailor it to the job you're applying for."
            ),
            action_items=[
                "Add a 'PROFESSIONAL SUMMARY' or 'OBJECTIVE' section at the top of your resume",
                "Write 2–3 sentences: who you are, your key skills, and what role you seek",
                "Mention your years of experience or education level upfront",
                "Tailor this section for each job application — reference the specific role",
                "Keep it under 60 words — recruiters spend only 6 seconds on first scan",
            ],
            example_improvement=(
                "Add:\n"
                "PROFESSIONAL SUMMARY\n"
                "Full-stack developer with 2+ years of experience building scalable "
                "web applications using React, Node.js, and AWS. Passionate about "
                "clean architecture and performance optimization."
        )))
    return detected


def generate_summary_issue(detected_issues:list[IssueDetails]):
    #Extract the issue title to formulate the issue_summary list
    return [i.issue_title for i in detected_issues]