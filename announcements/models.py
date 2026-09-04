# Create your models here.
from django.db import models
from django.conf import settings

class Announcement(models.Model):
    AUDIENCE_CHOICES = [
        ('ALL', 'All'),
        ('STUDENTS', 'Students Only'),
        ('TEACHERS', 'Teachers Only'),
        ('PARENTS', 'Parents Only'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    target_audience = models.CharField(max_length=10, choices=AUDIENCE_CHOICES, default='ALL')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='announcements')
    
    is_important = models.BooleanField(default=False, help_text="Pin this announcement to top")
    is_published = models.BooleanField(default=True)
    
    attachment = models.FileField(upload_to='announcements/attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_important', '-created_at']

    def __str__(self):
        return self.title