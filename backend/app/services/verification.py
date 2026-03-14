from app.models.lead import LeadInput, EnrichmentData, VerificationResult, LeadVerificationStatus, AuthorityTier
from app.utils.gemini_client import gemini_client
from app.config import settings
import asyncio
import json

class VerificationService:
    """
    Service for verifying lead authenticity and authority using Gemini + Google Search.
    Uses Micro-Agent architecture to separate Identity and Intent checks.
    """

    async def verify_lead(self, lead_input: LeadInput, enrichment_data: EnrichmentData) -> VerificationResult:
        """
        Verifies the lead's identity, employment, and intent concurrently.
        """
        identity_prompt = self._build_identity_prompt(lead_input, enrichment_data)
        intent_prompt = self._build_intent_prompt(lead_input, enrichment_data)
        
        try:
            print(f"🕵️‍♂️ [VerificationService] Micro-Agents Verifying: {lead_input.first_name} {lead_input.last_name}")
            
            id_task = gemini_client.generate_json_response(identity_prompt, use_search=True, api_key=settings.google_api_key_identity)
            intent_task = gemini_client.generate_json_response(intent_prompt, use_search=True, api_key=settings.google_api_key_intent)
            
            results = await asyncio.gather(id_task, intent_task, return_exceptions=True)

            for res in results:
                if isinstance(res, Exception):
                    print(f"❌ Verification agent failed: {res}")
                    return self._get_fallback_verification()

            id_data, intent_data = results
            
            status = self._map_status(id_data.get("verification_status"))
            tier = self._map_tier(id_data.get("authority_tier"))
            
            raw_score = id_data.get("verification_score", 0)
            
            # Add bonus points for intent
            intent_signal = intent_data.get("intent_signal", "None")
            if intent_signal == "Strong":
                raw_score += 10
                
            clamped_score = max(0, min(100, raw_score))

            return VerificationResult(
                status=status,
                score=clamped_score,
                authority_tier=tier,
                identity_verified=id_data.get("identity_verified", False),
                employment_verified=id_data.get("employment_verified", False),
                reason=id_data.get("verification_reason", "No reason provided."),
                intent_signal=intent_signal,
                intent_evidence=intent_data.get("intent_evidence", None)
            )

        except Exception as e:
            print(f"❌ [VerificationService] Verification failed: {e}")
            return self._get_fallback_verification()

    def _build_identity_prompt(self, lead_input: LeadInput, enrichment_data: EnrichmentData) -> str:
        enrichment_summary = f"- Official Company Name: {enrichment_data.company_info.get('company_name', 'N/A') if enrichment_data.company_info else 'N/A'} | Website: {enrichment_data.company_info.get('website', 'N/A') if enrichment_data.company_info else 'N/A'}"
        return f"""
        You are an expert Lead Identity Verification Agent. Validate if a lead is REAL and has AUTHORITY. Use Google Search.
        **Claim:** Name: {lead_input.first_name} {lead_input.last_name} | Email: {lead_input.email} | Claimed Company: {lead_input.company_name}
        **Company Data:** {enrichment_summary}

        **Tasks:**
        1. **Identity Check**: Does "{lead_input.first_name} {lead_input.last_name}" exist?
        2. **Employment**: Do they CURRENTLY work at "{lead_input.company_name}"?
        3. **Role Tier**: Tier 1 (C-Level/VP/Founder), Tier 2 (Director/Head), Tier 3 (Manager), Tier 4 (Contributor).
        4. **Email Check**: Does `{lead_input.email}` domain match `{enrichment_data.company_info.get('website', 'N/A') if enrichment_data.company_info else '?'}` (allow country code TLDs)? Does the pattern look corporate? If public email (gmail) for a big corp, flag Fake.

        **Output Logic:**
        - "Verified Decision Maker" (Identity+Employment confirmed + Tier 1/2).
        - "Verified Employee" (Identity+Employment confirmed + Tier 3/4).
        - "Likely Fake" (Contradicts public data, fake email pattern, famous name misuse).
        - "Unverified" (No info).

        **Scoring Base (0-90):** Start 0. +30 Identity, +30 Employment, +20 Domain Match, +10 Pattern Match. Penalty -100 if Fake.

        **Output Format (JSON):**
        {{
            "verification_status": "Verified Decision Maker" | "Verified Employee" | "Unverified" | "Likely Fake",
            "verification_score": <int>,
            "authority_tier": "Tier 1" | "Tier 2" | "Tier 3" | "Tier 4" | "Unknown",
            "identity_verified": <bool>,
            "employment_verified": <bool>,
            "verification_reason": "Short explanation"
        }}
        """
        
    def _build_intent_prompt(self, lead_input: LeadInput, enrichment_data: EnrichmentData) -> str:
        return f"""
        You are an expert Intent Signal Verification Agent. Use Google Search to find public evidence of the lead's company needing the requested services.
        **Company:** {lead_input.company_name} | **Inquiry Context:** "{lead_input.notes}"

        **Task:**
        - Is there ANY PUBLIC EVIDENCE that {lead_input.company_name} is interested in the topic mentioned in their notes?
        - E.g., if they asked for cloud migration, did they recently announce a digital transformation initiative?
        
        Determine Signal Strength:
        - **Strong**: Explicit news, job postings, or PR found related to the note.
        - **Weak**: Inferred/Logical fit based on industry, but no explicit PR.
        - **None**: No evidence or mismatch.

        **Output Format (JSON):**
        {{
            "intent_signal": "Strong" | "Weak" | "None",
            "intent_evidence": "URL or short summary of evidence found (or null)"
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
            reason="Verification failed due to technical error.",
            intent_signal="None",
            intent_evidence=None
        )

verification_service = VerificationService()
