from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    google_api_key: str
    database_url: str

    class Config:
        env_file = ".env"
        env_prefix = "" # No prefix for environment variables

settings = Settings()
