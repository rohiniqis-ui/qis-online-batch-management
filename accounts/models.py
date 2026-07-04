from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Assistant Manager', 'Assistant Manager'),
        ('Counselor', 'Counselor'),
        ('Trainer', 'Trainer'),
        ('Student', 'Student'),
    )

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.role}"