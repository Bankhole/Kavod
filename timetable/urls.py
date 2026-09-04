from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.classroom_list, name='classroom_list'),
    path('<int:classroom_id>/', views.timetable_view, name='grid'),
]
