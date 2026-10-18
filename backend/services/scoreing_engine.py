import re
import spacy

ZIP_CODE_PATTERN = r'\b\d{5}(?:-\d{4})?\b'

STREET_ADDRESS_PATTERN = (
    r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+'
    r'(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl)\b'
)

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