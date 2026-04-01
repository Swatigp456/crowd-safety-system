# test_new_gemini.py
from google import genai

# REPLACE WITH YOUR ACTUAL API KEY
API_KEY = "AIzaSyCb-hltBGfxzKkDdsVN-q5lxm6-VnG5N70"  # Put your real key here

print("=" * 50)
print("Testing New Google GenAI SDK")
print("=" * 50)

try:
    # Initialize client
    client = genai.Client(api_key=API_KEY)
    print("✅ Client created successfully")
    
    # Test with a simple prompt
    print("🔄 Sending test message...")
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents="Say 'Hello, API is working!'"
    )
    
    print(f"✅ SUCCESS! Response: {response.text}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")