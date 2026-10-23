from sentence_transformers import SentenceTransformer
import spacy
from services.groq_parser import parse_resume,parse_jd
from services.scoreing_engine import validate_skill,calculate_overall_score
from services.feedback import analyse_issue,generate_summary_issue
from services.jd_matcher import compare_resume_with_jd
from utils.file_utils import get_default_grammar_results,get_default_location_results


def analyse_resume(resume_text:str,nlp:spacy.language,embedder:SentenceTransformer,job_descripation:None):
    parsed_resume=parse_resume(raw_text=resume_text)

    skills=parsed_resume.get("skills",[])
    projects=parsed_resume.get("projects",[])
    keywords=parsed_resume.get("keywords",[])
    action_verb=parsed_resume.get("action_verbs",[])

    experience_month=sum(
        i.get("duration_months",0) for i in parsed_resume.get("experience") if isinstance(i,dict) 
    )

    contact_info={
        "email":parsed_resume.get("email",''),
        "phone":parsed_resume.get("phone",''),
        "linkedin":parsed_resume.get("linkedin",''),
        "github":parsed_resume.get("github",'')
    }

    skill_validations=validate_skill(skills=skills,embedder=embedder,experience_entries=parsed_resume.get("experience",[]),projects=projects)

    jd_comparission_result=None
    jd_keywords=None

    if job_descripation and job_descripation.strip():
        #parse jd
        parsed_jd=parse_jd(raw_text=job_descripation)
        jd_keywords=list[set(parsed_resume.get("required_skills",[])+parsed_jd.get("preferred_skills",[])+parsed_jd.get("keywords",[]))]

        jd_comparission_result=compare_resume_with_jd(resume_text=resume_text,resume_keyword=keywords,jd_text=job_descripation,jd_keywords=jd_keywords,embedder=embedder)

    grammer_results=get_default_grammar_results()
    location_results=get_default_location_results()

    scores=calculate_overall_score(text=resume_text,parsed_resume=parsed_resume,skills=skills,keywords=keywords,action_verbs=action_verb,skill_validation_results=skill_validations,grammar_results=grammer_results,location_results=location_results,jd_keywords=jd_keywords,experience_months=experience_month)

    detail_feedback=analyse_issue(parsed_resume=parsed_resume,text=resume_text,skill_validation=skill_validations,projetcs=projects,contact_info=contact_info,score=scores)

    issue_summary=generate_summary_issue(detected_issues=detail_feedback)

    validated_raw=scores.get("validated_skills",[])
    unvalidated_raw=scores.get("unvalidated_skills",[])
    total_skills=len(validated_raw) + len(unvalidated_raw)
    val_pct=round((len(validated_raw) / total_skills * 100) if total_skills > 0 else 0, 1)
    skill_validation_detail={
         "validated": [
            {
                "skill":    item['skill'],
                "projects": item.get('projects', []),
            }
            for item in validated_raw
        ],
        "unvalidated":     unvalidated_raw,
        "total":           total_skills,
        "validated_count": len(validated_raw),
        "validation_pct":  val_pct,
    }

    return {
        "ATS_score":          scores['overall_score'],
        "ats_score":          scores['overall_score'],
        "component_scores": {
            "formatting":       scores['formating_score'],
            "keywords":         scores['keyword_score'],
            "content":          scores['content_score'],
            "skill_validation": scores['skill_validation_score'],
            "ats_compatibility": scores['ats_compatibility_score'],
        },
        "issues_summary":    issue_summary,
        "detailed_feedback": detail_feedback,
        "jd_match_analysis": jd_comparission_result,
        "jd_comparison":     jd_comparission_result,
        "skills":            skills,
        "matched_keywords":  (
            jd_comparission_result['matched_keywords']
            if jd_comparission_result else list(keywords[:20])
        ),
        "missing_keywords":  (
            jd_comparission_result['missing_keywords']
            if jd_comparission_result else []
        ),
        "strengths": _generate_strengths(parsed_resume, skills, projects, action_verb, skill_validation_detail, scores),
        "interpretation":    scores.get('overall_interpretation', ''),
        "skill_validation_details": skill_validation_detail,
        "experience_months": experience_month,
    }

def _generate_strengths(parsed_resume, skills, projects, action_verbs, skill_validation, scores):
    strength=[]

    if parsed_resume.get("experience"):
        strength.append("Has a dedicated Experience section")
    if parsed_resume.get("projects") or len(projects):
        strength.append("Includes a Projects section showcasing applied skills")
    if parsed_resume.get("education"):
        strength.append("Education section is present")
    if parsed_resume.get("skills"):
        strength.append("Clear Skills section with listed technologies")
    if parsed_resume.get("professional_summary").strip():
        strength.append("Professional Summary provides a quick overview")

    if len(skills)>=8:
        strength.append(f"Strong skill set — {len(skills)} skills detected")
    if len(action_verbs)>=5:
        strength.append(f"Uses {len(action_verbs)} strong action verbs in bullet points")

    validated_skill=skill_validation.get("validated_skills",[])
    if len(validated_skill)>=3:
        strength.append(f"{len(validated_skill)} skills are backed by project/experience evidence")

    if scores.get("formating_score",0)>=16:
        strength.append("Well-formatted and ATS-friendly structure")
    if scores.get("content_score",0)>=20:
        strength.append("Content quality is high with measurable achievements")
    return strength