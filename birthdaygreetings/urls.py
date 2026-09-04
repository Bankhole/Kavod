from django.urls import path
from . import views

app_name = 'birthdaygreetings'

urlpatterns = [
    path('today/', views.today_birthdays_view, name='today_birthdays'),
]
