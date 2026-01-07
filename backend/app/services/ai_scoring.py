from app.models.lead import LeadInput, BANTAnalysis, LeadScore, EnrichmentData, VerificationResult, LeadVerificationStatus
from app.utils.gemini_client import gemini_client
import json

class AIScoringService:
    """
    Service for scoring leads using AI (Gemini).
    Now implements the FULL Multi-Factor Scoring Framework.
    """

    def score_lead(self, lead_input: LeadInput, enrichment_data: EnrichmentData, verification_result: VerificationResult) -> (BANTAnalysis, LeadScore):
        """
        Analyzes and scores a lead using the Gemini AI model.
        """
        # Fetch selected model from DB
        from app.db.database import get_session
        from app.models.settings import Settings
        from sqlmodel import select
        
        with next(get_session()) as session:
            settings_db = session.exec(select(Settings)).first()
            selected_model = settings_db.selected_model if settings_db else "gemini-2.5-flash"

        prompt = self._build_prompt(lead_input, enrichment_data, verification_result)
        
        try:
            # Get the structured JSON response from Gemini
            ai_response = gemini_client.generate_json_response(prompt, model_name=selected_model)
            
            # Parse the AI response into our Pydantic models
            bant_analysis = BANTAnalysis(**ai_response.get("bant_analysis", {}))
            
            # Extract the AI's dimensional analysis
            score_dimensions = ai_response.get("score_dimensions", {})
            risk_flags = ai_response.get("risk_flags", [])
            explanation = ai_response.get("explanation", "No explanation provided.")

            # Calculate the final weighted score Python-side for precision
            final_score, score_breakdown = self._calculate_weighted_score(score_dimensions, risk_flags, verification_result)
            
            lead_score = LeadScore(
                score=final_score,
                category=self._score_to_category(final_score),
                explanation=explanation,
                score_breakdown=score_breakdown,
                risk_flags=risk_flags
            )
            
            return bant_analysis, lead_score

        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"Failed to parse AI response: {e}")
            return self._get_fallback_scoring()

    def _build_prompt(self, lead_input: LeadInput, enrichment_data: EnrichmentData, verification_result: VerificationResult) -> str:
        return f"""
        You are an Expert Lead Qualification Agent. Your goal is to score sales leads using a STRICT Multi-Factor Scoring Framework.
        
        **Lead Information:**
        - Name: {lead_input.first_name} {lead_input.last_name}
        - Company: {lead_input.company_name}
        - Email: {lead_input.email}
        - Message: "{lead_input.notes}"

        **Verification Context (Pre-Computed):**
        - Status: {verification_result.status.value}
        - Identity Verified: {verification_result.identity_verified}
        - Employment Verified: {verification_result.employment_verified}
        - Authority Tier: {verification_result.authority_tier.value}
        - Intent Signal: {verification_result.intent_signal}
        - Intent Evidence: {verification_result.intent_evidence}

        **Enriched Company Data:**
        - Industry: {enrichment_data.company_info.get('industry', 'N/A') if enrichment_data.company_info else 'N/A'}
        - Size: {enrichment_data.company_info.get('size', 'N/A') if enrichment_data.company_info else 'N/A'}
        - Website: {enrichment_data.company_info.get('website', 'N/A') if enrichment_data.company_info else 'N/A'}

        **SCORING INSTRUCTIONS (Multi-Factor Model):**
        Evaluate the lead on these 6 dimensions (0-100 scale for each):

        1. **Authenticity (Weight: 30%)**: 
           - Is the person real? Do they work there? 
           - Used Pre-computed Verification Status.
           - Score 100 if "Verified Decision Maker" or "Verified Employee".
           - Score 50 if "Unverified" but looks plausible (not obviously fake).
           - Score 0 ONLY if "Likely Fake".

        2. **Authority (Weight: 20%)**:
           - Do they have buying power? 
           - 100 for Tier 1 (CXO), 80 for Tier 2 (Director/VP), 50 for Tier 3 (Manager), 20 for Individual Contributor.

        3. **Budget Realism (Weight: 10%)**:
           - Does the implied/stated budget match the company size? 
           - High score (80-100) if budget is clear and realistic.
           - Mid score (50) if budget is realistic but vague.
           - Low score (0-30) if unrealistic (e.g. $1M from a 1-person shop or $500 from a big corp).

        4. **Requirement Clarity (Weight: 10%)**:
           - How specific is the request? 
           - High score (80-100) for specific details (tech stack, timeline). 
           - Low score (20-40) for "Hi, info please".

        5. **Organizational Footprint (Weight: 10%)**:
           - Company maturity/size. 
           - High score (80-100) for established/large companies. 
           - Mid score (50-70) for legitimate SMEs. 
           - Low score (20-40) for unknowns/startups.

        6. **Intent Signals (Weight: 20%)**:
           - Is there evidence of need? 
           - Used Pre-computed Intent Signal.
           - Score 100 for "Strong Signal" (News/Reports).
           - Score 60 for "Weak/Inferred Signal" (Logical need + Industry match).
           - Score 20 for "No Signal".

        **Risk Factors (Negative Modifiers)**:
        Identify any specific risks that should LOWER the score:
        - "Industry Mismatch" (e.g. Grocery asking for Cloud without context).
        - "Vague Requirements" (High urgency but no details).
        - "Contradictory Info".

        **Output Format (JSON):**
        {{
            "bant_analysis": {{ "budget": "...", "authority": "...", "need": "...", "timeline": "..." }},
            "score_dimensions": {{
                "authenticity": <int 0-100>,
                "authority": <int 0-100>,
                "budget_realism": <int 0-100>,
                "requirement_clarity": <int 0-100>,
                "organizational_footprint": <int 0-100>,
                "intent_signals": <int 0-100>
            }},
            "risk_flags": ["List", "of", "risks", "found"],
            "explanation": "Brief summary of why this score was given."
        }}
        """

    def _calculate_weighted_score(self, dimensions: dict, risk_flags: list, verification_result: VerificationResult) -> (int, dict):
        """
        Calculates the weighted final score based on the 6 dimensions and applies modifiers.
        """
        # Weights
        W_AUTHENTICITY = 0.30
        W_AUTHORITY = 0.20
        W_BUDGET = 0.10
        W_CLARITY = 0.10
        W_FOOTPRINT = 0.10
        W_INTENT = 0.20

        # Extract scores (safely default to 0 if missing)
        s_auth = dimensions.get("authenticity", 0)
        s_auth_tier = dimensions.get("authority", 0)
        s_budget = dimensions.get("budget_realism", 0)
        s_clarity = dimensions.get("requirement_clarity", 0)
        s_footprint = dimensions.get("organizational_footprint", 0)
        s_intent = dimensions.get("intent_signals", 0)

        # 1. Base Weighted Score
        base_score = (
            (s_auth * W_AUTHENTICITY) +
            (s_auth_tier * W_AUTHORITY) +
            (s_budget * W_BUDGET) +
            (s_clarity * W_CLARITY) +
            (s_footprint * W_FOOTPRINT) +
            (s_intent * W_INTENT)
        )

        # 2. Risk Penalties
        # Apply -10 for each risk flag found
        penalty = len(risk_flags) * 10
        
        final_score = base_score - penalty

        # 3. FRAUD Override
        if verification_result.status == LeadVerificationStatus.LIKELY_FAKE:
            final_score = 0
            s_auth = 0 # Force auth to 0 in breakdown
        else:
            # 4. Baseline Score Rule
            # "No lead should score 0 unless it is explicitely fraudulent"
            # "Introduce a minimum baseline score (e.g., 20) for any non-fraudulent, coherent inquiry."
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
        """Converts a numeric score to a category based on new bands."""
        # 90-100: Rare, exceptionally strong
        # 80-90: High-confidence strategic lead
        # 60-79: Strong lead, pursue actively
        # 40-59: Moderate lead, needs qualification
        # 20-39: Low confidence, early-stage
        
        if score >= 90:
            return "Exceptional"
        elif score >= 80:
            return "High Confidence"
        elif score >= 60:
            return "Strong"
        elif score >= 40:
            return "Moderate"
        else:
            return "Low Confidence"

    def _get_fallback_scoring(self) -> (BANTAnalysis, LeadScore):
        """
        Returns a default scoring in case of AI failure.
        """
        bant = BANTAnalysis(
            budget="Analysis failed.",
            authority="Analysis failed.",
            need="Analysis failed.",
            timeline="Analysis failed."
        )
        score = LeadScore(
            score=20, # Baseline score even for errors? Or 0 for error? Let's say 0 for system error.
            category="Unscored",
            explanation="Could not process lead due to an internal error."
        )
        return bant, score

ai_scoring_service = AIScoringService()
