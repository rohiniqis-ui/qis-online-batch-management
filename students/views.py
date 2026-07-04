from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render

from batches.models import Batch

from .forms import BatchAssignmentRequestForm, BatchAssignmentReviewForm, StudentProfileForm
from .models import BatchAssignmentRequest, StudentProfile


def _role(user):
    return str(getattr(user, "role", "")).strip()


def _is_counselor(user):
    return _role(user) == "Counselor"


def _is_assistant_manager(user):
    return _role(user) == "Assistant Manager"


def _base_template_for_user(user):
    role = _role(user)
    if role == "Assistant Manager":
        return "includes/manager/base.html"
    if role == "Counselor":
        return "includes/counselor/base.html"
    if role == "Admin":
        return "includes/admin/base.html"
    return "base.html"


def _normalize_student_status(status):
    if status == "Pending":
        return "Approval Pending"
    return status


def _student_queryset_for_user(user):
    return StudentProfile.objects.select_related("user", "batch", "counselor").filter(
        is_deleted=False
    )


@login_required
def student_list(request):
    search_query = request.GET.get("q", "").strip()
    batch_id = request.GET.get("batch", "").strip()
    status = _normalize_student_status(request.GET.get("status", "").strip())

    students = _student_queryset_for_user(request.user).order_by("-created_at")

    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query)
            | Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(user__email__icontains=search_query)
        )

    if batch_id == "unassigned":
        students = students.filter(batch__isnull=True)
    elif batch_id:
        students = students.filter(batch_id=batch_id)

    if status:
        students = students.filter(status=status)

    paginator = Paginator(students, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    context = {
        "page_obj": page_obj,
        "batches": Batch.objects.all().order_by("id"),
        "status_choices": StudentProfile.STATUS_CHOICES,
        "search_query": search_query,
        "selected_batch": batch_id,
        "selected_status": status,
        "query_string": query_params.urlencode(),
        "is_counselor_portal": _is_counselor(request.user),
        "is_assistant_manager": _is_assistant_manager(request.user),
        "base_template": _base_template_for_user(request.user),
    }
    return render(request, "students/student_list.html", context)


@login_required
def student_detail(request, pk):
    student = get_object_or_404(_student_queryset_for_user(request.user), pk=pk)
    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
            "is_counselor_portal": _is_counselor(request.user),
            "base_template": _base_template_for_user(request.user),
        },
    )


@login_required
def student_create(request):
    if request.method == "POST":
        form = StudentProfileForm(request.POST, current_user=request.user)
        if form.is_valid():
            student = form.save()
            if _is_counselor(request.user) and not student.batch:
                messages.success(
                    request,
                    "Student profile created. Please request a batch assignment for approval.",
                )
            else:
                messages.success(request, f"Student {student.student_id} created successfully.")
            return redirect("students:student_detail", pk=student.pk)
        messages.error(request, "Please correct the errors below.")
    else:
        form = StudentProfileForm(current_user=request.user)

    return render(
        request,
        "students/student_form.html",
        {
            "form": form,
            "title": "Add Student",
            "button_label": "Create Student",
            "base_template": _base_template_for_user(request.user),
        },
    )


@login_required
def student_update(request, pk):
    student = get_object_or_404(_student_queryset_for_user(request.user), pk=pk)

    if request.method == "POST":
        form = StudentProfileForm(request.POST, instance=student, current_user=request.user)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student {student.student_id} updated successfully.")
            return redirect("students:student_detail", pk=student.pk)
        messages.error(request, "Please correct the errors below.")
    else:
        form = StudentProfileForm(instance=student, current_user=request.user)

    return render(
        request,
        "students/student_form.html",
        {
            "form": form,
            "student": student,
            "title": "Edit Student",
            "button_label": "Update Student",
            "base_template": _base_template_for_user(request.user),
        },
    )


@login_required
def student_delete(request, pk):
    student = get_object_or_404(_student_queryset_for_user(request.user), pk=pk)

    if request.method == "POST":
        student.is_deleted = True
        student.save(update_fields=["is_deleted", "updated_at"])
        messages.success(request, f"Student {student.student_id} deleted successfully.")
        return redirect("students:student_list")

    return render(
        request,
        "students/student_confirm_delete.html",
        {"student": student, "base_template": _base_template_for_user(request.user)},
    )


