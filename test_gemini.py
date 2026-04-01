# test_gemini.py
import google.generativeai as genai

# REPLACE WITH YOUR ACTUAL API KEY
API_KEY = "AIzaSyCb-hltBGfxzKkDdsVN-q5lxm6-VnG5N70"  # Put your real key here

print("Testing Gemini API...")

# Configure
genai.configure(api_key=API_KEY)

# Test the model
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'Hello, API is working!'")
    print("✅ SUCCESS! Response:", response.text)
except Exception as e:
    print("❌ ERROR:", e)