from django.db import models
from django.conf import settings
from batches.models import Batch
from students.models import StudentProfile


class Assignment(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Trainer'}
    )
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Submitted', 'Submitted'),
        ('Evaluated', 'Evaluated'),
        ('Late Submitted', 'Late Submitted'),
    )

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    submission_file = models.FileField(upload_to='assignment_submissions/', blank=True, null=True)
    submission_link = models.URLField(blank=True, null=True)
    marks = models.PositiveIntegerField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title}"