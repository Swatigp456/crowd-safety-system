# list_models.py
from google import genai

API_KEY = "AIzaSyCb-hltBGfxzKkDdsVN-q5lxm6-VnG5N70"  # Replace with your actual API key

print("=" * 60)
print("Fetching available models...")
print("=" * 60)

try:
    client = genai.Client(api_key=API_KEY)
    
    # List all available models
    models = client.models.list()
    
    print("\n✅ Available Models:\n")
    for model in models:
        if "gemini" in model.name:
            print(f"  📌 {model.name}")
            print(f"     Display Name: {model.display_name}")
            print(f"     Description: {model.description[:100]}...")
            print()
            
except Exception as e:
    print(f"❌ Error: {e}")