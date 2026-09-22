from django.test import TestCase


class AuthenticationPageTests(TestCase):
    def test_root_page_redirects_anonymous_users_to_registration(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/accounts/register/')

    def test_anonymous_users_do_not_see_the_navbar(self):
        response = self.client.get('/accounts/login/')
        self.assertNotContains(response, '<nav class="navbar')

    def test_register_page_is_available_without_login(self):
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete Registration')

    def test_protected_pages_redirect_anonymous_users_to_login(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/about/')
