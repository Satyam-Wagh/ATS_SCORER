import re
import spacy
from sentence_transformers import SentenceTransformer
import numpy as np
from backend.utils.matching import fuzzy_match_keywords
ZIP_CODE_PATTERN = r'\b\d{5}(?:-\d{4})?\b'

STREET_ADDRESS_PATTERN = (
    r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+'
    r'(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl)\b'
)
def _tier_score(n: float, tiers:list)-> float:
    for threshold, pts in tiers:
        if n>=threshold:
            return pts
    
    return 0.0

#Location/privacy detection
def detect_location_info(text:str,nlp):
    location=[]
    #method 01: use spacy
    doc=nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["LOC","GPE"]:
            location.append({"text":ent,"type":ent.label_})

    #method 02:street address through regx
    for i in re.finditer(STREET_ADDRESS_PATTERN,text,re.IGNORECASE):
        location.append("text":i.group(),"type":"address"})
    #method 03: zip code
    for i in re.finditer(ZIP_CODE_PATTERN,text):
        location.append({"text":i.group(),"type":"zip"})

    has_address= any(loc['type'] == 'address' for loc in location)
    has_zip     = any(loc['type'] == 'zip'     for loc in location)

    #conditions fror panalty
    if has_address and has_zip:
        privacy_risk,panelty="high",5.0
    elif has_address or has_zip:
        privacy_risk,panelty="high",4.0
    elif len(location)>3:
        privacy_risk,panelty="medium",3.0
    elif location:
        privacy_risk,panelty="low",2.0
    else:
        privacy_risk,panelty="none",0.0

    #create the recommendations
    recommenadations=[]
    if not location:
        recommenadations.append("NO privacy Concern detected")
    if has_address:
        recommenadations.append("Remove Full street address - ATS don't need complete address and it is privacy risk")
    if has_zip:
        recommenadations.append("Remove Zip code - this level of loaction detail is not needed.")
    if privacy_risk in ("low","medium") and not has_address and not has_zip:
        recommenadations.append("Consider reducing location mentions. 'City, State' in the contact header is sufficient.")

    return {
        "recommendaions":recommenadations,
        "locations":len(location),
        "detected_locations":location,
        "privacy_risk":privacy_risk,
        "panelty":panelty
    }
def _calculate_cosine_similarity(skill:str,text:str,embedder:SentenceTransformer):
    #similarity=A.B/(|A|X|B|)
    if not skill and not text:
        return False,0.0
    skill_vector=embedder.encode(skill,convert_to_tensor=False)
    text_vector=embedder.encode(text,convert_to_tensor=False)
    similarity=np.dot(skill_vector,text_vector)/(np.linalg.norm(skill_vector))*np.linalg.norm(text_vector)
    return float(max(0.0, min(1.0, similarity)))

def _skill_matches(text:str,skill:str,embedder:SentenceTransformer,threshold:float):
    #cheack first by python with O(n) complexity
    if skill in text:
        return True,1.0
    #run nural network to match the skills
    sim=_calculate_cosine_similarity(text=text,embedder=SentenceTransformer,skill=skill)
    return sim>=threshold,sim

def validate_skill(skills:list[str],experience_entries:list[dict],projects:list[dict],embedder:SentenceTransformer,threshold:float=0.6):
    if not skill:
        return {
            'validated_skills':      [],
            'unvalidated_skills':    [],
            'validation_percentage': 0.0,
            'skill_project_mapping': {},
            'validation_score':      0.0,
        }
    experince_text=""
    for i in experience_entries:
        experience_entries+=f"{i.get('job_title','')} {i.get('company','')} {i.get('description','')}"
    
    validated_skills=[]
    unvalidated_skills=[]
    skill_project_mapping={}

    for skill in skills:
        matched_project=[]
        max_similarity=0.0
        #match skill with projects
        for i in projects:
            project_text=f"{i.get("title")} {i.get("description")}"
            matched,sim=_skill_matches(skill=skill,text=project_text,embedder=embedder,threshold=threshold)
            max_similarity = max(max_similarity, sim)
            if matched:
                matched_project.append(i.get("title"),"Untitle Project")
        #match skill with experiences
        if experince_text:
            matched,sim=_skill_matches(skill=skill,text=experince_text,embedder=embedder,threshold=threshold)
            if matched and not "Experience section" in matched_project:
                matched_project.append("Experience section")
        if matched_project:
            validated_skills.append({"skill":skill,"projects":matched_project,"similarity":max_similarity})
        else:
            unvalidated_skills.append(skill)
            skill_project_mapping[skill]=[]
    validation_per=len(validated_skills)/len(skills)
    validation_score=validation_per*15.0
    return {
                'validated_skills':validated_skills,
                'unvalidated_skills': unvalidated_skills,
                'validation_percentage':validation_per,
                'skill_project_mapping':skill_project_mapping,
                'validation_score':validation_score,
            }

