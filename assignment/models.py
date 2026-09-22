# Create your models here.
from django.conf import settings
from django.db import models

from attendance.models import StudentClass

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    student_class = models.ForeignKey(
        StudentClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments',
        help_text='Leave blank to make this assignment available to all students.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submission_text = models.TextField(blank=True)
    file_upload = models.FileField(upload_to='assignments/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('assignment', 'student'), name='unique_assignment_submission'),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"