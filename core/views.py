from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# ── Login ─────────────────────────────────────────────────
def user_login(request):
    # If already logged in, redirect to their dashboard
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:          # ✅ fixed capitalisation
            login(request, user)
            return redirect_by_role(user)
        else:
            messages.error(request, 'Invalid username or password.')  # ✅ added

    return render(request, 'login.html')


# ── Logout ────────────────────────────────────────────────
def user_logout(request):
    logout(request)
    return redirect('login')


# ── Role redirect helper ───────────────────────────────────
def redirect_by_role(user):
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'teacher':
        return redirect('teacher_dashboard')
    elif user.role == 'student':
        return redirect('student_dashboard')
    else:
        return redirect('login')


# ── Dashboards ────────────────────────────────────────────
@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':      # stop teachers accessing admin
        return redirect('login')
    return render(request, 'admin_dashboard.html')


@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('login')
    return render(request, 'teacher_dashboard.html')


@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('login')
    return render(request, 'student_dashboard.html')
