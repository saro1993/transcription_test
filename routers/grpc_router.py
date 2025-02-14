import grpc
from fastapi import APIRouter, File, UploadFile, HTTPException
import audio_streaming_pb2
import audio_streaming_pb2_grpc
from fastapi.responses import JSONResponse

router = APIRouter()

# 📌 Prøv å koble til gRPC-serveren
print("🔄 Koble til gRPC-server på 127.0.0.1:50051...")
channel = grpc.insecure_channel("127.0.0.1:50051")

try:
    grpc_client = audio_streaming_pb2_grpc.TranscriptionServiceStub(channel)
    print("✅ Tilkoblet til gRPC-server!")
except Exception as e:
    print(f"❌ Kunne ikke koble til gRPC-server: {str(e)}")

@router.post("/transcribe/live", tags=["grpc"])
async def transcribe_live(file: UploadFile = File(...)):
    """
    1️⃣ Mottar lyddata fra frontend
    2️⃣ Sender lydstrøm til gRPC-serveren
    3️⃣ Returnerer transkripsjon til frontend
    """
    try:
        audio_data = await file.read()

        print(f"📤 Sender {len(audio_data)} bytes lyd til gRPC-serveren...")

        # Lag gRPC request med lyddata
        request = audio_streaming_pb2.AudioRequest(audio_chunk=audio_data)
        print(request)

        # Send til gRPC og få svar
        response = grpc_client.Transcribe(iter([request]))
        print(response)

        transcript = []
        for res in response:
            transcript.append(res.text)
            print(transcript)
            print(f"📝 Mottatt transkripsjon: {res.text}")

        return {"transcription": " ".join(transcript)}

    except grpc.RpcError as e:
        print(f"❌ Feil i gRPC-transkripsjon: {e.details()}")
        raise HTTPException(status_code=500, detail=e.details())

    except Exception as e:
        print(f"❌ Generell feil i transkripsjon: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
