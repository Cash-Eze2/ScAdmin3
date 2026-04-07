from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('',         views.user_login,  name='login'),    # root page = login
    path('logout/',  views.user_logout, name='logout'),

    # Dashboards
    path('admin-dashboard/',   views.admin_dashboard,   name='admin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
]
