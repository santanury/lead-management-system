from sqlmodel import SQLModel, Field, Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime
from sqlalchemy import JSON, Column

# --- API Models (Pydantic/SQLModel without table) ---

class LeadInput(SQLModel):
    first_name: str
    last_name: str
    email: EmailStr
    company_name: str
    notes: str = Field(..., description="Lead's notes, inquiry, or message from a form.")

class BANTAnalysis(BaseModel):
    budget: str = Field(..., description="Analysis of the lead's budget.")
    authority: str = Field(..., description="Analysis of the lead's decision-making authority.")
    need: str = Field(..., description="Analysis of the lead's need for the product/service.")
    timeline: str = Field(..., description="Analysis of the lead's timeline for purchase.")

class EnrichmentData(BaseModel):
    company_info: Optional[dict] = Field(None, description="Enriched information about the company.")
    email_valid: bool = Field(True, description="Whether the email address is valid.")

class LeadScore(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Numeric score from 0-100.")
    category: str = Field(..., description="Category: Hot, Warm, or Cold.")
    explanation: str = Field(..., description="AI-generated explanation for the score.")

class RoutingDecision(BaseModel):
    queue: str = Field(..., description="The queue the lead is routed to: Sales, Presales, or Nurture.")
    reason: str = Field(..., description="Reason for the routing decision.")

class AnalyzedLead(BaseModel):
    lead_input: LeadInput
    bant_analysis: BANTAnalysis
    enrichment_data: EnrichmentData
    lead_score: LeadScore
    routing_decision: RoutingDecision

# --- Database Model ---

class Lead(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Input
    first_name: str
    last_name: str
    email: str
    company_name: str
    notes: str

    # Enrichment
    email_valid: bool
    company_info: Optional[Dict] = Field(default=None, sa_column=Column(JSON))

    # BANT
    budget_analysis: str
    authority_analysis: str
    need_analysis: str
    timeline_analysis: str

    # Score
    score: int
    category: str
    explanation: str

    # Routing
    queue: str
    routing_reason: str

    # Meta
    created_at: datetime = Field(default_factory=datetime.utcnow)

