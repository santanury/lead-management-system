from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.settings import Settings

router = APIRouter()

from typing import List
from pydantic import BaseModel
from app.models.settings import Settings, SettingsBase

# Extend the database model for the API response
class SettingsResponse(SettingsBase):
    id: int
    available_models: List[dict]

@router.get("/settings", response_model=SettingsResponse)
async def get_settings(session: Session = Depends(get_session)):
    settings_db = session.exec(select(Settings)).first()
    if not settings_db:
        # Create default settings if not exists
        settings_db = Settings()
        session.add(settings_db)
        session.commit()
        session.refresh(settings_db)
    
    # Define available models here (or fetch from a config/service)
    models = [
        {"id": "gemini-2.5-flash", "name": "Gemini 1.5 Flash (Fast & Cheap)"},
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro (Smart & Capable)"},
    ]
    
    # Convert SQLModel to dict and add extra field
    response_data = settings_db.model_dump()
    response_data["available_models"] = models
    
    return response_data

@router.put("/settings", response_model=Settings)
async def update_settings(settings: Settings, session: Session = Depends(get_session)):
    settings_db = session.exec(select(Settings)).first()
    if not settings_db:
        settings_db = Settings()
        session.add(settings_db)
    
    settings_db.selected_model = settings.selected_model
    settings_db.auto_routing_enabled = settings.auto_routing_enabled
    settings_db.enrichment_enabled = settings.enrichment_enabled
    
    session.add(settings_db)
    session.commit()
    session.refresh(settings_db)
    return settings_db
