from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


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


class UserAdminTests(TestCase):
    def test_admin_can_create_user_without_duplicate_profile(self):
        admin_user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='securepass123',
        )
        self.client.force_login(admin_user)

        response = self.client.post(
            reverse('admin:accounts_user_add'),
            {
                'username': 'newstudent',
                'email': 'newstudent@example.com',
                'role': 'STUDENT',
                'password1': 'securepass123',
                'password2': 'securepass123',
            },
        )

        self.assertEqual(response.status_code, 302)
        created_user = get_user_model().objects.get(username='newstudent')
        self.assertEqual(created_user.profile.user_id, created_user.id)


class RegistrationPageTests(TestCase):
    def test_registration_form_includes_csrf_token(self):
        response = self.client.get(reverse('accounts:register'))

        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_registration_accepts_csrf_protected_post(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get(reverse('accounts:register'))
        csrf_token = response.cookies['csrftoken'].value

        response = client.post(
            reverse('accounts:register'),
            {
                'csrfmiddlewaretoken': csrf_token,
                'username': 'registereduser',
                'email': 'registered@example.com',
                'role': 'STUDENT',
            },
        )

        self.assertRedirects(response, reverse('accounts:login'))
        self.assertFalse(get_user_model().objects.get(username='registereduser').has_usable_password())

    def test_authenticated_navbar_hides_dashboard_links(self):
        user = get_user_model().objects.create_user(
            username='navuser',
            email='navuser@example.com',
            password='securepass123',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertNotContains(response, 'My Dashboard')
        self.assertNotContains(response, 'Payments Dashboard')
        self.assertNotContains(response, 'Admin Dashboard')


class GroupDashboardRenderTests(TestCase):
    """Regression tests: fully render each group dashboard so any bad
    {% url %} tag (e.g. NoReverseMatch) is caught by CI instead of in prod."""

    def _make_user(self, role, username):
        return get_user_model().objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='securepass123',
            role=role,
        )

    def test_teacher_dashboard_renders(self):
        user = self._make_user('TEACHER', 'teacher_smoke')
        self.client.force_login(user)
        response = self.client.get(reverse('accounts:teacher_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_student_dashboard_renders(self):
        user = self._make_user('STUDENT', 'student_smoke')
        self.client.force_login(user)
        response = self.client.get(reverse('accounts:student_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_parent_dashboard_renders(self):
        user = self._make_user('PARENT', 'parent_smoke')
        self.client.force_login(user)
        response = self.client.get(reverse('accounts:parent_dashboard'))
        self.assertEqual(response.status_code, 200)
