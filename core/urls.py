from django.urls import path
from . import views

urlpatterns = [
    path('/', views.user_login, name='login'),
    path('login/', views.user_login, name='login'),
    path('admin_dashbord', views.user, name='admin_dashboard'),
    path('teacher_dashboard', views.user, name='teacher'),
    path('student_dashboard', views.user, name='student'),
]
