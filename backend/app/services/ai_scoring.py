from app.models.lead import LeadInput, BANTAnalysis, LeadScore
from app.utils.gemini_client import gemini_client
import json

class AIScoringService:
    """
    Service for scoring leads using AI (Gemini).
    """

    def score_lead(self, lead_input: LeadInput) -> (BANTAnalysis, LeadScore):
        """
        Analyzes and scores a lead using the Gemini AI model.
        """
        prompt = self._build_prompt(lead_input)
        
        try:
            # Get the structured JSON response from Gemini
            ai_response = gemini_client.generate_json_response(prompt)
            
            # Parse the AI response into our Pydantic models
            bant_analysis = BANTAnalysis(**ai_response.get("bant_analysis", {}))
            
            # The AI provides a preliminary score and explanation
            ai_score_details = ai_response.get("lead_score", {})
            
            # Here you can add deterministic logic to adjust the score.
            # For now, we'll primarily use the AI's judgment.
            final_score = self._calculate_final_score(ai_score_details.get("score", 0), lead_input)
            
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

    def _build_prompt(self, lead_input: LeadInput) -> str:
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

        **Instructions:**
        1.  **BANT Analysis:** Evaluate each BANT component based on the lead's message. Be critical. If information is missing, state that it's inferred or not available.
        2.  **Lead Score:** Assign a score from 0 (very low quality) to 100 (perfect fit). A score of 85+ is "Hot", 60-84 is "Warm", and below 60 is "Cold".
        3.  **Explanation:** Justify your score in one or two sentences.

        **Output Format:**
        Return a single JSON object with two keys: "bant_analysis" and "lead_score".
        - "bant_analysis" should be an object with keys: "budget", "authority", "need", "timeline".
        - "lead_score" should be an object with keys: "score" (integer) and "explanation" (string).

        Example of a good lead: "We have a 20k budget approved and need to implement a solution in the next quarter. I am the department head responsible for this decision."
        Example of a bad lead: "Just looking for info."
        """

    def _calculate_final_score(self, ai_score: int, lead_input: LeadInput) -> int:
        """
        Applies deterministic adjustments to the AI-generated score.
        For example, boost score for known strategic companies.
        """
        score = ai_score
        if "big corp" in lead_input.company_name.lower():
            score += 5  # Add a small boost for enterprise leads
        
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
