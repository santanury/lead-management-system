import httpx
import json
import asyncio
from app.config import settings

class GeminiClient:
    def __init__(self):
        self.default_api_key = settings.google_api_key
        self.model_name = "gemini-2.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate_json_response(self, prompt: str, model_name: str = None, use_search: bool = False, api_key: str = None) -> dict:
        """
        Generates a JSON response asynchronously from a prompt using the Gemini REST API.
        Accepts a specific api_key to route requests to different quotas.
        """
        model = model_name or self.model_name
        url = f"{self.base_url}/{model}:generateContent"
        
        # Use provided key or fallback to default
        active_key = api_key or self.default_api_key
        params = {"key": active_key}
        
        headers = {"Content-Type": "application/json"}
        
        final_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON."
        
        data = {
            "contents": [{
                "parts": [{"text": final_prompt}]
            }],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }
        
        if use_search:
            data["tools"] = [{"google_search": {}}]
            if "generationConfig" in data:
                del data["generationConfig"]
        
        max_retries = 3
        backoff = 2
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(url, params=params, headers=headers, json=data)
                    
                    if response.status_code == 429:
                        if attempt == max_retries - 1:
                            raise Exception(f"Gemini API Rate Limit exceeded after {max_retries} retries.")
                        print(f"⚠️ Gemini Rate Limit. Retrying in {backoff}s...")
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                        
                    response.raise_for_status()
                    result = response.json()
                    break
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        if attempt == max_retries - 1:
                            raise e
                        print(f"⚠️ Gemini Rate Limit (Exception). Retrying in {backoff}s...")
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                        
                    if attempt == max_retries - 1:
                        print(f"❌ Error communicating with Gemini API after {max_retries} attempts: {e}")
                        raise e
                    print(f"⚠️ Gemini API Error (Attempt {attempt+1}): {e}. Retrying...")
                    await asyncio.sleep(backoff)
                    backoff *= 2
                except httpx.RequestError as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"⚠️ Gemini Network Error: {e}. Retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
                    backoff *= 2
                
        try:
            candidates = result.get("candidates", [])
            if not candidates:
                 raise ValueError("No candidates returned from Gemini API")
            
            text_response = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            cleaned_text = text_response.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
                
            return json.loads(cleaned_text)

        except Exception as e:
            print(f"Error generating/parsing response from Gemini: {e}")
            raise

    async def generate_content(self, prompt: str, model_name: str = None, api_key: str = None) -> str:
        """
        Generates a plain text response asynchronously.
        """
        model = model_name or self.model_name
        url = f"{self.base_url}/{model}:generateContent"
        active_key = api_key or self.default_api_key
        params = {"key": active_key}
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, params=params, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                candidates = result.get("candidates", [])
                if not candidates:
                     return ""
                return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            except Exception as e:
                print(f"Error generating content: {e}")
                return ""

gemini_client = GeminiClient()
