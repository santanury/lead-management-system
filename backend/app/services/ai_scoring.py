from app.models.lead import LeadInput, BANTAnalysis, LeadScore, EnrichmentData, VerificationResult, LeadVerificationStatus
from app.utils.gemini_client import gemini_client
from app.config import settings
import json
import asyncio

class AIScoringService:
    """
    Service for scoring leads using a Micro-Agent architecture (Gemini).
    Splits the evaluation into 3 concurrent tasks to prevent model drift.
    """

    async def score_lead(self, lead_input: LeadInput, enrichment_data: EnrichmentData, verification_result: VerificationResult) -> tuple[BANTAnalysis, LeadScore]:
        """
        Analyzes and scores a lead using multiple concurrent Gemini AI tasks.
        """
        from app.db.database import get_session
        from app.models.settings import Settings
        from sqlmodel import select
        
        with next(get_session()) as session:
            settings_db = session.exec(select(Settings)).first()
            selected_model = settings_db.selected_model if settings_db else "gemini-2.5-flash"

        # 1. Build Prompts
        bant_prompt = self._build_bant_prompt(lead_input, enrichment_data)
        auth_prompt = self._build_auth_prompt(lead_input, enrichment_data, verification_result)
        risk_prompt = self._build_risk_prompt(lead_input, enrichment_data)

        try:
            # 2. Execute concurrently with specific API Keys
            bant_task = gemini_client.generate_json_response(bant_prompt, model_name=selected_model, api_key=settings.google_api_key_bant)
            auth_task = gemini_client.generate_json_response(auth_prompt, model_name=selected_model, api_key=settings.google_api_key_auth)
            risk_task = gemini_client.generate_json_response(risk_prompt, model_name=selected_model, api_key=settings.google_api_key_risk)

            results = await asyncio.gather(bant_task, auth_task, risk_task, return_exceptions=True)

            # Check for catastrophic failures
            for res in results:
                if isinstance(res, Exception):
                    print(f"One or more micro-agents failed: {res}")
                    return self._get_fallback_scoring()

            bant_data, auth_data, risk_data = results

            # 3. Synthesize Results
            bant_analysis = BANTAnalysis(**bant_data.get("bant_analysis", {}))
            
            score_dimensions = {
                "budget_realism": bant_data.get("budget_realism", 0),
                "requirement_clarity": bant_data.get("requirement_clarity", 0),
                "authenticity": auth_data.get("authenticity", 0),
                "authority": auth_data.get("authority", 0),
                "organizational_footprint": auth_data.get("organizational_footprint", 0),
                # Pull intent correctly from verification layer
                 "intent_signals": 100 if verification_result.intent_signal == "Strong" else (60 if verification_result.intent_signal == "Weak" else 20)
            }

            risk_flags = risk_data.get("risk_flags", [])
            follow_up_questions = risk_data.get("follow_up_questions", [])
            explanation = risk_data.get("explanation", "Lead scored via distributed agents.")

            # 4. Calculate Final Score
            final_score, score_breakdown = self._calculate_weighted_score(score_dimensions, risk_flags, verification_result)
            
            lead_score = LeadScore(
                score=final_score,
                category=self._score_to_category(final_score),
                explanation=explanation,
                score_breakdown=score_breakdown,
                risk_flags=risk_flags,
                follow_up_questions=follow_up_questions
            )
            
            return bant_analysis, lead_score

        except Exception as e:
            print(f"Failed to execute or parse AI responses: {e}")
            return self._get_fallback_scoring()

    def _build_bant_prompt(self, lead_input: LeadInput, enrichment_data: EnrichmentData) -> str:
        return f"""
        You are an Expert BANT Analysis Agent. Your goal is strictly to evaluate the B.A.N.T conditions of a sales lead.
        
        **Lead Information:** Name: {lead_input.first_name} {lead_input.last_name} | Company: {lead_input.company_name} | Note: "{lead_input.notes}"
        **Enriched Company Data:** Size: {enrichment_data.company_info.get('size', 'N/A') if enrichment_data.company_info else 'N/A'}

        **Tasks:**
        1. Write a 1-sentence analysis for Budget, Authority, Need, and Timeline based on the note.
        2. Score 'budget_realism' (0-100): Does the implied/stated budget match the company size? (100 if clear/realistic, 50 if vague, 0 if unrealistic).
        3. Score 'requirement_clarity' (0-100): How specific is the request? (100 for specific tech/timeline, 20 for "Hi, info please").

        **Output Format (JSON):**
        {{
            "bant_analysis": {{ "budget": "...", "authority": "...", "need": "...", "timeline": "..." }},
            "budget_realism": <int>,
            "requirement_clarity": <int>
        }}
        """

    def _build_auth_prompt(self, lead_input: LeadInput, enrichment_data: EnrichmentData, verification_result: VerificationResult) -> str:
        return f"""
        You are an Expert Lead Authentication Agent. Evaluate the structural authority and legitimacy of this lead.
        
        **Lead Information:** Name: {lead_input.first_name} {lead_input.last_name} | Company: {lead_input.company_name}
        **Verification Context:** Status: {verification_result.status.value} | Tier: {verification_result.authority_tier.value}
        **Enriched Data:** Industry: {enrichment_data.company_info.get('industry', 'N/A') if enrichment_data.company_info else 'N/A'} | Size: {enrichment_data.company_info.get('size', 'N/A') if enrichment_data.company_info else 'N/A'}

        **Tasks:**
        1. Score 'authenticity' (0-100): 100 if Verified (Decision Maker/Employee), 50 if Unverified, 0 if Fake.
        2. Score 'authority' (0-100): 100 for Tier 1 (CXO), 80 for Tier 2, 50 for Tier 3, 20 for Tier 4.
        3. Score 'organizational_footprint' (0-100): Evaluate company maturity based on Size/Industry inputs. 100 for large/established, 50 for SME, 20 for unknowns.

        **Output Format (JSON):**
        {{
            "authenticity": <int>,
            "authority": <int>,
            "organizational_footprint": <int>
        }}
        """

    def _build_risk_prompt(self, lead_input: LeadInput, enrichment_data: EnrichmentData) -> str:
         return f"""
        You are an Expert Risk Assessment & Strategy Agent.
        
        **Lead Information:** Company: {lead_input.company_name} | Note: "{lead_input.notes}"
        **Enriched Data:** Industry: {enrichment_data.company_info.get('industry', 'N/A') if enrichment_data.company_info else 'N/A'}

        **Tasks:**
        1. Identify any "risk_flags" (List of strings): Look for Industry Mismatch, Vague Requirements, or contradictions. Empty list if none.
        2. Generate 3-5 "follow_up_questions": Strategic questions for a human sales agent to ask to validate the lead.
           - DO NOT ask about "triggers for budget expansion". Focus on validating current request.
        3. Provide an "explanation": A brief, 2-sentence summary of the lead's overall strategic position based on what you read.

        **Output Format (JSON):**
        {{
            "risk_flags": ["..."],
            "follow_up_questions": ["..."],
            "explanation": "..."
        }}
        """

    def _calculate_weighted_score(self, dimensions: dict, risk_flags: list, verification_result: VerificationResult) -> tuple[int, dict]:
        W_AUTHENTICITY = 0.30
        W_AUTHORITY = 0.20
        W_BUDGET = 0.10
        W_CLARITY = 0.10
        W_FOOTPRINT = 0.10
        W_INTENT = 0.20

        s_auth = dimensions.get("authenticity", 0)
        s_auth_tier = dimensions.get("authority", 0)
        s_budget = dimensions.get("budget_realism", 0)
        s_clarity = dimensions.get("requirement_clarity", 0)
        s_footprint = dimensions.get("organizational_footprint", 0)
        s_intent = dimensions.get("intent_signals", 0)

        base_score = (
            (s_auth * W_AUTHENTICITY) +
            (s_auth_tier * W_AUTHORITY) +
            (s_budget * W_BUDGET) +
            (s_clarity * W_CLARITY) +
            (s_footprint * W_FOOTPRINT) +
            (s_intent * W_INTENT)
        )

        penalty = len(risk_flags) * 10
        final_score = base_score - penalty

        if verification_result.status == LeadVerificationStatus.LIKELY_FAKE:
            final_score = 0
            s_auth = 0
        else:
            final_score = max(final_score, 20)

        final_score = int(round(final_score))
        final_score = min(max(final_score, 0), 100)

        breakdown = {
            "Authenticity": s_auth,
            "Authority": s_auth_tier,
            "Budget": s_budget,
            "Clarity": s_clarity,
            "Footprint": s_footprint,
            "Intent": s_intent,
            "RiskPenalty": -penalty
        }

        return final_score, breakdown

    def _score_to_category(self, score: int) -> str:
        if score >= 90: return "Exceptional"
        elif score >= 80: return "High Confidence"
        elif score >= 60: return "Strong"
        elif score >= 40: return "Moderate"
        else: return "Low Confidence"

    def _get_fallback_scoring(self) -> tuple[BANTAnalysis, LeadScore]:
        bant = BANTAnalysis(
            budget="Analysis failed.", authority="Analysis failed.", need="Analysis failed.", timeline="Analysis failed."
        )
        score = LeadScore(
            score=20, category="Unscored", explanation="Could not process lead due to an internal error."
        )
        return bant, score

ai_scoring_service = AIScoringService()
