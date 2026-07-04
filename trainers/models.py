from django.db import models
from django.conf import settings


class TrainerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=150, blank=True, null=True)
    experience = models.PositiveIntegerField(default=0)
    specialization = models.CharField(max_length=150, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    
from django.conf import settings
from django.db import models

from batches.models import Batch
from students.models import StudentProfile


class ClassSession(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="class_sessions")
    title = models.CharField(max_length=150)
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    meeting_link = models.URLField(blank=True)
    recording_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "Trainer"},
        related_name="created_class_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-session_date", "-start_time"]

    def __str__(self):
        return f"{self.batch} - {self.title}"


class TrainerAttendance(models.Model):
    STATUS_CHOICES = (
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Late", "Late"),
    )

    session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name="trainer_attendance_records",
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="trainer_attendance_records",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Present")
    remarks = models.CharField(max_length=200, blank=True)
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("session", "student")

    def __str__(self):
        return f"{self.student} - {self.session} - {self.status}"


class Assignment(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    total_marks = models.PositiveIntegerField(default=100)
    attachment_url = models.URLField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "Trainer"},
        related_name="created_assignments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-due_date"]

    def __str__(self):
        return f"{self.batch} - {self.title}"


class AssignmentEvaluation(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="evaluations")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="assignment_evaluations")
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    evaluated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("assignment", "student")


class Exam(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="exams")
    title = models.CharField(max_length=150)
    exam_date = models.DateField()
    total_marks = models.PositiveIntegerField(default=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "Trainer"},
        related_name="created_exams",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-exam_date"]

    def __str__(self):
        return f"{self.batch} - {self.title}"


class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="exam_results")
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("exam", "student")
