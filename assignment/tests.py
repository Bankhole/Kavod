from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase

from attendance.models import StudentClass

from .models import Assignment, Submission


class AssignmentSubmissionTests(TestCase):
	def setUp(self):
		self.grade_one = StudentClass.objects.create(name='Grade 1')
		self.grade_two = StudentClass.objects.create(name='Grade 2')
		self.student = get_user_model().objects.create_user(
			username='assignment_student',
			email='assignment_student@example.com',
			password='securepass123',
			role='STUDENT',
		)
		self.student.profile.student_class = self.grade_one
		self.student.profile.save(update_fields=['student_class'])
		self.assignment = Assignment.objects.create(
			title='Reading task',
			description='Read chapter one.',
			due_date=timezone.now() + timedelta(days=2),
			student_class=self.grade_one,
		)

	def test_student_sees_only_assignments_for_their_class(self):
		Assignment.objects.create(
			title='Other class task',
			description='Not for this student.',
			due_date=timezone.now() + timedelta(days=2),
			student_class=self.grade_two,
		)
		self.client.force_login(self.student)

		response = self.client.get('/assignments/')

		self.assertContains(response, 'Reading task')
		self.assertNotContains(response, 'Other class task')

	def test_student_can_submit_and_update_assignment(self):
		self.client.force_login(self.student)

		response = self.client.post(
			f'/assignments/submit/{self.assignment.pk}/',
			{'submission_text': 'My first answer.'},
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Submission.objects.filter(assignment=self.assignment, student=self.student).count(), 1)

		self.client.post(
			f'/assignments/submit/{self.assignment.pk}/',
			{'submission_text': 'My revised answer.'},
		)
		submission = Submission.objects.get(assignment=self.assignment, student=self.student)
		self.assertEqual(submission.submission_text, 'My revised answer.')
		self.assertEqual(Submission.objects.filter(assignment=self.assignment, student=self.student).count(), 1)
