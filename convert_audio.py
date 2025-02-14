import subprocess
import os
import platform
from google.cloud import storage

BUCKET_NAME = "transcriptionfortest"

def convert_audio_gcs(gcs_uri: str, target_sample_rate=16000, target_channels=1):
    """
    Laster ned en lydfil fra Google Cloud Storage, konverterer den til 16kHz mono og laster den opp igjen.
    Håndterer riktig filsti for både Windows og Linux.
    """
    client = storage.Client()
    
    # 🔹 Håndter riktig temp-mappe for Windows/Linux
    temp_dir = "/tmp" if platform.system() != "Windows" else os.environ.get("TEMP", "C:\\Temp")
    
    # 🔹 Ekstraher filnavn fra GCS URI
    file_name = gcs_uri.split("/")[-1]
    local_input_path = os.path.join(temp_dir, file_name)
    local_output_path = os.path.join(temp_dir, f"converted_{file_name}")

    try:
        # 🚀 Sjekk at filen lastes ned før vi konverterer
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"test/{file_name}")

        if not blob.exists():
            print(f"❌ Filen {gcs_uri} finnes ikke i GCS!")
            return None

        blob.download_to_filename(local_input_path)
        print(f"✅ Lydfil lastet ned til: {local_input_path}")

        # 🚀 Sjekk at filen faktisk ble lastet ned
        if not os.path.exists(local_input_path):
            raise FileNotFoundError(f"Filen ble ikke funnet etter nedlasting: {local_input_path}")

        # 🚀 Konverter filen med FFmpeg
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", local_input_path,
            "-ac", str(target_channels),
            "-ar", str(target_sample_rate),
            "-f", "wav",
            local_output_path
        ]

        subprocess.run(ffmpeg_cmd, check=True)
        print(f"✅ Fil konvertert: {local_output_path}")

        # 🚀 Last opp den konverterte filen til GCS
        converted_blob = bucket.blob(f"test/converted_{file_name}")
        converted_blob.upload_from_filename(local_output_path)
        print(f"✅ Konvertert fil lastet opp: gs://{BUCKET_NAME}/test/converted_{file_name}")

        # Returnerer GCS URI til den konverterte filen
        return f"gs://{BUCKET_NAME}/test/converted_{file_name}"

    except Exception as e:
        print(f"❌ Feil under konvertering: {e}")
        return None
