from django.contrib.auth import get_user_model
from django.test import TestCase


class ProfilePageTests(TestCase):
    def test_authenticated_user_can_open_profile_page(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username='student',
            email='student@example.com',
            password='securepass123',
        )

        self.client.force_login(user)
        response = self.client.get('/accounts/profile/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Your Profile')
