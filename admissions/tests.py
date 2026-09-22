from django.test import TestCase
from django.urls import reverse


class AdmissionViewTests(TestCase):
	def test_admission_form_renders_csrf_token(self):
		response = self.client.get(reverse('admissions:admission_apply'))

		self.assertContains(response, 'name="csrfmiddlewaretoken"')

	def test_admission_form_accepts_post_with_csrf_token(self):
		response = self.client.get(reverse('admissions:admission_apply'))
		csrf_token = response.cookies['csrftoken'].value

		response = self.client.post(
			reverse('admissions:admission_apply'),
			{
				'csrfmiddlewaretoken': csrf_token,
				'full_name': 'Test Student',
				'date_of_birth': '2015-01-01',
				'parent_name': 'Test Parent',
				'email': 'parent@example.com',
				'phone': '+2348000000000',
				'target_class': 'primary',
				'previous_school': '',
			},
		)

		self.assertRedirects(response, reverse('admissions:admission_apply'))
from django.test import TestCase

# Create your tests here.
