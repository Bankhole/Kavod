from django.urls import path
from . import views

urlpatterns = [
    # Exam hub: Lists all available quizzes (mounted at /exams/ in project urls)
    path('', views.quiz_list, name='quiz_list'),

    # Take Quiz: Displays the questions for a specific quiz
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),

    # Quiz Result: Displays the score after submission
    path('result/<int:result_id>/', views.quiz_result, name='quiz_result'),
]