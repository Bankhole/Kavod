# Create your models here.
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='courses_heading'
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"


class Lesson(models.Model):
    LESSON_TYPES = (
        ('recorded', 'Recorded Lesson'),
        ('live', 'Live Class'),
        ('tutorial', 'Video Tutorial'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=15, choices=LESSON_TYPES, default='recorded')
    order = models.PositiveIntegerField(default=1)
    is_preview = models.BooleanField(default=False, help_text="Is this lesson accessible for free preview?")

    # Common Video Content
    video_url = models.URLField(blank=True, null=True, help_text="Embed link or streaming URL (HLS/Vimeo/YouTube)")
    video_file = models.FileField(upload_to='lessons/videos/', blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=0)

    # Live Class Fields
    live_start_time = models.DateTimeField(blank=True, null=True)
    live_meeting_url = models.URLField(blank=True, null=True, help_text="Zoom, Google Meet, or WebRTC link")
    
    # Supplementary Content
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    @property
    def is_live_now(self):
        if self.lesson_type == 'live' and self.live_start_time:
            now = timezone.now()
            # Active if within scheduled window (assuming duration)
            end_time = self.live_start_time + timezone.timedelta(minutes=self.duration_minutes or 60)
            return self.live_start_time <= now <= end_time
        return False

    def __str__(self):
        return f"[{self.get_lesson_type_display()}] {self.title}"


class StudentEnrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')


class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    last_watched_seconds = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')