# accounts/urls.py
from django.urls import path
from .views import (
    UserRegisterView, UserLoginView, UserLogoutView, LogoutSuccessView,
    EditProfileView, dashboard_redirect, teacher_dashboard, student_dashboard,
    parent_dashboard,
)

app_name = 'accounts'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('logout/success/', LogoutSuccessView.as_view(), name='logout_success'),
    path('profile/', EditProfileView.as_view(), name='profile'),
    path('dashboard/', dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/teacher/', teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', student_dashboard, name='student_dashboard'),
    path('dashboard/parent/', parent_dashboard, name='parent_dashboard'),
]
