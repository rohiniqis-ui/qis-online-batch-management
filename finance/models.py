from django.db import models
from django.conf import settings
from students.models import StudentProfile


class FeePayment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Partially Paid', 'Partially Paid'),
        ('Paid', 'Paid'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    )

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_proof = models.FileField(upload_to='payment_proofs/', blank=True, null=True)
    payment_status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending'
    )
    payment_date = models.DateField(blank=True, null=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'Admin'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.balance_amount = self.total_fee - self.paid_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.username} - {self.payment_status}"