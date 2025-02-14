from fastapi import APIRouter, UploadFile, File, HTTPException
import asyncio
import json
import os
import tempfile
import subprocess
from google.cloud import speech, storage
from services.transcription_service import transcribe_audio_gcs
from services.upload_service import upload_audio_to_gcs
from models.google_transcription import TranscriptionResponse

router = APIRouter()

# ✅ Sett autentiseringsnøkkelen for Google Cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/saros/Documents/transcription_backend/trancription-test-c13fa390014c.json"

# ✅ Initialiser Google Cloud-klienter
speech_client = speech.SpeechClient()
storage_client = storage.Client()
print("✅ Google Cloud-autentisering OK!")

# 🎵 **Lydkonvertering via Midlertidig Fil**
def convert_audio_to_linear16(audio_bytes):
    """
    Konverterer lyd til LINEAR16 (16kHz mono) ved å lagre den midlertidig og bruke FFmpeg.
    """
    try:
        print("🔄 Konverterer mottatt lyd...")

        # 🚀 Lagre innkommende lyd midlertidig
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_input:
            temp_input.write(audio_bytes)
            temp_input_path = temp_input.name

        temp_output_path = temp_input_path.replace(".webm", ".wav")

        # 🎯 Kjør FFmpeg-konvertering
        ffmpeg_command = [
            "ffmpeg", "-y", "-i", temp_input_path,  # Input-fil
            "-ac", "1", "-ar", "16000", "-f", "wav", temp_output_path  # Output-fil (mono, 16kHz)
        ]

        process = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 🚨 Sjekk om FFmpeg feilet
        if process.returncode != 0:
            print(f"❌ FFmpeg-feil: {process.stderr.decode()}")
            os.remove(temp_input_path)  # Rydd opp midlertidig fil
            return None

        print(f"✅ Lyd konvertert og lagret midlertidig: {temp_output_path}")
        return temp_output_path  # ✅ Returnerer filbanen i stedet for bytes

    except Exception as e:
        print(f"❌ Feil under lydkonvertering: {e}")
        return None


# 🎧 **API-endepunkt for filopplasting og transkripsjon**
@router.post("/upload-file/", response_model=TranscriptionResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Laster opp en lydfil til Google Cloud Storage og transkriberer den.
    """
    try:
        print(f"✅ Mottok fil: {file.filename}")

        # 📥 Les innholdet fra filen
        file_bytes = await file.read()

        # 🔄 Konverter til riktig format
        converted_audio_path = convert_audio_to_linear16(file_bytes)
        if not converted_audio_path:
            raise Exception("Kunne ikke konvertere lydfilen.")

        # 🚀 Last opp til GCS
        gcs_uri = upload_audio_to_gcs(converted_audio_path)  
        if not gcs_uri:
            raise Exception("Opplasting til GCS feilet.")

        # 📝 Transkriber filen
        transcription_result = transcribe_audio_gcs(gcs_uri)  # ✅ Dette returnerer en dictionary

        if isinstance(transcription_result, dict) and "transcription" in transcription_result:
            transcription_text = transcription_result["transcription"]
        else:
            transcription_text = "Feil under transkripsjon"

        print(f"📝 Fullført transkripsjon: {transcription_text}")

        # 🔥 Slett midlertidig fil etter opplasting
        os.remove(converted_audio_path)

        return TranscriptionResponse(
            file_name=file.filename,
            gcs_uri=gcs_uri,
            transcription=transcription_text  # ✅ Nå er det en streng, ikke dictionary
        )
    except Exception as e:
        print(f"❌ Feil under filopplastning: {e}")
        raise HTTPException(status_code=500, detail=str(e))
