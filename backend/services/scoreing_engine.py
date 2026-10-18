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
    