@login_required
def student_batch_assign(request, pk):
    if not _is_counselor(request.user):
        raise PermissionDenied

    student = get_object_or_404(_student_queryset_for_user(request.user), pk=pk)

    if request.method == "POST":
        form = BatchAssignmentRequestForm(request.POST, current_batch=student.batch)
        if form.is_valid():
            pending_exists = BatchAssignmentRequest.objects.filter(
                student=student,
                status="Pending",
            ).exists()
            if pending_exists:
                messages.error(request, "This student already has a pending batch request.")
                return redirect("students:student_detail", pk=student.pk)

            BatchAssignmentRequest.objects.create(
                student=student,
                current_batch=student.batch,
                requested_batch=form.cleaned_data["batch"],
                requested_by=request.user,
                request_note=form.cleaned_data.get("request_note", ""),
            )
            messages.success(request, "Batch assignment request sent for assistant manager approval.")
            return redirect("students:student_detail", pk=student.pk)
        messages.error(request, "Please select a valid batch.")
    else:
        form = BatchAssignmentRequestForm(current_batch=student.batch)

    return render(
        request,
        "students/student_batch_form.html",
        {
            "form": form,
            "student": student,
            "title": "Request Batch Transfer" if student.batch_id else "Request Batch Assignment",
            "button_label": "Send Request",
            "base_template": _base_template_for_user(request.user),
        },
    )


@login_required
def student_batch_transfer(request, pk):
    if not _is_counselor(request.user):
        raise PermissionDenied

    student = get_object_or_404(_student_queryset_for_user(request.user), pk=pk)

    return student_batch_assign(request, pk)


@login_required
def student_batch_remove(request, pk):
    if not _is_counselor(request.user):
        raise PermissionDenied

    student = get_object_or_404(_student_queryset_for_user(request.user), pk=pk)

    if request.method == "POST":
        old_batch = student.batch
        student.batch = None
        if _is_counselor(request.user):
            student.counselor = request.user
        student.save(update_fields=["batch", "counselor", "updated_at"])
        messages.success(request, f"Batch {old_batch or ''} removed from {student.student_id}.")
        return redirect("students:student_detail", pk=student.pk)

    return render(
        request,
        "students/student_batch_remove.html",
        {"student": student, "base_template": _base_template_for_user(request.user)},
    )


@login_required
def batch_assignment_request_list(request):
    if not (_is_assistant_manager(request.user) or _is_counselor(request.user)):
        raise PermissionDenied

    status = request.GET.get("status", "").strip()
    search_query = request.GET.get("q", "").strip()

    base_requests = BatchAssignmentRequest.objects.select_related(
        "student",
        "student__user",
        "current_batch",
        "requested_batch",
        "requested_by",
        "reviewed_by",
    ).order_by("-created_at")

    requests = base_requests

    if status:
        requests = requests.filter(status=status)

    if search_query:
        requests = requests.filter(
            Q(student__student_id__icontains=search_query)
            | Q(student__user__first_name__icontains=search_query)
            | Q(student__user__last_name__icontains=search_query)
            | Q(student__user__email__icontains=search_query)
            | Q(requested_batch__batch_name__icontains=search_query)
            | Q(requested_by__first_name__icontains=search_query)
            | Q(requested_by__last_name__icontains=search_query)
        )

    paginator = Paginator(requests, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "students/batch_assignment_request_list.html",
        {
            "page_obj": page_obj,
            "status_choices": BatchAssignmentRequest.STATUS_CHOICES,
            "selected_status": status,
            "search_query": search_query,
            "query_string": query_params.urlencode(),
            "base_template": _base_template_for_user(request.user),
            "total_requests": base_requests.count(),
            "pending_requests": base_requests.filter(status="Pending").count(),
            "approved_requests": base_requests.filter(status="Approved").count(),
            "rejected_requests": base_requests.filter(status="Rejected").count(),
        },
    )


