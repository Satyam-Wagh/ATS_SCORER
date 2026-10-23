from fastapi import FastAPI
from api.routes import router
from core.config import APP_TITLE,APP_DESCRIPATION,APP_VERSION,SENTENCE_TRANSFORMER_MODEL,SPACY_MODEL_PRIMARY,SPACY_MODEL_SECONDARY
from contextlib import asynccontextmanager
from pathlib import Path
BASE_DIR=Path(__file__).parent
model_path=str(BASE_DIR/"models"/"fine-tune")
@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Process start.....")
    import spacy
    try:
        app.state.nlp=spacy.load(name=SPACY_MODEL_PRIMARY)
        print("Primary spacy model loads successfully..")
    except OSError:
        app.state.nlp=spacy.load(name=SPACY_MODEL_SECONDARY)
        print("Secondary spacy model loads successfully..")

    #load sentence transformer
    from sentence_transformers import SentenceTransformer
    app.state.embedder=SentenceTransformer(model_path)
    print("Load the sentence transformer")
    yield


app=FastAPI(title=APP_TITLE,description=APP_DESCRIPATION,version=APP_VERSION,
          lifespan=lifespan
           )
app.include_router(router=router)

@app.get("/")
def hellow():
    return "Welcome"
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'main:app', # This tells Uvicorn to look inside backend/main.py for 'app'
        reload = True, 
    )