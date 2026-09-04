# admissions/urls.py (App-level URL configuration)
from django.urls import path
from .views import admission_view

app_name = 'admissions'

urlpatterns = [
    path('', admission_view, name='admission_apply'),
    path('apply/', admission_view, name='admission_apply_legacy'),
]