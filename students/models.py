from django.db import models
from django.conf import settings
from batches.models import Batch


class StudentProfile(models.Model):

    STATUS_CHOICES = (
        ('Approval Pending', 'Approval Pending'),
        ('Upcoming', 'Upcoming'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Dropped', 'Dropped'),
        ('Inactive', 'Inactive'),
    )

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    student_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students"
    )

    counselor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'Counselor'},
        related_name='assigned_students'
    )

    admission_date = models.DateField(
        null=True,
        blank=True
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    qualification = models.CharField(
        max_length=150,
        blank=True
    )

    college = models.CharField(
        max_length=150,
        blank=True
    )

    guardian_name = models.CharField(
        max_length=100,
        blank=True
    )

    guardian_phone = models.CharField(
        max_length=15,
        blank=True
    )

    emergency_contact = models.CharField(
        max_length=15,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    pincode = models.CharField(
        max_length=10,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Approval Pending'
    )

    remarks = models.TextField(
        blank=True,
        help_text="Private counselor notes"
    )

    is_deleted = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        """
        Auto-generate Student ID.
        Example:
        STU0001
        STU0002
        """
        if not self.student_id:
            last_id = StudentProfile.objects.count() + 1
            self.student_id = f"STU{last_id:04d}"

        super().save(*args, **kwargs)

    @property
    def has_pending_batch_request(self):
        return self.batch_assignment_requests.filter(status="Pending").exists()

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"
    
from django.conf import settings
from django.db import models

from batches.models import Batch


class BatchAssignmentRequest(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    )

    student = models.ForeignKey(
        "StudentProfile",
        on_delete=models.CASCADE,
        related_name="batch_assignment_requests",
    )
    current_batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_batch_transfer_from_requests",
    )
    requested_batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="student_batch_assignment_requests",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "Counselor"},
        related_name="batch_assignment_requests_sent",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "Assistant Manager"},
        related_name="batch_assignment_requests_reviewed",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    request_note = models.TextField(blank=True)
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.student_id} -> {self.requested_batch} ({self.status})"


from django.db import models

from batches.models import Batch
from students.models import StudentProfile


class StudentFee(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Partially Paid", "Partially Paid"),
        ("Paid", "Paid"),
        ("Overdue", "Overdue"),
    )

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="learning_fee_records")
    title = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.student.student_id} - {self.title}"


class PaymentProof(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    )

    fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name="payment_proofs")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="learning_payment_proofs")
    transaction_id = models.CharField(max_length=100, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    proof_file = models.FileField(upload_to="payment_proofs/")
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]


class StudentFeedback(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="learning_feedback_entries")
    session = models.ForeignKey(
        "trainers.ClassSession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="learning_student_feedback_entries",
    )
    rating = models.PositiveSmallIntegerField(default=5)
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class StudentRequest(models.Model):
    REQUEST_TO_CHOICES = (
        ("Counselor", "Counselor"),
        ("Trainer", "Trainer"),
    )
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Rejected", "Rejected"),
    )

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="learning_requests")
    request_to = models.CharField(max_length=20, choices=REQUEST_TO_CHOICES)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class StudentEvent(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    event_date = models.DateField()
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True, related_name="learning_events")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["event_date"]

    def __str__(self):
        return self.title


class StudentNotification(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="learning_notifications")
    title = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.student_id} - {self.title}"
