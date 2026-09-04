"""
URL configuration for Pyshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Core site pages
    path('', views.home, name='home'),
    path('login/', RedirectView.as_view(pattern_name='accounts:login', permanent=False)),
    path('about/', views.about, name='about'),
    path('academics/', views.academics, name='academics'),
    path('contact/', views.contact, name='contact'),

    # Authentication and user portal routes
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # App routes
    path('exams/', include('exams.urls')),
    path('attendance/', include('attendance.urls', namespace='attendance')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('learning/', include('learning.urls', namespace='learning')),
    path('announcements/', include('announcements.urls', namespace='announcements')),
    path('birthdays/', include('birthdaygreetings.urls', namespace='birthdaygreetings')),
    path('timetable/', include('timetable.urls', namespace='timetable')),
    path('assignments/', include('assignment.urls', namespace='assignment')),
    path('admissions/', include('admissions.urls', namespace='admissions')),
    path('admission/', include('admissions.urls', namespace='legacy_admissions')),
]
