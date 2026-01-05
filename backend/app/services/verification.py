from app.models.lead import LeadInput, EnrichmentData, VerificationResult, LeadVerificationStatus, AuthorityTier
from app.utils.gemini_client import gemini_client
import json

class VerificationService:
    """
    Service for verifying lead authenticity and authority using Gemini + Google Search.
    """

    def verify_lead(self, lead_input: LeadInput, enrichment_data: EnrichmentData) -> VerificationResult:
        """
        Verifies the lead's identity, employment, and authority.
        """
        
        # Build prompt for the Agentic Verification Engine
        prompt = self._build_verification_prompt(lead_input, enrichment_data)
        
        try:
            print(f"🕵️‍♂️ [VerificationService] Verifying: {lead_input.first_name} {lead_input.last_name} at {lead_input.company_name}")
            
            # Call Gemini with processing search enabled
            # Note: We ask Gemini to do the searching and synthesis "internally" via tools if available, 
            # or we rely on its training + the search tool we specifically enable.
            verification_response = gemini_client.generate_json_response(prompt, use_search=True)
            
            # Map response to Pydantic model
            status_str = verification_response.get("verification_status")
            tier_str = verification_response.get("authority_tier")
            
            # Safe mapping for enums
            status = self._map_status(status_str)
            tier = self._map_tier(tier_str)
            
            raw_score = verification_response.get("verification_score", 0)
            clamped_score = max(0, min(100, raw_score))

            return VerificationResult(
                status=status,
                score=clamped_score,
                authority_tier=tier,
                identity_verified=verification_response.get("identity_verified", False),
                employment_verified=verification_response.get("employment_verified", False),
                reason=verification_response.get("verification_reason", "No reason provided.")
            )

        except Exception as e:
            print(f"❌ [VerificationService] Verification failed: {e}")
            return self._get_fallback_verification()

    def _build_verification_prompt(self, lead_input: LeadInput, enrichment_data: EnrichmentData) -> str:
        enrichment_summary = f"""
        - Official Company Name: {enrichment_data.company_info.get('company_name', 'N/A') if enrichment_data.company_info else 'N/A'}
        - Size: {enrichment_data.company_info.get('size', 'N/A') if enrichment_data.company_info else 'N/A'}
        - Website: {enrichment_data.company_info.get('website', 'N/A') if enrichment_data.company_info else 'N/A'}
        """
        
        return f"""
        You are an expert Lead Verification Agent. Your job is to validate whether a sales lead is REAL (authentic) and has the AUTHORITY they claim.
        You have access to Google Search. Use it to verify the person's existence and current role.

        **Lead Claims:**
        - Name: {lead_input.first_name} {lead_input.last_name}
        - Email: {lead_input.email}
        - Stated Company: {lead_input.company_name}
        - Note Context: "{lead_input.notes}"

        **Known Company Data:**
        {enrichment_summary}

        **Investigation Tasks:**
        1.  **Identity Check**: Does "{lead_input.first_name} {lead_input.last_name}" exist as a professional? Search for LinkedIn, official company bios, or news.
        2.  **Employment Check**: Does this person CURRENTLY work at "{lead_input.company_name}" (or the Official Company Name)? 
            - *Critical*: If they work at a DIFFERENT company now, flag as "Likely Fake" or "Unverified".
        3.  **Role & Authority Check**: What is their actual job title? 
            - Map it to a Tier: 
                - Tier 1: C-Level, Founder, Partner, EVP.
                - Tier 2: VP, Head of X, Director.
                - Tier 3: Manager, Lead.
                - Tier 4: Analyst, Associate, Engineer, Specialist.
            - Does the role match the company size? (e.g., A "CEO" of a 1-person company is technically Tier 1 but low authority in practice, but sticking to title is fine for now).
        4.  **Email Check**: 
            - **Domain**: Does the email domain match the official website? ({enrichment_data.company_info.get('website', 'N/A') if enrichment_data.company_info else '?'})
            - **Pattern Intelligence**: Search for "email format for {lead_input.company_name}" or guess based on typical corporate patterns (e.g., firstname.lastname@, firstinitial.lastname@). 
            - Does `{lead_input.email}` look like a standard corporate email for this company?
            - If email is @gmail/@yahoo but claiming to be an Executive at a Big Corp -> FLAG AS FAKE/PERSONAL.
            - If email uses a weird variation (e.g. `soumya17@` vs `soumya.chaki@`) -> Downgrade confidence.

        **Output Logic:**
        - **Verified Decision Maker**: Identity confirmed + Employment confirmed + Tier 1 or 2. (Email Pattern Match is preferred but NOT required for small companies).
        - **Verified Employee**: Identity confirmed + Employment confirmed + Tier 3 or 4.
        - **Likely Fake**: 
            - Claimed role contradicts public data (e.g. LinkedIn says they are a student or work elsewhere).
            - Famous name (e.g. Satya Nadella) with non-corporate email.
            - Non-existent person at a major company.
            - **Email Pattern Mismatch**: Domain is correct but username part looks HIGHLY suspicious (e.g. `ceo.microsoft@outlook.com` or `satya123@microsoft.com`). If it's just a common variation (e.g. `ahmad.zafar` vs `zafar.ahmad`), DO NOT fail it.
        - **Unverified**: Cannot find enough info to confirm or deny.

        **Scoring (0-100):**
        - Start at 0.
        - +30 for Identity Verified.
        - +30 for Employment Verified at this company.
        - +20 for Corporate Domain Match.
        - +10 for Standard Email Pattern Match (Bonus).
        - +10 for Tier 1 Role, +5 for Tier 2 Role.
        - PENALTY: -100 if "Likely Fake".

        **Return JSON:**
        {{
            "verification_status": "Verified Decision Maker" | "Verified Employee" | "Unverified" | "Likely Fake",
            "verification_score": <int>,
            "authority_tier": "Tier 1" | "Tier 2" | "Tier 3" | "Tier 4" | "Unknown",
            "identity_verified": <bool>,
            "employment_verified": <bool>,
            "verification_reason": "<Short explanation>"
        }}
        """

    def _map_status(self, status: str) -> LeadVerificationStatus:
        if not status: return LeadVerificationStatus.UNVERIFIED
        status_clean = status.lower()
        if "decision maker" in status_clean: return LeadVerificationStatus.VERIFIED_DECISION_MAKER
        if "employee" in status_clean: return LeadVerificationStatus.VERIFIED_EMPLOYEE
        if "fake" in status_clean: return LeadVerificationStatus.LIKELY_FAKE
        return LeadVerificationStatus.UNVERIFIED

    def _map_tier(self, tier: str) -> AuthorityTier:
        if not tier: return AuthorityTier.UNKNOWN
        tier_clean = tier.lower()
        if "tier 1" in tier_clean: return AuthorityTier.TIER_1
        if "tier 2" in tier_clean: return AuthorityTier.TIER_2
        if "tier 3" in tier_clean: return AuthorityTier.TIER_3
        if "tier 4" in tier_clean: return AuthorityTier.TIER_4
        return AuthorityTier.UNKNOWN

    def _get_fallback_verification(self) -> VerificationResult:
        return VerificationResult(
            status=LeadVerificationStatus.UNVERIFIED,
            score=0,
            authority_tier=AuthorityTier.UNKNOWN,
            identity_verified=False,
            employment_verified=False,
            reason="Verification failed due to technical error."
        )

verification_service = VerificationService()
