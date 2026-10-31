from groq import Groq
import json
from core.config import GROQ_API_KEY
import re
import logging

logging.basicConfig(level=logging.INFO,filename="llm_call.log")
GROQ_MODEL="openai/gpt-oss-120b"
logger = logging.getLogger("groq_parser")
_client=None
def _get_client():
    global _client
    if _client is None:
        logger.info("Initializing Groq client singleton...")
        api_key=GROQ_API_KEY
        if api_key is None:
            logger.critical("Initialization failed: GROQ_API_KEY is not defined!")
            raise ValueError("Groq api key is not define")
        _client=Groq(api_key=api_key)
        logger.info("Groq client initialized successfully.")
    return _client

RESUME_SYSTEM_PROMPT = (
    "You are a resume parser. Extract information from the resume "
    "and return ONLY a valid JSON object. No explanation, no markdown."
)

RESUME_USER_PROMPT = """Extract the following from this resume and return as JSON:
{{
  "name": "full name",
  "email": "email address",
  "phone": "phone number",
  "linkedin": "LinkedIn URL if present, otherwise null",
  "github": "GitHub URL if present, otherwise null",
  "professional_summary": "the full text of the Summary, Profile, About Me, Objective, or Professional Summary section at the top of the resume. Copy the ENTIRE paragraph exactly as written. If no such section exists, return an empty string.",
  "skills": ["list", "of", "skills"],
  "experience": [
    {{
      "job_title": "",
      "company": "",
      "start_date": "",
      "end_date": "",
      "duration_months": 0,
      "description": ""
    }}
  ],
  "education": [
    {{
      "degree": "",
      "institution": "",
      "year": ""
    }}
  ],
  "certifications": ["list of certifications"],
  "projects": [
    {{
      "title": "project name",
      "description": "what the project does and how it was built",
      "technologies": ["tech", "used"]
    }}
  ],
  "action_verbs": ["strong action verbs used in bullet points, e.g. developed, implemented, designed"],
  "keywords": ["important keywords and phrases from the resume for ATS matching"]
}}

Important instructions:
- For duration_months, calculate the number of months between start_date and end_date. If end_date is "Present" or "Current", calculate from start_date to now.
- For skills, extract ALL technical and soft skills mentioned anywhere in the resume.
- For action_verbs, find verbs that start bullet points or describe achievements.
- For keywords, extract noun phrases and technical terms relevant to ATS matching.
- Return ONLY valid JSON. No markdown code fences, no explanation.

Resume Text:
{raw_text}"""

def _call_llm(client:Groq,system_prompt:str,user_prompt:str)->str:
    logger.info(f"Dispatching API call to model: {GROQ_MODEL}")
    responce=client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role":"system","content":system_prompt},
                  {
                      "role":"user",
                      "content":user_prompt
                  }],
        temperature=0.0,
        max_tokens=4096
    )
    return responce.choices[0].message.content.strip()

def _try_extract_json(text):
    logger.info("Attempting regex JSON extraction block...")
    try:
        #clean text remove \uf0b7
        cleaned_text=text.replace('\uf0b7',"")
        #extraction
        json_match=re.search(r'\{.*\}', cleaned_text, re.DOTALL)

        if not json_match:
            logger.warning("Regex parsing mismatch: No valid opening/closing structural brackets found.")
            raise ValueError("No JSON object extracted")
        json_string=json_match.group(0)
        logger.debug(f"Extracted substring slice for target parsing: {json_string[:100]}...")
        parsed_data=json.loads(json_string)
        logger.info("JSON successfully deserialised.")
        return parsed_data
    except json.JSONDecodeError as je:
        logger.error(f"JSON parsing structural error: Content is syntactically invalid code. Error: {str(je)}")
        logger.debug(f"Failed block snippet: \n{text[:300]}")
        return None
    except Exception as e:
        logger.error(f"An unexpected parsing exception occurred: {str(e)}", exc_info=True)
        return None
