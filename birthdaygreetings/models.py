from django.db import models
from django.conf import settings
from django.utils import timezone


class BirthdayProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff/Teacher'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='birthday_profile'
    )
    date_of_birth = models.DateField()
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    grade_or_department = models.CharField(max_length=100, blank=True, help_text='e.g., Grade 10 or Science Dept')
    profile_picture = models.ImageField(upload_to='birthdays/', blank=True, null=True)
    custom_message = models.CharField(
        max_length=255,
        blank=True,
        help_text='Optional special greeting message from administration.'
    )

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.date_of_birth})"

    @property
    def is_birthday_today(self):
        today = timezone.now().date()
        return self.date_of_birth.month == today.month and self.date_of_birth.day == today.day
