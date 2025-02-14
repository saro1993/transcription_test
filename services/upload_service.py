from google.cloud import storage
import os

BUCKET_NAME = "transcriptionfortest"

def upload_audio_to_gcs(file_path: str) -> str:
    """
    Laster opp en fil til Google Cloud Storage og returnerer GCS URI.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob_name = f"test/{os.path.basename(file_path)}"  # Bruk filnavnet som blob-name
        blob = bucket.blob(blob_name)

        # 🚀 Last opp filen
        blob.upload_from_filename(file_path)

        gcs_uri = f"gs://{BUCKET_NAME}/{blob_name}"
        print(f"✅ Fil lastet opp til GCS: {gcs_uri}")
        return gcs_uri

    except Exception as e:
        print(f"❌ Feil ved opplasting til GCS: {e}")
        return None
