from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Student, StudentClass


class AttendanceViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='secret123',
            role='TEACHER',
        )

    def test_attendance_dashboard_requires_login(self):
        response = self.client.get('/attendance/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/attendance/')

    def test_attendance_dashboard_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get('/attendance/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class Attendance')

    def test_student_can_view_read_only_attendance(self):
        student_user = get_user_model().objects.create_user(
            username='student', email='student@example.com', password='secret123',
            role='STUDENT', first_name='Ada', last_name='Student',
        )
        student_class = StudentClass.objects.create(name='Grade 10')
        Student.objects.create(
            student_class=student_class, roll_number='STU-001',
            first_name='Ada', last_name='Student',
        )
        self.client.force_login(student_user)

        response = self.client.get('/attendance/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Attendance')
        self.assertNotContains(response, 'Save Attendance')
