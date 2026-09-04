from django.contrib.auth import get_user_model
from django.test import TestCase


class AttendanceViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='secret123',
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
