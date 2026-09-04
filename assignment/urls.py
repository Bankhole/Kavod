from django.urls import path
from . import views

app_name = 'assignment'

urlpatterns = [
    path('', views.assignment_list, name='list'),
    path('submit/<int:pk>/', views.submit_assignment_ajax, name='submit'),
]
