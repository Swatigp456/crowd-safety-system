# test_api.py
import google.generativeai as genai

# Replace with your actual API key
API_KEY = "AIzaSyBli-JO7iDPVagbJMGP-HRBCEI8qdoX9R8"

# Configure Gemini
genai.configure(api_key=API_KEY)

# Test the API
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'Hello, API is working!'")
    print("✅ API Key is working!")
    print("Response:", response.text)
except Exception as e:
    print("❌ API Key failed:", e)