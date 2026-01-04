import google.generativeai as genai
import os

from dotenv import load_dotenv

# Load env variables
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

def test_gemini_key():
    print(f"Testing API Key: {API_KEY[:10]}...")
    
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        print("Sending 'Hello' to Gemini...")
        response = model.generate_content("Say 'Hello, I am working!' if you can hear me.")
        
        print("\n--- RESPONSE FROM GEMINI ---")
        print(response.text)
        print("----------------------------")
        print("SUCCESS: API Key is functional.")
        return True
        
    except Exception as e:
        print("\n!!! ERROR !!!")
        print(f"Failed to connect to Gemini: {e}")
        return False

if __name__ == "__main__":
    test_gemini_key()