@login_required
def batch_assignment_request_review(request, pk):
    if not _is_assistant_manager(request.user):
        raise PermissionDenied

    assignment_request = get_object_or_404(
        BatchAssignmentRequest.objects.select_related(
            "student",
            "student__user",
            "current_batch",
            "requested_batch",
            "requested_by",
        ),
        pk=pk,
    )

    if request.method == "POST":
        if assignment_request.status != "Pending":
            messages.info(request, "This request has already been reviewed.")
            return redirect("students:batch_assignment_request_list")

        form = BatchAssignmentReviewForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                assignment_request.status = (
                    "Approved" if form.cleaned_data["action"] == "approve" else "Rejected"
                )
                assignment_request.review_note = form.cleaned_data.get("review_note", "")
                assignment_request.reviewed_by = request.user
                assignment_request.reviewed_at = timezone.now()
                assignment_request.save(
                    update_fields=[
                        "status",
                        "review_note",
                        "reviewed_by",
                        "reviewed_at",
                        "updated_at",
                    ]
                )

                if assignment_request.status == "Approved":
                    student = assignment_request.student
                    student.batch = assignment_request.requested_batch
                    student.counselor = assignment_request.requested_by
                    student.status = "Upcoming"
                    student.save(update_fields=["batch", "counselor", "status", "updated_at"])

            messages.success(request, f"Request {assignment_request.status.lower()} successfully.")
            return redirect("students:batch_assignment_request_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = BatchAssignmentReviewForm()

    return render(
        request,
        "students/batch_assignment_request_review.html",
        {
            "form": form,
            "assignment_request": assignment_request,
            "base_template": _base_template_for_user(request.user),
        },
    )


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import StudentProfile


@login_required
def approval_students(request):
    students = StudentProfile.objects.filter(
        status="Approval Pending",
        is_deleted=False
    ).select_related("user", "batch")

    return render(
        request,
        "manager/approval_students.html",
        {"students": students}
    )


@login_required
def upcoming_students(request):
    students = StudentProfile.objects.filter(
        status="Upcoming",
        is_deleted=False
    ).select_related("user", "batch")

    return render(
        request,
        "manager/upcoming_students.html",
        {"students": students}
    )


@login_required
def ongoing_students(request):
    students = StudentProfile.objects.filter(
        status="Ongoing",
        is_deleted=False
    ).select_related("user", "batch")

    return render(
        request,
        "manager/ongoing_students.html",
        {"students": students}
    )


@login_required
def completed_students(request):
    students = StudentProfile.objects.filter(
        status="Completed",
        is_deleted=False
    ).select_related("user", "batch")

    return render(
        request,
        "manager/completed_students.html",
        {"students": students}
    )


def student_detail(request, pk):

    student = get_object_or_404(
        StudentProfile,
        pk=pk,
        is_deleted=False
    )

    return render(
        request,
        "manager/student_detail.html",
        {
            "student": student
        }
    )


def approve_student_request(request, request_id):

    batch_request = get_object_or_404(
        BatchAssignmentRequest,
        id=request_id,
        status="Pending"
    )


    batch_request.status = "Approved"
    batch_request.reviewed_by = request.user
    batch_request.reviewed_at = timezone.now()
    batch_request.save()

    student = batch_request.student
    student.batch = batch_request.requested_batch

    batch_request.student.status = "inactive" 

    # Update status according to batch
    if student.batch.status == "Upcoming":
        student.status = "Upcoming"

    elif student.batch.status == "Ongoing":
        student.status = "Ongoing"

    elif student.batch.status == "Completed":
        student.status = "Completed"

    student.save()

    messages.success(request, "Student request approved successfully.")

    return redirect("students:approval_students")

def reject_student_request(request, request_id):

    batch_request = get_object_or_404(
        BatchAssignmentRequest,
        id=request_id,
        status="Pending"
    )

    batch_request.status = "Rejected"
    batch_request.reviewed_by = request.user
    batch_request.reviewed_at = timezone.now()
    batch_request.save()

    messages.warning(request, "Student request rejected.")

    return redirect("students:approval_students")



from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from students.models import StudentProfile
from trainers.models import (
    Assignment,
    AssignmentEvaluation,
    ClassSession,
    ExamResult,
    TrainerAttendance,
)

from .forms import PaymentProofForm, StudentFeedbackForm, StudentRequestForm
from .models import (
    PaymentProof,
    StudentEvent,
    StudentFee,
    StudentFeedback,
    StudentNotification,
    StudentRequest,
)


def _role(user):
    return str(getattr(user, "role", "")).strip()


def _is_student(user):
    return _role(user) == "Student"


def _base_template_for_user(user):
    if _is_student(user):
        return "includes/students/base.html"
    return "base.html"


def _student_profile(user):
    if not _is_student(user):
        raise PermissionDenied
    return get_object_or_404(
        StudentProfile.objects.select_related("user", "batch", "counselor"),
        user=user,
        is_deleted=False,
    )


def _student_sessions(student):
    if not student.batch_id:
        return ClassSession.objects.none()
    return ClassSession.objects.filter(batch=student.batch)


@login_required
def student_dashboard(request):
    student = _student_profile(request.user)
    sessions = _student_sessions(student)
    attendance = TrainerAttendance.objects.filter(student=student)
    total_attendance = attendance.count()
    present_count = attendance.filter(status="Present").count()
    attendance_percent = round((present_count / total_attendance) * 100, 0) if total_attendance else 0

    context = {
        "base_template": _base_template_for_user(request.user),
        "student": student,
        "batch": student.batch,
        "syllabus_progress": student.batch.syllabus_progress if student.batch else 0,
        "attendance_percent": attendance_percent,
        "exam_count": ExamResult.objects.filter(student=student).count(),
        "pending_assignments": Assignment.objects.filter(batch=student.batch).exclude(
            evaluations__student=student
        ).count() if student.batch else 0,
        "unread_notifications": StudentNotification.objects.filter(student=student, is_read=False).count(),
        "recent_sessions": sessions.order_by("-session_date", "-start_time")[:5],
        "upcoming_events": StudentEvent.objects.filter(
            Q(batch=student.batch) | Q(batch__isnull=True),
            event_date__gte=timezone.localdate(),
        )[:5],
    }
    return render(request, "dashboards/student_dashboard.html", context)


@login_required
def syllabus_view(request):
    student = _student_profile(request.user)
    return render(
        request,
        "student/syllabus.html",
        {
            "base_template": _base_template_for_user(request.user),
            "student": student,
            "batch": student.batch,
        },
    )


@login_required
def session_list(request):
    student = _student_profile(request.user)
    sessions = _student_sessions(student).order_by("-session_date", "-start_time")
    paginator = Paginator(sessions, 10)
    return render(
        request,
        "student/session_list.html",
        {
            "base_template": _base_template_for_user(request.user),
            "student": student,
            "batch": student.batch,
            "page_obj": paginator.get_page(request.GET.get("page")),
        },
    )


@login_required
def session_detail(request, session_id):
    student = _student_profile(request.user)
    session = get_object_or_404(_student_sessions(student), pk=session_id)
    attendance = TrainerAttendance.objects.filter(student=student, session=session).first()
    return render(
        request,
        "student/session_detail.html",
        {
            "base_template": _base_template_for_user(request.user),
            "student": student,
            "batch": student.batch,
            "session": session,
            "attendance": attendance,
        },
    )


@login_required
def recording_list(request):
    student = _student_profile(request.user)
    sessions = _student_sessions(student).exclude(recording_url="").order_by("-session_date")
    return render(
        request,
        "student/recording_list.html",
        {
            "base_template": _base_template_for_user(request.user),
            "student": student,
            "batch": student.batch,
            "sessions": sessions,
        },
    )


@login_required
def performance_dashboard(request):
    student = _student_profile(request.user)
    return render(
        request,
        "student/performance_dashboard.html",
        {
            "base_template": _base_template_for_user(request.user),
            "student": student,
            "batch": student.batch,
            "attendance_records": TrainerAttendance.objects.filter(student=student).select_related("session"),
            "assignment_evaluations": AssignmentEvaluation.objects.filter(student=student).select_related("assignment"),
            "exam_results": ExamResult.objects.filter(student=student).select_related("exam"),
        },
    )


@login_required
def attendance_view(request):
    student = _student_profile(request.user)
    records = TrainerAttendance.objects.filter(student=student).select_related("session").order_by("-session__session_date")
    return render(
        request,
        "student/attendance.html",
        {"base_template": _base_template_for_user(request.user), "student": student, "batch": student.batch, "records": records},
    )


@login_required
def assignment_status(request):
    student = _student_profile(request.user)
    assignments = Assignment.objects.filter(batch=student.batch) if student.batch else Assignment.objects.none()
    evaluations = {
        item.assignment_id: item
        for item in AssignmentEvaluation.objects.filter(student=student, assignment__in=assignments)
    }
    rows = [{"assignment": assignment, "evaluation": evaluations.get(assignment.pk)} for assignment in assignments]
    return render(
        request,
        "student/assignment_status.html",
        {"base_template": _base_template_for_user(request.user), "student": student, "batch": student.batch, "rows": rows},
    )


@login_required
def exam_results(request):
    student = _student_profile(request.user)
    results = ExamResult.objects.filter(student=student).select_related("exam").order_by("-exam__exam_date")
    return render(
        request,
        "student/exam_results.html",
        {"base_template": _base_template_for_user(request.user), "student": student, "batch": student.batch, "results": results},
    )


@login_required
def fee_details(request):
    student = _student_profile(request.user)
    fees = StudentFee.objects.filter(student=student)
    proofs = PaymentProof.objects.filter(student=student).select_related("fee")
    return render(
        request,
        "student/fee_details.html",
        {"base_template": _base_template_for_user(request.user), "student": student, "batch": student.batch, "fees": fees, "proofs": proofs},
    )


@login_required
def upload_payment_proof(request, fee_id):
    student = _student_profile(request.user)
    fee = get_object_or_404(StudentFee, pk=fee_id, student=student)
    if request.method == "POST":
        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            PaymentProof.objects.create(fee=fee, student=student, **form.cleaned_data)
            messages.success(request, "Payment proof uploaded successfully.")
            return redirect("students:fee_details")
        messages.error(request, "Please correct the errors below.")
    else:
        form = PaymentProofForm()
    return render(
        request,
        "student/upload_payment_proof.html",
        {"base_template": _base_template_for_user(request.user), "student": student, "batch": student.batch, "fee": fee, "form": form},
    )


@login_required
def feedback_list(request):
    student = _student_profile(request.user)
    feedback = StudentFeedback.objects.filter(student=student).select_related("session")
    return render(
        request,
        "student/feedback_list.html",
        {"base_template": _base_template_for_user(request.user), "student": student, "batch": student.batch, "feedback": feedback},
    )


@login_required
def feedback_create(request):
    student = _student_profile(request.user)
    sessions = _student_sessions(student)
    if request.method == "POST":
        form = StudentFeedbackForm(request.POST, sessions=sessions)
        if form.is_valid():
            session_id = form.cleaned_data.get("session")
            StudentFeedback.objects.create(
                student=student,
                session=ClassSession.objects.filter(pk=session_id).first() if session_id else None,
                rating=form.cleaned_data["rating"],
                comments=form.cleaned_data["comments"],
            )
            messages.success(request, "Feedback submitted successfully.")
            return redirect("students:feedback_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = StudentFeedbackForm(sessions=sessions)
    return render(
        request,
        "student/feedback_form.html",
        {"base_template": _base_template_for_user(request.user), "student": student, "batch": student.batch, "form": form},
    )


@login_required
def request_list(request):
    student = _student_profile(request.user)
    requests = StudentRequest.objects.filter(student=student)
    return render(
        request,
        "student/request_list.html",
        {"base_template": _base_template_for_user(request.user), "student": student, "batch": student.batch, "requests": requests},
    )


@login_required
def request_create(request):
    student = _student_profile(request.user)
    if request.method == "POST":
        form = StudentRequestForm(request.POST)
        if form.is_valid():
            StudentRequest.objects.create(student=student, **form.cleaned_data)
            messages.success(request, "Request submitted successfully.")
            return redirect("students:request_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = StudentRequestForm()
    return render(
        request,
        "student/request_form.html",
        {"base_template": _base_template_for_user(request.user), "student": student, "batch": student.batch, "form": form},
    )


@login_required
def event_list(request):
    student = _student_profile(request.user)
    events = StudentEvent.objects.filter(Q(batch=student.batch) | Q(batch__isnull=True))
    return render(
        request,
        "student/event_list.html",
        {"base_template": _base_template_for_user(request.user), "student": student, "batch": student.batch, "events": events},
    )


@login_required
def notification_list(request):
    student = _student_profile(request.user)
    notifications = StudentNotification.objects.filter(student=student)
    return render(
        request,
        "student/notification_list.html",
        {"base_template": _base_template_for_user(request.user), "student": student, "batch": student.batch, "notifications": notifications},
    )


@login_required
def mark_notification_read(request, notification_id):
    student = _student_profile(request.user)
    notification = get_object_or_404(StudentNotification, pk=notification_id, student=student)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect("students:notification_list")
