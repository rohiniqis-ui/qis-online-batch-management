from django.db import models
from django.conf import settings
from students.models import StudentProfile


class Request(models.Model):
    REQUEST_TYPE_CHOICES = (
        ('Academic', 'Academic'),
        ('Fee', 'Fee'),
        ('Batch Change', 'Batch Change'),
        ('Leave', 'Leave'),
        ('Technical Issue', 'Technical Issue'),
        ('Other', 'Other'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Escalated', 'Escalated'),
        ('Resolved', 'Resolved'),
    )

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPE_CHOICES)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests'
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.request_type}"