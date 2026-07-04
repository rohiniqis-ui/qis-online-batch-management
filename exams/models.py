from django.db import models
from batches.models import Batch
from students.models import StudentProfile


class Exam(models.Model):
    exam_name = models.CharField(max_length=100)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    total_marks = models.PositiveIntegerField()
    exam_date = models.DateField()

    def __str__(self):
        return f"{self.exam_name} - {self.batch.batch_name}"


class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    marks_obtained = models.PositiveIntegerField()
    grade = models.CharField(max_length=10, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.exam_name}"