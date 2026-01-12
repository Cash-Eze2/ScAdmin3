from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# app views

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not none:
            login(request,user)

            if hasattr(user, 'role'):
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.role == 'teacher':
                    return redirect('teacher_dashboard')
                else:
                    messages.error(request, "Invalid credentials")
                    return render(request,'login.html')
    return render(request, 'login.html')


@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def teacher_dashboard(request):
    return render(request, 'teacher_dashboard.html')

@login_required
def student_dashboard(request):
    return render(request, 'student_dashboard.html')

