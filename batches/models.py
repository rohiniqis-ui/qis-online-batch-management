from django.db import models
from django.conf import settings


class Batch(models.Model):
    STATUS_CHOICES = (
        ('Upcoming', 'Upcoming'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Archived', 'Archived'),
    )

    batch_name = models.CharField(max_length=100)
    course_name = models.CharField(max_length=100)
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'Trainer'},
        related_name='assigned_batches'
    )
    assistant_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'Assistant Manager'},
        related_name='managed_batches'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    schedule = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Upcoming')
    syllabus_progress = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.batch_name