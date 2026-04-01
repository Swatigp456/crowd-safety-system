 # ai/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import GeminiChatbot
import json

# Create the chatbot instance
chatbot = GeminiChatbot()

@login_required
def chat_page(request):
    """Display the chat page"""
    return render(request, 'ai/chat.html')

@login_required
@csrf_exempt
def chat_api(request):
    """Handle chat messages"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        # Get the user's message
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'Message is empty'}, status=400)
        
        # Get user context (optional)
        user_context = {
            'location': request.GET.get('location', 'Unknown'),
            'time': str(request.user.date_joined) if request.user.is_authenticated else 'Unknown'
        }
        
        # Get AI response
        response = chatbot.get_response(user_message, user_context)
        
        return JsonResponse(response)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
