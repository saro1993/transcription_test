from google.cloud import  speech
import logging
from convert_audio import convert_audio_gcs

logging.basicConfig(level=logging.DEBUG)

BUCKET_NAME = "transcriptionfortest"


def transcribe_audio_gcs(gcs_uri):
    """
    Transkriber en lydfil som er lagret i Google Cloud Storage.
    Støtter automatisk detektering av norsk bokmål, nynorsk og engelsk.
    """
    # 🚀 Først konverter filen til 16kHz mono
    converted_gcs_uri = convert_audio_gcs(gcs_uri)

    if not converted_gcs_uri:
        raise Exception("Kunne ikke konvertere lydfil.")

    # 🚀 Send forespørsel til Google Speech-to-Text
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=converted_gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,  
        language_code="nb-NO",  
        alternative_language_codes=["nn-NO", "en-US"],  
        enable_automatic_punctuation=True,  
        model="latest_long", 
        use_enhanced=True 
    )

    try:
        operation = client.long_running_recognize(config=config, audio=audio)
        response = operation.result()

        transcript = "\n".join([result.alternatives[0].transcript for result in response.results])
        return {"gcs_uri": converted_gcs_uri, "transcription": transcript}

    except Exception as e:
        return {"gcs_uri": converted_gcs_uri, "transcription": f"Feil under transkripsjon: {str(e)}"}
    