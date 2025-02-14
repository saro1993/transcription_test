from fastapi import FastAPI, UploadFile, File, HTTPException
from routers.transcription import router as transcription_router
from routers.grpc_router import router as grpc_router
from fastapi.middleware.cors import CORSMiddleware
from services.transcription_service import transcribe_audio_gcs
from services.upload_service import upload_audio_to_gcs
import grpc_server
import threading
from models.bert_model import BERTModel as bert_model
from pydantic import BaseModel
import openai
from dotenv import load_dotenv
import os
import logging
from transformers import logging


# Sett loggnivået for transformers til error for å undertrykke advarsler
logging.set_verbosity_error()

class RapportRequest(BaseModel):
    text: str

app = FastAPI()
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

load_dotenv()

api_key = os.getenv("GPT_API_SECRET_KEY")
if not api_key:
    raise ValueError("GPT_API_SECRET_KEY er ikke satt i miljøvariablene eller .env-filen.")
openai.api_key = api_key

# 🌍 CORS-støtte for API og gRPC
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    grpc_thread = threading.Thread(target=grpc_server.serve)
    grpc_thread.start()

# 🛠 Registrer API-endepunktene
app.include_router(transcription_router, prefix="/api/v1", tags=["transcription"])
app.include_router(grpc_router, prefix="/api/v1", tags=["grpc"])

# ✅ API-endepunkt for filopplastning og transkripsjon
@app.post("/api/v1/upload-file/", tags=["transcription"])
async def upload_and_transcribe(file: UploadFile = File(...)):
    """
    1️⃣ Laster opp fil til GCS.
    2️⃣ Transkriberer filen med Google Speech-to-Text API.
    3️⃣ Returnerer transkripsjonen.
    """
    try:
        gcs_uri = await upload_audio_to_gcs(file.file)
        print(f"✅ Fil lastet opp til GCS: {gcs_uri}")

        transcript = await transcribe_audio_gcs(gcs_uri)
        print(f"✅ Transkripsjon fullført!")

        return {"gcs_uri": gcs_uri, "transcription": transcript}

    except Exception as e:
        print(f"❌ Feil under prosessering: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Funksjon for å klassifisere tekst ved hjelp av BERT-modellen
async def classify_text_api(text: str):
    bert_instance = bert_model()
    try:
        classification = bert_instance.classify_text(text).tolist()
        return {"classification": classification}
    except Exception as e:
        print(f"❌ Feil under klassifisering: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

system_message = (
"Hei! du er en AI-assistent som kan hjelpe med å generere en rapport basert på teksten du får."
"Du skal lage titell , innledning, hoveddel og konklusjon i rapporten."
"Du skal være objektiv og nøytral i rapporten."
"Du skal skrive så mye som mulig, samtidig som du holder deg til temaet."
"Du skal være saklig og informativ i rapporten."
)

# Funksjon for å generere en rapport ved hjelp av GPT-modellen
async def generate_rapport_api(text: str):
    try:
        # Send forespørselen til GPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": text},
            ]
        )
        # Hent svaret fra GPT
        gpt_response = response['choices'][0]['message']['content']
        # Lagre svaret i et format slik at frontenden kan vise det
        with open("rapport.txt", "w") as file:
            file.write(gpt_response)
        return {"rapport": gpt_response} if gpt_response else {"rapport": "Kunne ikke generere rapport."}
    except Exception as e:
        print(f"❌ Feil under generering av rapport: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# sende the final rapport to the client
@app.post("/api/v1/generate-rapport/", tags=["transcription"])
async def generate_rapport(rapport_request: RapportRequest):
    try:
        classification = await classify_text_api(rapport_request.text)
        print(f"✅ Klassifisering fullført!", classification)
        rapport = await generate_rapport_api(rapport_request.text)
        print(f"✅ Rapport generert!", rapport)
        return {"classification": classification, "rapport": rapport}
    except Exception as e:
        print(f"❌ Feil under rapport generering: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", tags=["health"])
def health_check():
    return {"message": "API is running"}
