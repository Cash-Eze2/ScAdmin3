from django.db import models
from django.contrib.auth.models import AbstractUser


# ── Custom User ──────────────────────────────────────────
class User(AbstractUser):
    ROLES = (
        ('admin',   'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role           = models.CharField(max_length=10, choices=ROLES, default='admin')
    address        = models.TextField(max_length=200, blank=True, null=True)
    phone_number   = models.CharField(max_length=15, blank=True, null=True)
    profile_pic    = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"  # fixed: was self.user_type


# ── Teacher Profile ───────────────────────────────────────
class Teacher(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id     = models.CharField(max_length=20, unique=True, blank=True, null=True)
    qualification   = models.CharField(max_length=100, blank=True, null=True)
    date_joined     = models.DateField(auto_now_add=True)

    # removed address & phone_number — already on User

    def __str__(self):
        return f"Teacher: {self.user.get_full_name() or self.user.username}"


# ── Student Profile ───────────────────────────────────────
class Student(models.Model):
    user             = models.OneToOneField(User, on_delete=models.CASCADE)
    admission_number = models.CharField(max_length=20, unique=True)
    date_of_birth    = models.DateField(blank=True, null=True)
    guardian_name    = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone   = models.CharField(max_length=15, blank=True, null=True)
    date_admitted    = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Student: {self.user.get_full_name() or self.user.username} ({self.admission_number})"


# ── Class ─────────────────────────────────────────────────
class Class(models.Model):
    name          = models.CharField(max_length=50)        # e.g. "Grade 3A"
    grade_level   = models.IntegerField()                  # e.g. 3
    class_teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.name


# ── Subject ───────────────────────────────────────────────
class Subject(models.Model):
    name       = models.CharField(max_length=100)
    code       = models.CharField(max_length=10, unique=True)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subjects')
    teacher    = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


# ── Enrollment (Student ↔ Class) ──────────────────────────
class Enrollment(models.Model):
    student       = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_name    = models.ForeignKey(Class, on_delete=models.CASCADE)
    session       = models.CharField(max_length=20
                                     )        # e.g. "2024/2025"
    date_enrolled = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'class_name', 'session')

    def __str__(self):
        return f"{self.student} → {self.class_name} ({self.session})"


# ── Attendance ────────────────────────────────────────────
class Attendance(models.Model):
    STATUS = (
        ('present', 'Present'),
        ('absent',  'Absent'),
        ('late',    'Late'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date    = models.DateField()
    status  = models.CharField(max_length=10, choices=STATUS, default='present')

    class Meta:
        unique_together = ('student', 'subject', 'date')

    def __str__(self):
        return f"{self.student} | {self.subject} | {self.date} — {self.status}"


# ── Grade ─────────────────────────────────────────────────
class Grade(models.Model):
    TERMS = (
        ('term1', 'Term 1'),
        ('term2', 'Term 2'),
        ('term3', 'Term 3'),
    )
    student      = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject      = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term         = models.CharField(max_length=10, choices=TERMS)
    score        = models.DecimalField(max_digits=5, decimal_places=2)
    grade_letter = models.CharField(max_length=2, blank=True)
    remarks      = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'subject', 'term')

    def save(self, *args, **kwargs):
        # Auto-assign grade letter on save
        if self.score >= 90:   self.grade_letter = 'A+'
        elif self.score >= 80: self.grade_letter = 'A'
        elif self.score >= 70: self.grade_letter = 'B'
        elif self.score >= 60: self.grade_letter = 'C'
        elif self.score >= 50: self.grade_letter = 'D'
        else:                  self.grade_letter = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} | {self.subject} | {self.term} — {self.grade_letter}"


# ── Fee Structure ─────────────────────────────────────────
class FeeStructure(models.Model):
    class_name  = models.ForeignKey(Class, on_delete=models.CASCADE)
    term        = models.CharField(max_length=10)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.class_name} | {self.term} — ${self.amount}"


# ── Fee Payment ───────────────────────────────────────────
class FeePayment(models.Model):
    student       = models.ForeignKey(Student, on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_paid   = models.DecimalField(max_digits=10, decimal_places=2)
    date          = models.DateField(auto_now_add=True)
    receipt_number = models.CharField(max_length=30, unique=True, blank=True)

    def __str__(self):
        return f"{self.student} | Receipt #{self.receipt_number}"


# ── Timetable ─────────────────────────────────────────────
class Timetable(models.Model):
    DAYS = (
        ('monday',    'Monday'),
        ('tuesday',   'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday',  'Thursday'),
        ('friday',    'Friday'),
    )
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject    = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day        = models.CharField(max_length=10, choices=DAYS)
    start_time = models.TimeField()
    end_time   = models.TimeField()

    class Meta:
        unique_together = ('class_name', 'day', 'start_time')

    def __str__(self):
        return f"{self.class_name} | {self.subject} | {self.day} {self.start_time}–{self.end_time}"
