from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Grunnmodell
class TranscriptionBase(BaseModel):
    """
    Basemodell for transkripsjoner.
    
    - `file_name`: Navnet på lydfilen
    - `gcs_uri`: Google Cloud Storage URI for filen
    - `transcription`: Selve transkripsjonsteksten (kan være None hvis ikke ferdig transkribert)
    - `created_at`: Tidspunkt for når transkripsjonen ble opprettet
    """
    file_name: str = Field(..., example="audio.wav")
    gcs_uri: str = Field(..., example="gs://my-bucket/audio.wav")
    transcription: Optional[str] = Field(None, example="Dette er en transkribert tekst.")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # TODO: Implementer støtte for status (om transkripsjonen er ferdig eller pågår)
    # status: str = Field(default="pending", example="completed")


# Modell for å opprette en ny transkripsjon
class TranscriptionCreate(TranscriptionBase):
    """
    Modell for å opprette en ny transkripsjon.
    
    - Arver alle felt fra `TranscriptionBase`
    - Kan utvides med flere felt hvis det trengs.
    """
    pass


# Modell for å returnere transkripsjon som API-response
class TranscriptionResponse(TranscriptionBase):
    """
    Response-modell som brukes når en transkripsjon sendes tilbake til klienten.
    
    - `id`: Unik ID for transkripsjonen (kan være None hvis ikke lagret i DB)
    """
    id: Optional[int] = Field(None, example=1)


# TODO: Implementer en modell for listevisning av transkripsjoner
class TranscriptionListResponse(BaseModel):
    """
    Modell for å returnere en liste av transkripsjoner.
    
    - `transcriptions`: En liste av transkripsjonsobjekter
    """
    transcriptions: List[TranscriptionResponse]


# TODO: Implementer en modell for å oppdatere eksisterende transkripsjoner
class TranscriptionUpdate(BaseModel):
    """
    Modell for å oppdatere eksisterende transkripsjoner.
    
    - `transcription`: Kan oppdateres hvis transkripsjonen er endret
    - `status`: Kan oppdateres for å indikere om transkripsjonen er ferdig
    """
    transcription: Optional[str] = None
    # status: Optional[str] = Field(None, example="completed")
