import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    _ENV_PATH=Path(__file__).resolve().parents[2]/'.env'
    load_dotenv(_ENV_PATH)
except ImportError:
    pass

#api meta data
APP_TITLE="ATS RESUME ANYLYZER"
APP_DESCRIPATION="anylise the resume using nlp+ml"
APP_VERSION="1.0.0"

ALLOWED_ORIGINS=[
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173"
]

#file
MAX_FILE_SIZE_MB=5
MAX_FILE_SIZE=MAX_FILE_SIZE_MB*1024*1024

#supported mime types

SUPPORTED_MIME_TYPES={
     'application/pdf': 'pdf',
}


SUPPORTED_EXTENTIONS={".pdf"}#we deals with only pdf

SPACY_MODEL_PRIMARY="en_core_web_md" #better accuracy
SPACY_MODEL_SECONDARY='"en_core_web_sm' 
SENTENCE_TRANSFORMER_MODEL = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")

JD_SEMENTIC_WEIGHT=0.4
JD_KEYWORD_WEIGHT=0.6

#GROQ_API_KEY=os.getenv("GROQ_API_KEY","")