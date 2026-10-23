from groq import Groq
import json
from core.config import GROQ_API_KEY
import re

GROQ_MODEL="openai/gpt-oss-120b"

_client=None
def _get_client():
    global _client
    if _client is None:
        api_key=GROQ_API_KEY
        if api_key is None:
            raise ValueError("Groq api key is not define")
        _client=Groq(api_key=api_key)
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
    try:
        #clean text remove \uf0b7
        cleaned_text=text.replace('\uf0b7',"")
        #extraction
        json_match=re.search(r'\{.*\}', cleaned_text, re.DOTALL)

        if not json:
            raise ValueError("No JSON object extracted")
        json_string=json_match.group(0)
        parsed_data=json.loads(json_string)
        return parsed_data
    except json.JSONDecodeError as je:
        print("JSON Extraction error")
        return None
    except Exception as e:
        print(f"An Unexpected error occured {e}")
        return None

def parse_resume(raw_text):
    _client=_get_client()
    prompt=RESUME_USER_PROMPT.format(raw_text=raw_text)
    raw_res=_call_llm(_client,system_prompt=RESUME_SYSTEM_PROMPT,user_prompt=prompt)
    result=_try_extract_json(text=raw_res)

    if result is None:
        strict_prompt = (
        "Your previous response was not valid JSON. "
        "Return ONLY the raw JSON object, no markdown, no explanation, no code fences.\n\n"
        + prompt)
        raw_res=_call_llm(_client,system_prompt=RESUME_SYSTEM_PROMPT,user_prompt=prompt)
        result=_try_extract_json(text=raw_res)
        if result is None:
            raise ValueError("Groq gives invalid responces")
    return result
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
        + prompt
    )
        responce=_call_llm(client=_client,system_prompt=JD_SYSTEM_PROMPT,user_prompt=strict_prompt)
        result=_try_extract_json(responce)
        if result is None:
            raise ValueError("Groq returns the unparseble result")
    return result