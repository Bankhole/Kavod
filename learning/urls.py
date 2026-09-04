from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:course_slug>/lessons/<uuid:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('progress/<uuid:lesson_id>/', views.update_lesson_progress, name='update_lesson_progress'),
]
