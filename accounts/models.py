from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin/Staff'
        TEACHER = 'TEACHER', 'Teacher'
        STUDENT = 'STUDENT', 'Student'
        PARENT = 'PARENT', 'Parent'

    role = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.STUDENT,
    )
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


def generate_access_code():
    """A short, unique code the admin hands out for a new user to log in with."""
    return f"NX-{secrets.token_hex(4).upper()}"


def _generate_unique_access_code():
    code = generate_access_code()
    while Profile.objects.filter(access_code=code).exists():
        code = generate_access_code()
    return code


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    student_id_or_staff_code = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    postal_code = models.CharField(max_length=20, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='Nigeria')
    access_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text='Unique login code generated at registration, issued out by the admin.',
    )

    class Meta:
        permissions = [
            ('access_teacher_dashboard', 'Can access teacher dashboard'),
            ('access_student_dashboard', 'Can access student dashboard'),
            ('access_parent_dashboard', 'Can access parent dashboard'),
            ('manage_school_operations', 'Can manage school operations (invoices, results, timetable admin)'),
        ]

    def __str__(self):
        return f"Profile for {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, _ = Profile.objects.get_or_create(user=instance)
        if not profile.access_code:
            profile.access_code = _generate_unique_access_code()
            profile.save(update_fields=['access_code'])


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    profile, _ = Profile.objects.get_or_create(user=instance)
    profile.save()


@receiver(post_save, sender=User)
def assign_default_group(sender, instance, created, **kwargs):
    """Seed a new user's Group membership from their `role` so admins immediately see it in /admin/.

    Only runs on creation: once a user exists, Group membership is managed via the
    admin panel and must not be silently overwritten on subsequent saves.
    """
    if not created:
        return
    from django.contrib.auth.models import Group
    from .permissions import ROLE_TO_GROUP

    group_name = ROLE_TO_GROUP.get(str(instance.role).upper())
    if group_name:
        group, _ = Group.objects.get_or_create(name=group_name)
        instance.groups.add(group)
