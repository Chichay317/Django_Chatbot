from django.shortcuts import render, redirect
from django.http import JsonResponse
import os
import google.generativeai as genai
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from .responses import PREDEFINED_RESPONSES
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

def chatbot(request):
    authenticated = request.user.is_authenticated

    chats = Chat.objects.filter(user=request.user) if authenticated else None

    if request.method == 'POST':
        message = request.POST.get('message') 

        if message:
            try:
                response = model.generate_content(message)
                response_text = response.text

                if authenticated:
                    chat = Chat(user=request.user, message=message, response=response_text, created_at=timezone.now())
                    chat.save()

            except Exception as e:
                response_text = "I'm having trouble generating a response right now. Please try again later."

            return JsonResponse({"response": response_text})
        return JsonResponse({"error": "No message provided"}, status=400)

    return render(request, 'chatbot.html', {
        'chats': chats, 
        'questions_and_answers': PREDEFINED_RESPONSES, 
        'authenticated': authenticated,
        'chat_saving_message': "Your chats won't be saved unless you log in." if not authenticated else ""
    })

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = "User does not exist."
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = "Couldn't create account, Please try again later."
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "Passwords don't match."
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
