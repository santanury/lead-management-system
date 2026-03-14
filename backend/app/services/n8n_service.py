import httpx
from app.config import settings
from app.models.lead import LeadInput, LeadScore

class N8nService:
    """
    Service for sending lead data to an n8n webhook asynchronously.
    """
    
    async def trigger_webhook(self, lead_input: LeadInput, lead_score: LeadScore):
        """
        Sends the lead_input and lead_score to the configured n8n webhook URL.
        """
        webhook_url = settings.n8n_webhook_url
        
        if not webhook_url:
            print("⚠️ [N8nService] No N8N_WEBHOOK_URL configured. Skipping webhook trigger.")
            return

        payload = {
            "lead_input": lead_input.model_dump(),
            "lead_score": lead_score.model_dump()
        }

        print(f"🚀 [N8nService] Sending {lead_score.category} lead ({lead_input.first_name}) to n8n...")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
                print(f"✅ [N8nService] Successfully triggered n8n webhook! Status: {response.status_code}")
                
        except httpx.HTTPError as e:
            print(f"❌ [N8nService] Failed to trigger n8n webhook: {e}")
        except Exception as e:
            print(f"❌ [N8nService] Unexpected error triggering n8n webhook: {e}")

n8n_service = N8nService()
