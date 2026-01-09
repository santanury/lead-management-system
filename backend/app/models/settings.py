from sqlmodel import SQLModel, Field
from typing import Optional

class SettingsBase(SQLModel):
    selected_model: str = Field(default="gemini-2.5-flash")
    auto_routing_enabled: bool = Field(default=True)
    enrichment_enabled: bool = Field(default=True)
    webhook_url: Optional[str] = Field(default=None, description="URL to send analyzed lead data to (e.g. n8n webhook)")

class Settings(SettingsBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
