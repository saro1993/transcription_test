from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gpt_api_secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
