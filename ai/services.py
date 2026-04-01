# ai/services.py
from google import genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class GeminiChatbot:
    """Gemini AI Chatbot using google-genai SDK"""
    
    def __init__(self):
        self.available = False
        self.client = None
        # Use only the models that appeared in your list
        self.model_names = [
            "gemini-2.5-flash",      # From your list ✅
            "gemini-2.0-flash",      # From your list ✅
            "gemini-flash-latest",   # From your list ✅
            "gemini-1.5-flash",      # Alternative
        ]
        self.current_model = None
        
        try:
            # Get API key from settings
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            
            if not api_key:
                print("❌ ERROR: GEMINI_API_KEY not found in settings!")
                return
            
            if api_key == "AIzaSyCxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
                print("❌ ERROR: Please replace with your actual API key in settings.py!")
                return
            
            # Initialize the client
            self.client = genai.Client(api_key=api_key)
            print("✅ Gemini client initialized")
            
            # Try each model until one works
            for model_name in self.model_names:
                try:
                    print(f"🔄 Testing model: {model_name}...")
                    test_response = self.client.models.generate_content(
                        model=model_name,
                        contents="Say 'OK'"
                    )
                    
                    if test_response and test_response.text:
                        self.current_model = model_name
                        self.available = True
                        print(f"✅ Using model: {model_name}")
                        break
                        
                except Exception as e:
                    print(f"   Model {model_name} failed: {e}")
                    continue
            
            if not self.available:
                print("❌ No working model found!")
                
        except Exception as e:
            self.available = False
            print(f"❌ Gemini initialization error: {e}")
    
    def get_response(self, user_message, user_context=None):
        """
        Get AI response for user's message
        """
        # Check if AI is available
        if not self.available:
            return {
                'status': 'error',
                'message': "AI service is not available. Please check your API key configuration.",
                'error': "API not configured"
            }
        
        try:
            # Create a prompt for safety assistant
            prompt = f"""You are a friendly crowd safety assistant. Answer this question briefly and helpfully.

Question: {user_message}

Answer:"""
            
            # Get response from Gemini
            response = self.client.models.generate_content(
                model=self.current_model,
                contents=prompt
            )
            
            # Check if we got a valid response
            if response and response.text:
                return {
                    'status': 'success',
                    'message': response.text.strip(),
                    'error': None
                }
            else:
                return {
                    'status': 'error',
                    'message': "I couldn't generate a response. Please try again.",
                    'error': "Empty response"
                }
            
        except Exception as e:
            print(f"Gemini error: {e}")
            return {
                'status': 'error',
                'message': f"Sorry, I encountered an error. Please try again.",
                'error': str(e)
            }