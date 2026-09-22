<<<<<<< HEAD
from django.urls import path, include
from kavod import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('admissions/', views.admissions, name='admissions'),
    path('academics/', views.academics, name='academics'),
    path('contact/', views.contact, name='contact'),
    path('payments/', include('payments.urls')),
    path('birthdays/', include('birthdaygreetings.urls')),
]
=======
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('admissions/', views.admissions, name='admissions'),
    path('academics/', views.academics, name='academics'),
    path('contact/', views.contact, name='contact'),
]
>>>>>>> a79162f0f57a88911ff8216bfa0a9b5b9f1aa1a5
