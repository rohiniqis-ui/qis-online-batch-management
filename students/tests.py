from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from batches.models import Batch
from .models import BatchAssignmentRequest, StudentProfile


User = get_user_model()


class StudentBatchWorkflowTests(TestCase):
    def setUp(self):
        self.counselor = User.objects.create_user(
            username="counselor",
            email="counselor@example.com",
            password="StrongPass123",
            role="Counselor",
        )
        self.batch = Batch.objects.create(
            batch_name="Batch A",
            course_name="Python",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 2, 1),
            schedule="Weekdays",
            status="Upcoming",
        )
        self.client.force_login(self.counselor)

    def test_counselor_can_create_student_with_selected_batch(self):
        response = self.client.post(
            reverse("students:student_create"),
            {
                "username": "studentone",
                "first_name": "Student",
                "last_name": "One",
                "email": "studentone@example.com",
                "phone": "9876543210",
                "password": "StrongPass123",
                "batch": self.batch.pk,
                "status": "Approval Pending",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        student = StudentProfile.objects.get(user__username="studentone")
        self.assertEqual(student.batch, self.batch)
        self.assertEqual(student.status, "Approval Pending")
        self.assertIsNotNone(student.counselor)

    def test_counselor_can_request_batch_assignment_when_none_selected(self):
        response = self.client.post(
            reverse("students:student_create"),
            {
                "username": "studenttwo",
                "first_name": "Student",
                "last_name": "Two",
                "email": "studenttwo@example.com",
                "phone": "9876543210",
                "password": "StrongPass123",
                "status": "Approval Pending",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        student = StudentProfile.objects.get(user__username="studenttwo")
        self.assertIsNone(student.batch)
        self.assertEqual(student.status, "Approval Pending")

        request_response = self.client.post(
            reverse("students:student_batch_assign", args=[student.pk]),
            {"batch": self.batch.pk, "request_note": "Please assign this batch."},
            follow=True,
        )

        self.assertEqual(request_response.status_code, 200)
        request = BatchAssignmentRequest.objects.get(student=student)
        self.assertEqual(request.requested_batch, self.batch)
        self.assertEqual(request.status, "Pending")
        self.assertTrue(student.has_pending_batch_request)