def _calculate_formatin_score(parssed_resume:dict,text:str):
    score=0.0

    exp_ent=[i for i in parssed_resume.get("experience",[]) if isinstance(i,dict)]
    edu_ent=[i for i in parssed_resume.get("education",[]) if isinstance(i,dict)]
    proj_ent=[i for i in parssed_resume.get("projects",[]) if isinstance(i,dict)]
    skills=parssed_resume.get("skills",[])
    summary=parssed_resume.get("professional_summary",'')

    if exp_ent and any(e.get("job_title") or e.get("description") for e in exp_ent):
        score+=3.0
    if edu_ent:
        score+=2.0
    if len(skills)>3:
        score+=3.0
    if len(summary)>30:
        score+=1.3
    if proj_ent:
        score+=1.5

    bullet_count=sum(1 for line in text.split("\n") if re.match(r'^\s*[•\-\*\◦]', line) or re.match(r'^\s*\d+\.', line))
    score+=_tier_score(bullet_count,[(15,5.0),(10,4.0),(5,3.0),(3,2.0),(1,1.0)])#range of score

    filled=sum(1 for i in [bool(exp_ent),bool(edu_ent),bool(proj_ent),bool(skills),bool(summary.strip())])
    score+=_tier_score(filled,[(4,5.0),(3,4.0),(2,3.0),(1,2.0)])#range of score

    return min(20,max(0.0,score))

def _calculate_keyword_score(resume_keyword:list,skill:list,jd_keywords=None):
    score=0.0
    score+=_tier_score(len(resume_keyword), [(20,10.0),(15,8.0),(10,6.0),(5,4.0),(3,2.0)])
    score+=_tier_score(len(skill), [(15,10.0),(10,8.0),(7,6.0),(5,4.0),(3,2.0)])

    if jd_keywords:
        all_resume_terms=list(set(resume_keyword+skill))
        fuzzy=fuzzy_match_keywords(all_resume_terms,jd_keyword=jd_keywords,threshold=80)
        score+=len(fuzzy["matched"])/len(jd_keywords) if jd_keywords else 0
    elif len(resume_keyword)>=10:
        score+=3.0
    return min(25,min(0.0,max))

def _calculate_content_qulity(text:str,action_verbs:list,gramer_results:dict):
    score=0.0
    score+=_tier_score(len(action_verbs), [(15,10.0),(10,8.0),(7,6.0),(5,4.0),(3,2.0)])
    #identify number patterns
    number_patter= [
        r'\d+%',
        r'\$\d+',
        r'\d+[kKmMbB]',
        r'\d+\s*(?:users|customers|clients|projects|hours|days|months|years)',
        r'(?:increased|decreased|improved|reduced|grew|saved)\s+(?:by\s+)?\d+',
    ]
    achivement_count=sum(len(re.findall(i,text,re.IGNORECASE))for i in number_patter)
    score+=_tier_score(achivement_count,[(10,5.0),(7,4.0),(5,3.0),(3,2.0),(1,1.0)])

    #give penalty to grammer qulity
    grammer_penalty=gramer_results.get("penalty_applied",0.0)
    score+=max(0.0,10-grammer_penalty/2.0)

    return min(25.0,max(0.0,score))

#skill validation score
def _calculate_skill_validation_score(validation_result:dict):
    return max(15.0,min(0.0,validation_result.get("validation_score",0.0)))
