from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    # Exam hub: Lists all available quizzes (mounted at /exams/ in project urls)
    path('', views.quiz_list, name='quiz_list'),

    # Take Quiz: Displays the questions for a specific quiz
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),

    # Quiz Result: Displays the score after submission
    path('result/<int:result_id>/', views.quiz_result, name='quiz_result'),

    # Manual result sheet workflow
    path('results/upload/', views.manual_result_upload, name='manual_result_upload'),
    path('results/upload/<int:sheet_id>/edit/', views.manual_result_upload, name='edit_result_sheet'),
    path('results/check/', views.check_results, name='check_results'),
    path('results/sheet/<int:sheet_id>/', views.result_sheet_detail, name='result_sheet_detail'),
]