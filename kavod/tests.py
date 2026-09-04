from django.test import SimpleTestCase


class AuthenticationPageTests(SimpleTestCase):
    def test_root_page_shows_login_form(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login to Your Account')

    def test_register_page_is_available_without_login(self):
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')

    def test_protected_pages_redirect_anonymous_users_to_login(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/about/')