#5. ATS COMPATIBILITY SCORE
def _calculate_ats_comptibility(text:str,location_result:dict,parsed_resume:dict):
    score=15.0
    #deduction01
    score-=location_result.get("panelty",0.0)
    #deduction 02
    special_char=len(re.findall(r'[│┤├┼┴┬╔╗╚╝═║╠╣╦╩╬]', text))
    if special_char>20:
        score+=2.0
    elif special_char>10:
        score-=1.0

    exp_entries=[i for i in parsed_resume.get("experience",[]) if isinstance(i,dict)]
    edu_entries=[i for i in parsed_resume.get("education",[]) if isinstance(i,dict)]
    skills_count=len(parsed_resume.get("skills",[]))

    exp_count_len=sum(len(exp_entries.get("description",''))for i in exp_entries)
    edu_count_len=sum(len((e.get('degree') or '') + (e.get('institution') or ''))for i in edu_entries)

    #deduction 03
    short_section=sum([bool(exp_entries)and exp_count_len<20,bool(edu_entries)and edu_count_len<20,bool(parsed_resume.get("skills") and skills_count<2)])
    if short_section<=2:
        score-=2.0
    elif short_section>=1:
        score-=1.0

    if exp_entries and skills_count>5:
        score+=1.0
    return min(15.0,max(0.0,score))

def calculate_overall_score(
    text: str,
    parsed_resume:dict,
    skills: list[str],
    keywords: list[str],
    action_verbs: list[str],
    skill_validation_results: dict,
    grammar_results: dict,
    location_results: dict,
    jd_keywords: list[str] = None,
    experience_months: int = 0,
):
    formating_score=_calculate_formatin_score(parssed_resume=parsed_resume,text=text)
    skill_validation_score=_calculate_skill_validation_score(validation_result=skill_validation_results)
    keyword_score=_calculate_keyword_score(resume_keyword=keywords,skill=skills,jd_keywords=jd_keywords)
    content_score=_calculate_content_qulity(text=text,gramer_results=grammar_results,action_verbs=action_verbs)
    ats_complitibility_score=_calculate_ats_comptibility(text=text,location_result=location_results,parsed_resume=parsed_resume)

   

    COMPONENT_MAX={"foramtating":20,"keyword":25,"content":25,"skill_validation":15,"ats_competibility":15}
    formating_pct=(formating_score/COMPONENT_MAX["foramtating"])*100
    skill_validation_pct=(skill_validation_score/COMPONENT_MAX["skill_validation"])*100
    keyword_pct=(keyword_score/COMPONENT_MAX["keyword"])*100
    content_pct=(content_score/COMPONENT_MAX["content"])*100
    ats_complitibility_pct=(ats_complitibility_score/COMPONENT_MAX["ats_competibility"])*100

    skill_keyword_pct=(keyword_pct*0.6)+(skill_validation_pct*0.4)

    base_score=(skill_keyword_pct*0.4+content_pct*0.3+formating_pct*0.15+ats_complitibility_pct*0.15)

    panalties={}
    bonuses={}
    score=base_score

    if grammar_results.get("penalty_applied",0.0)>0:
        panalties["grammer"]=grammar_results.get("penalty_applied")
    #for location add penulty
    if location_results.get("panelty",0.0)>0:
        panalties["location"]=location_results["panelty"]

    validation_pct=skill_validation_results.get("validation_percentage",0.0)

    #for skill
    if validation_pct>=0.9:
        score+=2.0
        bonuses["excellent_skill_validation"]=2.0
    elif validation_pct>=8:
        score+=1.0
        bonuses["good_skill_validation"]=1.0
    #for grammer
    if grammar_results.get("totle_errors",0.0)==0:
        bonuses["perfact_grammer"]=1.0
        score+=1.0

    name_of_jd_penulty="missing_jd_keywords"
    if jd_keywords and len(jd_keywords)>0:
        all_resume_terms=list(set((keywords or [])+(skills or [])))
        fuzzy=fuzzy_match_keywords(resume_kewords=all_resume_terms,jd_keyword=jd_keywords,threshold=80)
        missing_words_count=len(fuzzy["missing"])
        missing_words_pct=missing_words_count/len(jd_keywords)

        if missing_words_count>=0.7:
            panalties[name_of_jd_penulty]=15.0
            score-=15.0
        elif missing_words_pct>0.5:
            panalties[name_of_jd_penulty]=10.0
            score-=10.0
        elif missing_words_count>0.3:
            panalties[name_of_jd_penulty]=5.0
            score-=5.0

    overall_score=min(100,max(0.0,score))

    interpretaion=_generate_score_interpretation(overall_score)

    return {
        "overall_score":round(overall_score,1),
        "formating_score":round(formating_score,1),
        "keyword_score":round(keyword_score,1),
        "content_score":round(content_score,1),
        "skill_validation_score":round(skill_validation_score,1),
        "ats_compatibility_score":round(ats_complitibility_score,1),
        "overall_interpretation":interpretaion,
        "penalties":panalties,
        "bonuses":bonuses
    }

