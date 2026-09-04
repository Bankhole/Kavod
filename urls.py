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
