import requests
import json
from app.config import settings

class GeminiClient:
    def __init__(self):
        self.api_key = settings.google_api_key
        # Using the model confirmed by user and curl check
        self.model_name = "gemini-2.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def generate_json_response(self, prompt: str, model_name: str = None, use_search: bool = False) -> dict:
        """
        Generates a JSON response from a prompt using the Gemini REST API.
        """
        model = model_name or self.model_name
        url = f"{self.base_url}/{model}:generateContent"
        params = {"key": self.api_key}
        
        # We verify request structures for Gemini 1.5/pro series
        headers = {"Content-Type": "application/json"}
        
        # Construct the payload
        # Ensure we ask for JSON explicitly in the prompt as well
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
            # Add Google Search tool
            data["tools"] = [{"google_search": {}}]

        try:
            response = requests.post(url, params=params, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract text from response
            # Structure: candidates[0].content.parts[0].text
            candidates = result.get("candidates", [])
            if not candidates:
                 raise ValueError("No candidates returned from Gemini API")
            
            text_response = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            # Clean up markdown code blocks if present
            cleaned_text = text_response.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:] # Handle ``` if just that
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
                
            return json.loads(cleaned_text)

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response body: {response.text}")
            raise
        except Exception as e:
            print(f"Error generating response from Gemini: {e}")
            raise

    def generate_content(self, prompt: str, model_name: str = None) -> str:
        """
        Generates a plain text response.
        """
        model = model_name or self.model_name
        url = f"{self.base_url}/{model}:generateContent"
        params = {"key": self.api_key}
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(url, params=params, headers=headers, json=data, timeout=30)
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
