from app.models.lead import EnrichmentData
from app.utils.gemini_client import gemini_client
import json

class EnrichmentService:
    """
    A modular service for enriching lead data.
    Uses Gemini to "hallucinate" (retrieve knowledge of) company details.
    """

    def enrich_lead(self, company_name: str, email: str) -> EnrichmentData:
        """
        Enriches lead data with company information and email validation.
        """
        is_valid_email = self._validate_email(email)
        company_info = self._enrich_company_info(company_name, email) if is_valid_email else None
        
        return EnrichmentData(
            company_info=company_info,
            email_valid=is_valid_email,
        )

    def _validate_email(self, email: str) -> bool:
        """
        Simulates email validation.
        """
        if "invalid" in email:
            return False
        return True

    def _enrich_company_info(self, company_name: str, email: str) -> dict:
        """
        Uses Gemini to get company details.
        """
        # Fetch status of search enrichment from settings potentially, but forcing for now as per user request
        
        # Extract domain from email if possible for better search
        domain = email.split('@')[-1] if email and "@" in email else ""
        
        prompt = f"""
        You are a data enrichment bot with access to Google Search.
        Use Google Search to find the latest information about the company "{company_name}" (Domain: {domain}).
        
        Provide a JSON object with:
        - company_name (official name)
        - industry (e.g. Technology, Healthcare, Finance)
        - size (approx employees, e.g. "10-50", "1000+")
        - website (official URL)
        
        Return ONLY valid JSON.
        """
        
        try:
            print(f"🔍 [EnrichmentService] Searching Google for: {company_name}")
            # Use JSON response method with search enabled
            result = gemini_client.generate_json_response(prompt, use_search=True)
            print(f"✅ [EnrichmentService] Search Result: {result}")
            return result
        except Exception as e:
            print(f"❌ [EnrichmentService] Enrichment failed: {e}")
            return {
                "company_name": company_name,
                "industry": "Unknown",
                "size": "Unknown",
                "website": "Unknown",
            }

enrichment_service = EnrichmentService()
