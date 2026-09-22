<<<<<<< HEAD
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase

from .models import Quiz


class ExamsTemplateTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_quiz_list_template_renders_for_authenticated_users(self):
        quiz = Quiz.objects.create(title="Sample Quiz")
        request = self.factory.get("/exams/")
        request.user = AnonymousUser()

        html = render_to_string(
            "exams/quiz_list.html",
            {
                "quizzes": [quiz],
                "page_title": "Available Exams",
                "request": request,
            },
            request=request,
        )

        self.assertIn("Sample Quiz", html)
=======
from django.test import TestCase

# Create your tests here.
>>>>>>> a79162f0f57a88911ff8216bfa0a9b5b9f1aa1a5
