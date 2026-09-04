# Create your models here.

# models.py
from django.db import models

class AdmissionApplication(models.Model):
    CLASS_CHOICES = [
        ('nursery', 'Nursery'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
    ]

    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    parent_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    target_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    previous_school = models.CharField(max_length=200, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.target_class}"