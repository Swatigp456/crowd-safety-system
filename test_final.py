# test_final.py
from google import genai

# REPLACE WITH YOUR ACTUAL API KEY
API_KEY = "AIzaSyCb-hltBGfxzKkDdsVN-q5lxm6-VnG5N70"  # Put your real key here

print("=" * 60)
print("Testing Gemini Models from Your List")
print("=" * 60)

# Models from your list
models_to_test = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-1.5-flash",
]

try:
    client = genai.Client(api_key=API_KEY)
    print("✅ Client created successfully\n")
    
    working_model = None
    
    for model_name in models_to_test:
        print(f"Testing: {model_name}")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Say 'Hello, I am working!'"
            )
            
            if response and response.text:
                print(f"  ✅ SUCCESS! Response: {response.text[:50]}...\n")
                working_model = model_name
                break
            else:
                print(f"  ❌ No response\n")
                
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    if working_model:
        print("=" * 60)
        print(f"✅ WORKING MODEL FOUND: {working_model}")
        print("=" * 60)
        
        # Test a real question
        print("\nTesting with a real question...\n")
        response = client.models.generate_content(
            model=working_model,
            contents="What is the best way to stay safe in a crowd? Give a short answer."
        )
        
        if response and response.text:
            print(f"🤖 AI Response:\n{response.text}")
            
    else:
        print("=" * 60)
        print("❌ No working model found!")
        print("=" * 60)
        
except Exception as e:
    print(f"❌ Error: {e}")