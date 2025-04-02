from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

def home_view(request):
    if request.user.is_authenticated:
        return redirect('accommodation_list')
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
            elif user.is_property_owner:
                return redirect('accommodation_list')
            elif user.is_cedars_staff or user.is_admin:
                return redirect(reverse('admin:index'))
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'login.html')
    
    return render(request, 'login.html')

@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def student_selection_view(request):
    return render(request, 'student_selection.html')


def reserve_view(request):
    return render(request, 'reserve.html')  

def rate_view(request):
    return render(request, 'rate.html')  