# test_models.py
from google import genai

# REPLACE WITH YOUR ACTUAL API KEY
API_KEY = "AIzaSyCb-hltBGfxzKkDdsVN-q5lxm6-VnG5N70"  # Put your real key here

print("=" * 60)
print("Testing Gemini Models")
print("=" * 60)

try:
    # Initialize client
    client = genai.Client(api_key=API_KEY)
    print("✅ Client created successfully")
    
    # Models to test from your list
    models_to_test = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-flash-latest",
        "gemini-1.5-flash",
    ]
    
    working_model = None
    
    for model_name in models_to_test:
        print(f"\n🔄 Testing model: {model_name}...")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="What is the best way to stay safe in a crowd? Give a short answer."
            )
            
            if response and response.text:
                print(f"✅ SUCCESS with {model_name}!")
                print(f"   Response: {response.text[:100]}...")
                working_model = model_name
                break
            else:
                print(f"   No response from {model_name}")
                
        except Exception as e:
            print(f"   Error with {model_name}: {e}")
    
    if working_model:
        print(f"\n🎉 Working model found: {working_model}")
        print("✅ Your API key is working correctly!")
        
        # Test a proper conversation
        print("\n" + "=" * 60)
        print("Testing a proper conversation...")
        print("=" * 60)
        
        response = client.models.generate_content(
            model=working_model,
            contents="You are a safety assistant. Answer: How to stay safe?"
        )
        
        if response and response.text:
            print(f"\n🤖 AI Response:\n{response.text}")
        
    else:
        print("\n❌ No working model found. Please check your API key.")
        
except Exception as e:
    print(f"\n❌ Client error: {e}")