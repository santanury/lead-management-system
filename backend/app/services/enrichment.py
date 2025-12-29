from app.models.lead import EnrichmentData

class EnrichmentService:
    """
    A modular service for enriching lead data.
    In a real-world application, this service would integrate with third-party
    APIs like Clearbit, Hunter.io, or internal databases.
    """

    def enrich_lead(self, company_name: str, email: str) -> EnrichmentData:
        """
        Enriches lead data with company information and email validation.
        """
        is_valid_email = self._validate_email(email)
        company_info = self._enrich_company_info(company_name) if is_valid_email else None
        
        return EnrichmentData(
            company_info=company_info,
            email_valid=is_valid_email,
        )

    def _validate_email(self, email: str) -> bool:
        """
        Simulates email validation.
        Placeholder: For the hackathon, we'll assume most emails are valid.
        A real implementation would use a service like NeverBounce or ZeroBounce.
        """
        if "invalid" in email:
            return False
        return True

    def _enrich_company_info(self, company_name: str) -> dict:
        """
        Simulates company data enrichment.
        Placeholder: Returns mock data based on the company name.
        A real implementation would use a service like Clearbit or ZoomInfo.
        """
        # Mock data for demonstration purposes
        if "big corp" in company_name.lower():
            return {
                "company_name": "Big Corp Inc.",
                "industry": "Technology",
                "size": "10,001+ employees",
                "website": "www.bigcorp.com",
            }
        elif "startup" in company_name.lower():
            return {
                "company_name": "Startup LLC",
                "industry": "Software",
                "size": "11-50 employees",
                "website": "www.startup.io",
            }
        return {
            "company_name": company_name,
            "industry": "Unknown",
            "size": "Unknown",
            "website": "Unknown",
        }

enrichment_service = EnrichmentService()
