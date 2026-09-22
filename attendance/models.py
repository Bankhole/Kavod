# Create your models here.
# attendance/models.py
from django.conf import settings
from django.db import models

class AcademicSession(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., 2025/2026 First Term")
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class StudentClass(models.Model):
    name = models.CharField(max_length=50, help_text="e.g., Grade 10-A")

    def __str__(self):
        return self.name

class Student(models.Model):
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='students')
    roll_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        limit_choices_to={'role': 'PARENT'},
        help_text='Parent/guardian account allowed to view this student\'s attendance.',
    )

    class Meta:
        ordering = ['roll_number']

    def __str__(self):
        return f"{self.roll_number} - {self.first_name} {self.last_name}"

class AttendanceHeader(models.Model):
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'subject', 'student_class', 'date')

    def __str__(self):
        return f"{self.student_class} | {self.subject} | {self.date}"

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
    ]
    header = models.ForeignKey(AttendanceHeader, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f"{self.student} - {self.get_status_display()}"
