from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
import json
from .models import User

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_student:
                return redirect('student_selection') 
            elif user.is_property_owner:
                return redirect('http://127.0.0.1:8000/api/accommodations/') 
            elif user.is_cedars_staff or user.is_admin:
                return redirect('http://127.0.0.1:8000/admin/')
            else:
                return redirect('http://127.0.0.1:8000/')
        else:
            return JsonResponse({'message': 'Invalid credentials'}, status=400)
    elif request.method == 'GET':
        return render(request, 'login.html')
@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout successful'})
    elif request.method == 'GET':
        return redirect('http://127.0.0.1:8000/')

def student_selection_view(request):
    return render(request, 'student_selection.html') 
