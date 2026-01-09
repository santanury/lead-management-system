from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from app.models.lead import LeadInput, AnalyzedLead, Lead, BANTAnalysis, EnrichmentData, LeadScore, RoutingDecision
from app.services.enrichment import enrichment_service
from app.services.ai_scoring import ai_scoring_service
from app.services.routing import routing_service
from app.services.verification import verification_service
from app.utils.webhook_client import send_webhook
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
    
    # Real "New Leads Today" calculation
    today = datetime.utcnow().date()
    new_today = len([l for l in leads if l.created_at and l.created_at.date() == today]) 

    # Chart data: Leads by Category
    categories = {"Hot": 0, "Warm": 0, "Cold": 0}
    for l in leads:
        if l.category in categories:
            categories[l.category] += 1
        else:
            # Handle standard "Warm" or others if logic changes
            categories["Warm"] += 1

    chart_data = [
        {"name": "Hot", "leads": categories["Hot"]},
        {"name": "Warm", "leads": categories["Warm"]},
        {"name": "Cold", "leads": categories["Cold"]},
    ]

    return {
        "total_leads": total,
        "qualified_leads": qualified,
        "avg_score": round(avg_score, 1),
        "new_leads_today": new_today,
        "leads_by_category": chart_data
    }

@router.get("/", response_model=List[Lead])
async def get_leads(session: Session = Depends(get_session)):
    """
    Fetch all leads from the database.
    """
    return session.exec(select(Lead)).all()

from app.models.settings import Settings

@router.post("/analyze", response_model=AnalyzedLead)
async def analyze_lead(lead_input: LeadInput, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    """
    Receives lead data, enriches it, scores it using AI, determines routing, and SAVES to DB.
    """
    try:
        # 0. Check Settings
        settings_db = session.exec(select(Settings)).first()
        enrichment_enabled = settings_db.enrichment_enabled if settings_db else True

        # 1. Enrich lead data
        if enrichment_enabled:
            enrichment_data = enrichment_service.enrich_lead(lead_input.company_name, lead_input.email)
        else:
            # Create empty enrichment data if disabled
            enrichment_data = EnrichmentData(
                company_info=None,
                email_valid=True # Assume valid if we skip verification to not block the flow
            )
        
        if not enrichment_data.email_valid:
            raise HTTPException(status_code=400, detail="Invalid email address provided.")

        # 2. Verify Lead (Agentic Verification)
        verification_result = verification_service.verify_lead(lead_input, enrichment_data)

        # 3. Score the lead using AI (now aware of verification)
        bant_analysis, lead_score = ai_scoring_service.score_lead(lead_input, enrichment_data, verification_result)

        # 4. Determine routing
        routing_decision = routing_service.route_lead(lead_score)
        
        # 5. Save to Database
        db_lead = Lead(
            first_name=lead_input.first_name,
            last_name=lead_input.last_name,
            email=lead_input.email,
            company_name=lead_input.company_name,
            notes=lead_input.notes,
            email_valid=enrichment_data.email_valid,
            company_info=enrichment_data.company_info,
            company_logo_url=enrichment_data.company_logo_url,
            profile_image_url=enrichment_data.profile_image_url,
            budget_analysis=bant_analysis.budget,
            authority_analysis=bant_analysis.authority,
            need_analysis=bant_analysis.need,
            timeline_analysis=bant_analysis.timeline,
            score=lead_score.score,
            category=lead_score.category,
            explanation=lead_score.explanation,
            # New Verification Fields
            verification_status=verification_result.status.value,
            verification_score=verification_result.score,
            authority_tier=verification_result.authority_tier.value,
            identity_verified=verification_result.identity_verified,
            employment_verified=verification_result.employment_verified,
            verification_reason=verification_result.reason,
            intent_signal=verification_result.intent_signal,
            intent_evidence=verification_result.intent_evidence,
            score_breakdown=lead_score.score_breakdown,
            risk_flags=lead_score.risk_flags,
            follow_up_questions=lead_score.follow_up_questions,
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
            routing_decision=routing_decision,
            verification_result=verification_result
        )

        # 6. Trigger Outgoing Webhook (if configured)
        if settings_db and settings_db.webhook_url:
            # We send the full analyzed payload
            background_tasks.add_task(send_webhook, settings_db.webhook_url, analyzed_lead)
        
        return analyzed_lead
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "Rate Limit" in error_msg:
             raise HTTPException(status_code=429, detail="API Rate Limit Exceeded. Please wait a moment and try again.")

        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

@router.delete("/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, session: Session = Depends(get_session)):
    """
    Delete a lead by ID.
    """
    lead = session.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    session.delete(lead)
    session.commit()
    return None




