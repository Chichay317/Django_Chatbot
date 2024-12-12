from django.shortcuts import render, redirect
from django.http import JsonResponse
import os
import google.generativeai as genai
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone

gemini_api_key = os.environ["GEMINI_API_KEY"]
genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message') 
        if message:
            response = model.generate_content(message)
            chat = Chat(user=request.user, message=message, response=response.text, created_at=timezone.now())
            chat.save()
            return JsonResponse({"response": response.text})
        return JsonResponse({"error": "No message provided"}, status=400)
    return render(request, 'chatbot.html', {'chats': chats})

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
