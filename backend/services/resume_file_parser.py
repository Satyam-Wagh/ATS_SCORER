import io
from backend.core.config import MAX_FILE_SIZE,MAX_FILE_SIZE_MB,SUPPORTED_MIME_TYPES
import pdfplumber
from backend.utils.file_utils import FileParsingError,TextExtractionError
import pdfplumber as pdf
from pdfminer.high_level import extract_text
def validateFile(file):
    #this function is import at frontend
    file_size_bytes=len(file)
    if file_size_bytes>MAX_FILE_SIZE:
        size=file_size_bytes/(1024*1024)
        return False,(f"Please Upload the file in {MAX_FILE_SIZE_MB} MB")
    if file.type not in SUPPORTED_MIME_TYPES:
        return False,f"Invalid File type"
    else:
        return True,""

def _extraction_by_pdfminer(file:bytes):
    #primary function
    text=extract_text(io.BytesIO(file))
    if not text.strip():
        raise TextExtractionError(
            "No text Extracted by pdfminer"
        )
    return text

def _extract_pdf_by_pdfplumber(file:bytes):
    #secondry
    text=""
    with pdfplumber.open(io.BytesIO(file)) as pdf:
        for page in pdf.pages:
            page_text=page.extract_text()
            if page_text:
                text+=page_text+"/n"
    if not text.strip():
        raise TextExtractionError(
            "No text extracted from PdfPlumber"
        )
    return text

#This is main function
def resume_parser(file:bytes):
    try:
        #primary
        text=_extraction_by_pdfminer(file)
    except TextExtractionError as e:
        #secondary
        try:
            text=_extract_pdf_by_pdfplumber(file)
        except TextExtractionError as e:
           raise FileParsingError(
               "An Unexpected Error occurred while processing the file. Please try again and contact to support"
           ) 
    return text