def _validate_resume_result(result: dict) -> dict:
    logger.info("Beginning execution schema constraint checks...")
    defaults = {
        "name": "",
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
        "professional_summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "certifications": [],
        "projects": [],
        "action_verbs": [],
        "keywords": [],
    }
    for key, default in defaults.items():
        if key not in result or result[key] is None:
            result[key] = default
            
        # Ensure list fields are actually lists
        if isinstance(default, list) and not isinstance(result[key], list):
            result[key] = default

    #Validate experience entries
    for exp in result.get("experience", []):
        if not isinstance(exp, dict):
            continue
        exp.setdefault("job_title", "")
        exp.setdefault("company", "")
        exp.setdefault("start_date", "")
        exp.setdefault("end_date", "")
        exp.setdefault("duration_months", 0)
        exp.setdefault("description", "")
        #Ensure duration_months is an int
        try:
            exp["duration_months"] = int(exp["duration_months"])
        except (ValueError, TypeError):
            exp["duration_months"] = 0

    #Validate project entries
    for proj in result.get("projects", []):
        if not isinstance(proj, dict):
            continue
        proj.setdefault("title", "")
        proj.setdefault("description", "")
        proj.setdefault("technologies", [])
    logger.info("Schema integrity checks successfully completed.")
    logger.info(f"final result {result}")
    return result
def parse_resume(raw_text):
    logger.info("--- START RESUME PARSING WORKFLOW ---")
    _client=_get_client()
    prompt=RESUME_USER_PROMPT.format(raw_text=raw_text)
    raw_res=_call_llm(_client,system_prompt=RESUME_SYSTEM_PROMPT,user_prompt=prompt)
    #first attempt
    logger.info("Executing Primary Inference Pass (Attempt #1)...")
    result=_try_extract_json(text=raw_res)

    if result is not None:
        logger.info("Primary pass successful. Commencing schema evaluation...")
        return _validate_resume_result(result=result)
    #second attempt
    logger.warning("Primary pass failed to return parseable JSON. Engaging Self-Correction Pipeline (Attempt #2)...")
    strict_prompt = (
        "Your previous response was not valid JSON. "
        "Return ONLY the raw JSON object, no markdown, no explanation, no code fences.\n\n"
        + prompt)
    raw_res=_call_llm(_client,system_prompt=RESUME_SYSTEM_PROMPT,user_prompt=strict_prompt)
    result=_try_extract_json(text=raw_res)
    if result is not None:
        logger.info("second attempt is sucessfully completed. result is passing to schema validation")
        return _validate_resume_result(result=result)
    raise ValueError( f"Groq returned unparseable response after retry. Raw response:\n{raw_res[:500]}")
#JD parsing
JD_SYSTEM_PROMPT = (
    "You are a job description parser. Extract information and "
    "return ONLY a valid JSON object. No explanation, no markdown."
)

JD_USER_PROMPT = """Extract the following from this job description and return as JSON:
{{
  "job_title": "",
  "required_skills": ["list of must-have skills"],
  "preferred_skills": ["list of nice-to-have skills"],
  "experience_required": "",
  "education_required": "",
  "key_responsibilities": ["list of responsibilities"],
  "keywords": ["important keywords and phrases for ATS matching"]
}}
Important instructions:
- required_skills: skills explicitly stated as required or must-have.
- preferred_skills: skills stated as preferred, nice-to-have, or bonus.
- keywords: extract ALL important terms an ATS system would match against,
  including skills, technologies, certifications, and domain terms.
- Return ONLY valid JSON. No markdown code fences, no explanation.
Job Description Text:
{raw_text}"""
def parse_jd(raw_text):
    _client=_get_client()
    jd_prompt=JD_USER_PROMPT.format(raw_text=raw_text)
    responce=_call_llm(client=_client,system_prompt=JD_SYSTEM_PROMPT,user_prompt=jd_prompt)
    result=_try_extract_json(responce)
    if result is None:
        strict_prompt = (
        "Your previous response was not valid JSON. "
        "Return ONLY the raw JSON object, no markdown, no explanation, no code fences.\n\n"
        + jd_prompt
    )
        responce=_call_llm(client=_client,system_prompt=JD_SYSTEM_PROMPT,user_prompt=strict_prompt)
        result=_try_extract_json(responce)
        if result is None:
            raise ValueError("Groq returns the unparseble result")
    return result