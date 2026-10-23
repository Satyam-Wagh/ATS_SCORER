#we skip analyze_skills_gap
from utils.matching import fuzzy_match_keywords,normalize_skill
import numpy as np
from sentence_transformers import SentenceTransformer
import spacy
def calculate_sementic_similarity(resume_text:str,jd_text:str,embedder:SentenceTransformer):
    resume_emd=embedder.encode(resume_text)
    jd_emd=embedder.encode(jd_text)
    sementic_similarity=np.dot(resume_emd,jd_emd)/(np.linalg.norm(resume_emd)*np.linalg.norm(jd_emd))
    return float(np.clip(sementic_similarity,0.0,1.0))

def Identify_match_miss_keywords(resume_keywords,jd_keywords):
    result=fuzzy_match_keywords(resume_keywords,jd_keywords)
    return result

def calculate_match_percentage(
    match_keywords:list,
    jd_keywords: list[str],
    semantic_similarity: float,
) -> float:
    if not jd_keywords:
        return 0.0
    keyword_overlap = len(match_keywords) / len(jd_keywords)
    match_pct = (keyword_overlap * 0.6 + semantic_similarity * 0.4) * 100
    return float(np.clip(match_pct, 0.0, 100.0))

def compare_resume_with_jd(
        resume_text:str,
        resume_keyword:list,
        jd_text:str,
        jd_keywords:list,
        embedder:SentenceTransformer):
    sementic_similarity=calculate_sementic_similarity(resume_text,jd_text)
    match_miss_words=Identify_match_miss_keywords(resume_text,jd_text)
    match_words=match_miss_words["matched"]
    miss_word=match_miss_words["missing"]
    match_per=calculate_match_percentage(match_words,jd_keywords,sementic_similarity)

    return {
        "match_percentege":match_per,
        "semantic_similarity":sementic_similarity,
        "match_words":match_words,
        "miss_word":miss_word   
    }