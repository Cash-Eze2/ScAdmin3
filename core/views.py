from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Student, Teacher, Class, Subject, Attendance, Grade, FeePayment, FeeStructure, Timetable


# ── Login ─────────────────────────────────────────────────
def user_login(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect_by_role(user)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


# ── Logout ────────────────────────────────────────────────
def user_logout(request):
    logout(request)
    return redirect('login')


# ── Role redirect helper ──────────────────────────────────
def redirect_by_role(user):
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'teacher':
        return redirect('teacher_dashboard')
    elif user.role == 'student':
        return redirect('student_dashboard')
    else:
        return redirect('login')


# ── Admin Dashboard ───────────────────────────────────────
@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('login')

    today = timezone.now().date()

    # Count totals
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_classes  = Class.objects.count()

    # Fee stats
    total_fees_expected   = sum(f.amount for f in FeeStructure.objects.all())
    total_fees_collected  = sum(p.amount_paid for p in FeePayment.objects.all())
    total_fees_outstanding = total_fees_expected - total_fees_collected
    pending_fees = Student.objects.filter(
        feepayment__isnull=True
    ).distinct().count()

    # Attendance today
    today_attendance = Attendance.objects.filter(date=today)
    present_count = today_attendance.filter(status='present').count()
    absent_count  = today_attendance.filter(status='absent').count()
    late_count    = today_attendance.filter(status='late').count()
    total_today   = today_attendance.count()

    # Percentages (avoid dividing by zero)
    present_pct = round((present_count / total_today) * 100) if total_today else 0
    absent_pct  = round((absent_count  / total_today) * 100) if total_today else 0
    late_pct    = round((late_count    / total_today) * 100) if total_today else 0

    # Recent students (last 5 added)
    recent_students = Student.objects.select_related('user').order_by('-id')[:5]

    context = {
        'total_students':        total_students,
        'total_teachers':        total_teachers,
        'total_classes':         total_classes,
        'pending_fees':          pending_fees,
        'total_fees_expected':   total_fees_expected,
        'total_fees_collected':  total_fees_collected,
        'total_fees_outstanding': total_fees_outstanding,
        'present_pct':           present_pct,
        'absent_pct':            absent_pct,
        'late_pct':              late_pct,
        'recent_students':       recent_students,
    }
    return render(request, 'admin_dashboard.html', context)


# ── Teacher Dashboard ─────────────────────────────────────
@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('login')

    today = timezone.now().date()

    # Get this teacher's profile
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        teacher = None

    my_class    = Class.objects.filter(class_teacher=teacher).first() if teacher else None
    my_subjects = Subject.objects.filter(teacher=teacher).count() if teacher else 0

    # Students in teacher's class
    my_students_list = []
    my_students_count = 0
    if my_class:
        enrollments = my_class.enrollment_set.select_related('student__user')
        my_students_list  = [e.student for e in enrollments]
        my_students_count = len(my_students_list)

    # Today's attendance count for teacher's class
    today_attendance = 0
    if my_class:
        today_attendance = Attendance.objects.filter(
            student__enrollment__class_name=my_class,
            date=today,
            status='present'
        ).count()

    # Today's timetable for teacher
    day_name = today.strftime('%A').lower()   # e.g. 'monday'
    todays_timetable = Timetable.objects.filter(
        subject__teacher=teacher,
        day=day_name
    ).select_related('subject', 'class_name').order_by('start_time') if teacher else []

    context = {
        'teacher':           teacher,
        'my_class':          my_class,
        'my_subjects':       my_subjects,
        'my_students':       my_students_count,
        'my_students_list':  my_students_list,
        'today_attendance':  today_attendance,
        'todays_timetable':  todays_timetable,
        'pending_grades':    0,   # you can expand this later
    }
    return render(request, 'teacher_dashboard.html', context)


# ── Student Dashboard ─────────────────────────────────────
@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('login')

    today = timezone.now().date()

    # Get this student's profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None

    # Timetable for today
    todays_timetable = []
    total_subjects   = 0
    if student:
        enrollment = student.enrollment_set.first()
        if enrollment:
            day_name = today.strftime('%A').lower()
            todays_timetable = Timetable.objects.filter(
                class_name=enrollment.class_name,
                day=day_name
            ).select_related('subject__teacher__user').order_by('start_time')
            total_subjects = Subject.objects.filter(
                class_name=enrollment.class_name
            ).count()

    # Attendance stats
    present_count = 0
    absent_count  = 0
    late_count    = 0
    attendance_pct = 0
    if student:
        present_count = Attendance.objects.filter(student=student, status='present').count()
        absent_count  = Attendance.objects.filter(student=student, status='absent').count()
        late_count    = Attendance.objects.filter(student=student, status='late').count()
        total_att     = present_count + absent_count + late_count
        attendance_pct = round((present_count / total_att) * 100) if total_att else 0

    # Grades
    recent_grades = []
    avg_grade     = '—'
    if student:
        recent_grades = Grade.objects.filter(
            student=student
        ).select_related('subject').order_by('-id')[:5]

        all_grades = Grade.objects.filter(student=student)
        if all_grades.exists():
            avg = sum(g.score for g in all_grades) / all_grades.count()
            avg_grade = round(avg, 1)

    # Fee status
    total_fee    = 0
    amount_paid  = 0
    fee_balance  = 0
    if student:
        enrollment = student.enrollment_set.first()
        if enrollment:
            fee_structures = FeeStructure.objects.filter(
                class_name=enrollment.class_name
            )
            total_fee   = sum(f.amount for f in fee_structures)
            amount_paid = sum(
                p.amount_paid for p in FeePayment.objects.filter(student=student)
            )
            fee_balance = total_fee - amount_paid

    context = {
        'student_profile':   student,
        'todays_timetable':  todays_timetable,
        'total_subjects':    total_subjects,
        'present_count':     present_count,
        'absent_count':      absent_count,
        'late_count':        late_count,
        'attendance_pct':    attendance_pct,
        'recent_grades':     recent_grades,
        'avg_grade':         avg_grade,
        'total_fee':         total_fee,
        'amount_paid':       amount_paid,
        'fee_balance':       fee_balance,
    }
    return render(request, 'student_dashboard.html', context)