def generate_strengths(
    score_results: dict,
    skill_validation_results: dict,
    grammar_results: dict,
) :

    strengths = []

    if score_results['formatting_score']       >= 16:
        strengths.append(' Well-structured with clear sections and bullet points')
    if score_results['keywords_score']          >= 20:
        strengths.append(' Strong keyword optimization and skills presence')
    if score_results['content_score']           >= 20:
        strengths.append(' Excellent use of action verbs and quantifiable achievements')
    if score_results['skill_validation_score']  >= 12:
        pct = skill_validation_results.get('validation_percentage', 0) * 100
        strengths.append(f' {pct:.0f}% of skills are validated by projects')
    if score_results['ats_compatibility_score'] >= 13:
        strengths.append(' Excellent ATS compatibility with clean formatting')
    if grammar_results.get('total_errors', 0)   == 0:
        strengths.append(' Error-free grammar and spelling')

    if not strengths:
        strengths.append('Your resume has potential - focus on the recommendations below')
    return strengths

def generate_critical_issue(score_results:dict,grammer_results:dict,location_results:dict):
    issue=[]

    critical_error=len(grammer_results.get("critical_errors",[]))
    if critical_error>0:
        issue.append(f"{critical_error} critical errors/speling errors are detected")
    if location_results.get("privacy_risk")=="high":
        issue.append("High privacy risk remove the detail loaction information")
    if score_results["formatting_score"]<10:
        issue.append("Poor formation in resume. enhance the formating of your resume")
    if score_results["skill_validation_score"]<7:
        issue.append(' Most skills lack supporting evidence in projects')
    return issue

def generate_improvements(
    score_results: Dict,
    skill_validation_results: Dict,
) -> List[str]:
    improvements = []

    if 12 <= score_results['formatting_score']       < 16:
        improvements.append('Add more bullet points and improve section organization')
    if 14 <= score_results['keywords_score']          < 20:
        improvements.append('Include more relevant keywords and technical skills')
    if 14 <= score_results['content_score']           < 20:
        improvements.append('Add more quantifiable achievements and action verbs')
    if 7  <= score_results['skill_validation_score']  < 12:
        unvalidated_count = len(skill_validation_results.get('unvalidated_skills', []))
        improvements.append(f'Validate {unvalidated_count} skill(s) by adding relevant project details')
    if 9  <= score_results['ats_compatibility_score'] < 13:
        improvements.append('Simplify formatting for better ATS compatibility')

    return improvements

def _generate_score_interpretation(overall_score: float) -> str:
    if overall_score >= 90:    return 'Excellent! Your resume is highly optimized for ATS systems.'
    elif overall_score >= 80:  return 'Great! Your resume should perform well with most ATS systems.'
    elif overall_score >= 70:  return 'Good! Your resume is ATS-friendly with room for minor improvements.'
    elif overall_score >= 60:  return 'Fair. Your resume needs some improvements to be fully ATS-compatible.'
    elif overall_score >= 50:  return 'Below Average. Significant improvements needed for ATS compatibility.'
    else:                      return 'Poor. Your resume requires major revisions to pass ATS screening.'