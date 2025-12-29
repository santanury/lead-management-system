from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from app.models.lead import LeadInput, AnalyzedLead, Lead, BANTAnalysis, EnrichmentData, LeadScore, RoutingDecision
from app.services.enrichment import enrichment_service
from app.services.ai_scoring import ai_scoring_service
from app.services.routing import routing_service
from app.db.database import get_session

from sqlmodel import Session, select
from typing import List
from app.db.database import get_session

router = APIRouter()

@router.get("/stats")
async def get_stats(session: Session = Depends(get_session)):
    """
    Returns dashboard statistics: total leads, qualified leads, avg score.
    """
    leads = session.exec(select(Lead)).all()
    total = len(leads)
    qualified = len([l for l in leads if l.category == "Hot"])
    avg_score = sum([l.score for l in leads]) / total if total > 0 else 0
    
    # Simple calculation for "New Leads Today" (mock logic for now since we don't have created_at timestamp yet)
    # real implementation would filter by date.
    new_today = len(leads) 

    return {
        "total_leads": total,
        "qualified_leads": qualified,
        "avg_score": round(avg_score, 1),
        "new_leads_today": new_today
    }

@router.get("/", response_model=List[Lead])
async def get_leads(session: Session = Depends(get_session)):
    """
    Fetch all leads from the database.
    """
    return session.exec(select(Lead)).all()

@router.post("/analyze", response_model=AnalyzedLead)
async def analyze_lead(lead_input: LeadInput, session: Session = Depends(get_session)):
    """
    Receives lead data, enriches it, scores it using AI, determines routing, and SAVES to DB.
    """
    # 1. Enrich lead data
    enrichment_data = enrichment_service.enrich_lead(lead_input.company_name, lead_input.email)
    
    if not enrichment_data.email_valid:
        raise HTTPException(status_code=400, detail="Invalid email address provided.")

    # 2. Score the lead using AI
    bant_analysis, lead_score = ai_scoring_service.score_lead(lead_input)

    # 3. Determine routing
    routing_decision = routing_service.route_lead(lead_score)
    
    # 4. Save to Database
    db_lead = Lead(
        first_name=lead_input.first_name,
        last_name=lead_input.last_name,
        email=lead_input.email,
        company_name=lead_input.company_name,
        notes=lead_input.notes,
        email_valid=enrichment_data.email_valid,
        company_info=enrichment_data.company_info,
        budget_analysis=bant_analysis.budget,
        authority_analysis=bant_analysis.authority,
        need_analysis=bant_analysis.need,
        timeline_analysis=bant_analysis.timeline,
        score=lead_score.score,
        category=lead_score.category,
        explanation=lead_score.explanation,
        queue=routing_decision.queue,
        routing_reason=routing_decision.reason
    )
    session.add(db_lead)
    session.commit()
    session.refresh(db_lead)

    # 5. Combine and return the full analysis
    analyzed_lead = AnalyzedLead(
        lead_input=lead_input,
        bant_analysis=bant_analysis,
        enrichment_data=enrichment_data,
        lead_score=lead_score,
        routing_decision=routing_decision
    )
    
    return analyzed_lead
