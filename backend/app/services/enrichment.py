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
            company_logo_url=company_info.get("company_logo_url") if company_info else None,
            profile_image_url=company_info.get("profile_image_url") if company_info else None
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
        
        # Determine fallback logo URL
        # Switched to Google Favicons as Clearbit was reported unreachable
        fallback_logo_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128" if domain else None
        
        prompt = f"""
        You are a data enrichment bot with access to Google Search.
        Use Google Search to find the latest information about the company "{company_name}" (Domain: {domain}).
        Also try to find a URL for their official logo and a generic profile image placeholder or the CEO's image if relevant.
        
        Provide a JSON object with:
        - company_name (official name)
        - industry (e.g. Technology, Healthcare, Finance)
        - size (approx employees, e.g. "10-50", "1000+")
        - website (official URL)
        - company_logo_url (URL to a high-quality logo image, or null)
        - profile_image_url (URL to a relevant profile image, or null)
        
        Return ONLY valid JSON.
        """
        
        try:
            print(f"🔍 [EnrichmentService] Searching Google for: {company_name}")
            # Use JSON response method with search enabled
            # Use JSON response method with search enabled
            result = gemini_client.generate_json_response(prompt, use_search=True)
            print(f"✅ [EnrichmentService] Search Result: {result}")
            
            # Fallback/Override for logo if Gemini returns nothing or a broken link (basic check)
            if fallback_logo_url:
                 # If Gemini didn't find one, or we want to trust Clearbit
                 current_logo = result.get("company_logo_url")
                 if not current_logo or "http" not in current_logo:
                     result["company_logo_url"] = fallback_logo_url
                     print(f"⚠️ [EnrichmentService] Used Google Favicon fallback for logo: {fallback_logo_url}")

            return result
        except Exception as e:
            print(f"❌ [EnrichmentService] Enrichment failed: {e}")
            return {
                "company_name": company_name,
                "industry": "Unknown",
                "size": "Unknown",
                "website": "Unknown",
                "company_logo_url": fallback_logo_url,
                "profile_image_url": None
            }

enrichment_service = EnrichmentService()
