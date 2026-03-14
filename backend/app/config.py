from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    google_api_key: str
    database_url: str
    
    # Task-Specific API Keys (Defaults to google_api_key if not set)
    google_api_key_bant: Optional[str] = None
    google_api_key_auth: Optional[str] = None
    google_api_key_risk: Optional[str] = None
    google_api_key_identity: Optional[str] = None
    google_api_key_intent: Optional[str] = None

    # n8n Webhook URL
    n8n_webhook_url: Optional[str] = None

    class Config:
        env_file = ".env"
        env_prefix = "" # No prefix for environment variables

settings = Settings()

# Post-init fallback logic
if not settings.google_api_key_bant: settings.google_api_key_bant = settings.google_api_key
if not settings.google_api_key_auth: settings.google_api_key_auth = settings.google_api_key
if not settings.google_api_key_risk: settings.google_api_key_risk = settings.google_api_key
if not settings.google_api_key_identity: settings.google_api_key_identity = settings.google_api_key
if not settings.google_api_key_intent: settings.google_api_key_intent = settings.google_api_key
