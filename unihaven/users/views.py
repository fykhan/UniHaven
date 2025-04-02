from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User

def home_view(request):
    user = request.user
    if user.is_authenticated and not user.is_anonymous:
        if user.is_student:
            return redirect('student_selection')
        elif user.is_cedars_staff:
            return redirect('cedars_dashboard')
    return redirect('login')

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
            elif user.is_cedars_staff:
                return redirect('cedars_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'login.html')
    return render(request, 'login.html')

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout successful'})
    elif request.method == 'GET':
        logout(request)
        return redirect('home')

def student_selection_view(request):
    return render(request, 'student_selection.html')

@login_required
@user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.is_cedars_staff))
def cedars_dashboard_view(request):
    return render(request, 'cedars_dashboard.html')
