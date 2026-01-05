from app.models.lead import LeadInput, BANTAnalysis, LeadScore, EnrichmentData, VerificationResult, LeadVerificationStatus
from app.utils.gemini_client import gemini_client
import json

class AIScoringService:
    """
    Service for scoring leads using AI (Gemini).
    """

    def score_lead(self, lead_input: LeadInput, enrichment_data: EnrichmentData, verification_result: VerificationResult) -> (BANTAnalysis, LeadScore):
        """
        Analyzes and scores a lead using the Gemini AI model.
        """
        # Fetch selected model from DB
        from app.db.database import get_session
        from app.models.settings import Settings
        from sqlmodel import select
        
        # Helper to get session since we are in a service
        # In a larger app, we'd pass session as dependency
        with next(get_session()) as session:
            settings_db = session.exec(select(Settings)).first()
            selected_model = settings_db.selected_model if settings_db else "gemini-2.5-flash"

        prompt = self._build_prompt(lead_input, enrichment_data, verification_result)
        
        try:
            # Get the structured JSON response from Gemini
            ai_response = gemini_client.generate_json_response(prompt, model_name=selected_model)
            
            # Parse the AI response into our Pydantic models
            bant_analysis = BANTAnalysis(**ai_response.get("bant_analysis", {}))
            
            # The AI provides a preliminary score and explanation
            ai_score_details = ai_response.get("lead_score", {})
            
            # Here you can add deterministic logic to adjust the score.
            # For now, we'll primarily use the AI's judgment.
            final_score = self._calculate_final_score(ai_score_details.get("score", 0), lead_input, verification_result, enrichment_data)
            
            lead_score = LeadScore(
                score=final_score,
                category=self._score_to_category(final_score),
                explanation=ai_score_details.get("explanation", "No explanation provided."),
            )
            
            return bant_analysis, lead_score

        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"Failed to parse AI response: {e}")
            # Fallback to a default/error state if AI fails
            return self._get_fallback_scoring()

    def _build_prompt(self, lead_input: LeadInput, enrichment_data: EnrichmentData, verification_result: VerificationResult) -> str:
        """
        Constructs the prompt for the Gemini API.
        """
        return f"""
        Analyze the following sales lead and perform a BANT analysis (Budget, Authority, Need, Timeline). 
        Based on your analysis, provide a lead score from 0 to 100 and a brief explanation.

        **Lead Information:**
        - First Name: {lead_input.first_name}
        - Last Name: {lead_input.last_name}
        - Company: {lead_input.company_name}
        - Email: {lead_input.email}
        - Notes/Message: "{lead_input.notes}"

        **Verification & Authority Check (Pre-Computed):**
        - Status: {verification_result.status.value}
        - Verified Score: {verification_result.score}/100
        - Authority Tier: {verification_result.authority_tier.value}
        - Reason: {verification_result.reason}

        **Enriched Company Data (from Google Search):**
        - Official Name: {enrichment_data.company_info.get('company_name', 'N/A') if enrichment_data.company_info else 'N/A'}
        - Industry: {enrichment_data.company_info.get('industry', 'N/A') if enrichment_data.company_info else 'N/A'}
        - Size: {enrichment_data.company_info.get('size', 'N/A') if enrichment_data.company_info else 'N/A'}
        - Website: {enrichment_data.company_info.get('website', 'N/A') if enrichment_data.company_info else 'N/A'}
        
        **Instructions:**
        1.  **Verification:** Cross-reference the user's claims with the enriched company data. 
            - If the user claims to be from a large enterprise but the enriched data shows a small unknown shop, flag this as a risk.
            - If the email domain aligns with the website, treat it as verified.
        2.  **BANT Analysis:** Evaluate each BANT component based on the lead's message. Be critical. If information is missing, state that it's inferred or not available.
        3.  **Lead Score:** Assign a score from 0 to 100. **BE STRICT.** 
            - **100/100** should be extremely rare (reserved for perfect, verified, immediate high-value deals).
            - A typical "Good" lead should be in the **70-85** range.
            - 85+ is "Hot", 60-84 is "Warm", below 60 is "Cold".
        4.  **High-Stakes Risk Guardrail:**
            - **Rule**: If the inferred Budget is HIGH (e.g., > $50,000) BUT the Verification Status is "Unverified" or "Likely Fake", you MUST penalize the score.
            - A high-budget claim from an unknown/unverified entity is suspect. CAP the score at 50 ("Cold") and mark explanation as "High Risk / Manual Review Needed".
        5.  **Explanation:** Justify your score in one or two sentences. Explicitly mention if the company background check (enrichment) positively or negatively influenced the score.
            - **CRITICAL:** Your explanation MUST be consistent with the score key.
            - If score < 60, do NOT call it a "warm" lead. Call it "Cold", "Weak", or "High Risk".
            - If score is 60-84, call it "Warm" or "Promising".
            - If score is 85+, call it "Hot" or "Excellent".

        **Output Format:**
        Return a single JSON object with two keys: "bant_analysis" and "lead_score".
        - "bant_analysis" should be an object with keys: "budget", "authority", "need", "timeline".
        - "lead_score" should be an object with keys: "score" (integer) and "explanation" (string).

        Example of a good lead: "We have a 20k budget approved and need to implement a solution in the next quarter. I am the department head responsible for this decision."
        Example of a bad lead: "Just looking for info."
        """

    def _calculate_final_score(self, ai_score: int, lead_input: LeadInput, verification_result: VerificationResult, enrichment_data: EnrichmentData) -> int:
        """
        Applies deterministic adjustments to the AI-generated score and budget caps.
        """
        # CRITICAL: If flagged as Likely Fake, kill the score.
        if verification_result.status == LeadVerificationStatus.LIKELY_FAKE:
            return 0
            
        score = ai_score

        # --- BUDGET TIER CAP LOGIC ---
        import re
        budget_val = 0
        # Heuristic extraction of budget from notes
        matches = re.findall(r'(\d+)(?:k|000)\b', lead_input.notes.lower())
        if matches:
            vals = [int(m) * 1000 for m in matches]
            budget_val = max(vals)
        else:
             if "million" in lead_input.notes.lower() or "1m" in lead_input.notes.lower():
                 budget_val = 1000000

        # User Feedback logic: "Verified employee, decision maker, and big corp should be consider if proposal is good"
        # Only apply bonuses if the base proposal is decent.
        if score >= 50:
            # 1. Verification / Authority Boost
            if verification_result.status == LeadVerificationStatus.VERIFIED_DECISION_MAKER:
                score += 10 
            elif verification_result.status == LeadVerificationStatus.VERIFIED_EMPLOYEE:
                score += 5
            
            # 2. Company Size Boost
            company_size = enrichment_data.company_info.get("size", "0") if enrichment_data.company_info else "0"
            size_str = str(company_size).lower()
            if any(s in size_str for s in ["1000+", "5000+", "10,000+", "500+", "large", "enterprise", "public"]):
                score += 10

        # --- APPLY BUDGET CAPS (Final Ceiling) ---
        # Ensure that small deals cannot reach 100/100, even with bonuses.
        # < $10k -> Cap at 70 (Warm)
        # $10k - $50k -> Cap at 85 (Warm/Hot border)
        # > $50k -> No Cap (Hot)
        
        if budget_val > 0 and budget_val < 10000:
            score = min(score, 70) 
        elif budget_val >= 10000 and budget_val < 50000:
            score = min(score, 85)

        return min(max(score, 0), 100) # Clamp score between 0 and 100

    def _score_to_category(self, score: int) -> str:
        """Converts a numeric score to a category."""
        if score >= 85:
            return "Hot"
        elif score >= 60:
            return "Warm"
        else:
            return "Cold"

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
            score=0,
            category="Unscored",
            explanation="Could not process lead due to an internal error."
        )
        return bant, score

ai_scoring_service = AIScoringService()
