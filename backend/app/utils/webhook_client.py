import requests
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

def send_webhook(url: str, data: dict):
    """
    Sends a JSON payload to the specified webhook URL.
    Intended to be run as a background task.
    """
    if not url:
        return

    try:
        logger.info(f"🚀 [Webhook] Sending lead data to {url}...")
        
        # Determine if data is Pydantic model or dict
        payload = data
        if hasattr(data, "model_dump"):
            payload = data.model_dump(mode="json")
        elif hasattr(data, "dict"):
            payload = data.dict()
            
        response = requests.post(
            url, 
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"✅ [Webhook] Successfully delivered to {url} (Status: {response.status_code})")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ [Webhook] Failed to send data to {url}: {e}")
