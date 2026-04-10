from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Teacher, Student, Class, Subject,
    Enrollment, Attendance, Grade,
    FeeStructure, FeePayment, Timetable
)


# ── User ──────────────────────────────────────────────────
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Columns shown in the user list
    list_display  = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter   = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Add 'role' field to the user edit form
    fieldsets = UserAdmin.fieldsets + (
        ('School Info', {
            'fields': ('role', 'phone_number', 'address', 'profile_pic')
        }),
    )

    # Add 'role' field to the create user form
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('School Info', {
            'fields': ('role', 'phone_number', 'address', 'profile_pic')
        }),
    )


# ── Teacher ───────────────────────────────────────────────
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display  = ('user', 'employee_id', 'qualification', 'date_joined')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'employee_id')


# ── Student ───────────────────────────────────────────────
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ('user', 'admission_number', 'guardian_name', 'guardian_phone', 'date_admitted')
    search_fields = ('user__username', 'user__first_name', 'admission_number')
    list_filter   = ('date_admitted',)


# ── Class ─────────────────────────────────────────────────
@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display  = ('name', 'grade_level', 'class_teacher')
    search_fields = ('name',)
    list_filter   = ('grade_level',)


# ── Subject ───────────────────────────────────────────────
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display  = ('name', 'code', 'class_name', 'teacher')
    search_fields = ('name', 'code')
    list_filter   = ('class_name',)


# ── Enrollment ────────────────────────────────────────────
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display  = ('student', 'class_name', 'session', 'date_enrolled')
    search_fields = ('student__user__username', 'session')
    list_filter   = ('session', 'class_name')


# ── Attendance ────────────────────────────────────────────
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display  = ('student', 'subject', 'date', 'status')
    search_fields = ('student__user__username',)
    list_filter   = ('status', 'date', 'subject')

    # Makes it easy to change status directly from the list
    list_editable = ('status',)


# ── Grade ─────────────────────────────────────────────────
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display  = ('student', 'subject', 'term', 'score', 'grade_letter')
    search_fields = ('student__user__username', 'subject__name')
    list_filter   = ('term', 'grade_letter', 'subject')
    list_editable = ('score',)


# ── Fee Structure ─────────────────────────────────────────
@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display  = ('class_name', 'term', 'amount', 'description')
    search_fields = ('class_name__name', 'term')
    list_filter   = ('term', 'class_name')


# ── Fee Payment ───────────────────────────────────────────
@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display  = ('student', 'fee_structure', 'amount_paid', 'date', 'receipt_number')
    search_fields = ('student__user__username', 'receipt_number')
    list_filter   = ('date', 'fee_structure')


# ── Timetable ─────────────────────────────────────────────
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display  = ('class_name', 'subject', 'day', 'start_time', 'end_time')
    search_fields = ('class_name__name', 'subject__name')
    list_filter   = ('day', 'class_name')
