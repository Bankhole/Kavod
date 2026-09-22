# attendance/urls.py
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_dashboard, name='dashboard'),
    path('my-attendance/', views.student_attendance, name='student_attendance'),
    path('api/get-students/', views.get_students, name='get_students'),
    path('api/save-attendance/', views.save_attendance, name='save_attendance'),
    path('my-children/', views.parent_attendance, name='parent_attendance'),
]