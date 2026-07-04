from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render

from batches.models import Batch
from students.models import StudentProfile

from .forms import AssignmentForm, ClassSessionForm, ExamForm, SyllabusProgressForm
from .models import Assignment, AssignmentEvaluation, ClassSession, Exam, ExamResult, TrainerAttendance


def _role(user):
    return str(getattr(user, "role", "")).strip()


def _is_trainer(user):
    return _role(user) == "Trainer"


def _base_template_for_user(user):
    if _role(user) == "Trainer":
        return "includes/trainers/base.html"
    return "base.html"


def _trainer_batches(user):
    return Batch.objects.filter(trainer=user).order_by("-created_at")


def _get_trainer_batch(user, batch_id):
    if not _is_trainer(user):
        raise PermissionDenied
    return get_object_or_404(_trainer_batches(user), pk=batch_id)


@login_required
def trainer_dashboard(request):
    if not _is_trainer(request.user):
        raise PermissionDenied

    batches = _trainer_batches(request.user)
    batch_ids = batches.values_list("id", flat=True)
    students = StudentProfile.objects.filter(batch_id__in=batch_ids, is_deleted=False)

    context = {
        "base_template": _base_template_for_user(request.user),
        "assigned_batches": batches.count(),
        "total_students": students.count(),
        "today_classes": ClassSession.objects.filter(
            batch_id__in=batch_ids,
            session_date=timezone.localdate(),
        ).count(),
        "pending_evaluation": Assignment.objects.filter(batch_id__in=batch_ids).count(),
        "assigned_batch_count": batches.count(),
        "active_student_count": students.count(),
        "average_progress": batches.aggregate(avg=Avg("syllabus_progress"))["avg"] or 0,
        "upcoming_sessions": ClassSession.objects.filter(batch_id__in=batch_ids).order_by(
            "session_date", "start_time"
        )[:5],
            "recent_assignments": Assignment.objects.filter(batch_id__in=batch_ids)[:5],
    }
    return render(request, "dashboards/trainer_dashboard.html", context)


@login_required
def assigned_batch_list(request):
    if not _is_trainer(request.user):
        raise PermissionDenied

    search_query = request.GET.get("q", "").strip()
    batches = _trainer_batches(request.user).annotate(student_count=Count("students"))

    if search_query:
        batches = batches.filter(
            Q(batch_name__icontains=search_query)
            | Q(course_name__icontains=search_query)
            | Q(status__icontains=search_query)
        )

    paginator = Paginator(batches, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "trainer/assigned_batch_list.html",
        {
            "base_template": _base_template_for_user(request.user),
            "page_obj": page_obj,
            "search_query": search_query,
        },
    )


@login_required
def batch_student_list(request, batch_id):
    batch = _get_trainer_batch(request.user, batch_id)
    search_query = request.GET.get("q", "").strip()
    students = StudentProfile.objects.select_related("user").filter(
        batch=batch,
        is_deleted=False,
    )

    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query)
            | Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(user__email__icontains=search_query)
        )

    paginator = Paginator(students.order_by("student_id"), 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "trainer/batch_student_list.html",
        {
            "base_template": _base_template_for_user(request.user),
            "batch": batch,
            "page_obj": page_obj,
            "search_query": search_query,
        },
    )


@login_required
def update_syllabus_progress(request, batch_id):
    batch = _get_trainer_batch(request.user, batch_id)

    if request.method == "POST":
        form = SyllabusProgressForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            messages.success(request, "Syllabus progress updated successfully.")
            return redirect("trainer:assigned_batch_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = SyllabusProgressForm(instance=batch)

    return render(
        request,
        "trainer/syllabus_progress_form.html",
        {"base_template": _base_template_for_user(request.user), "batch": batch, "form": form},
    )


@login_required
def class_session_list(request, batch_id):
    batch = _get_trainer_batch(request.user, batch_id)
    sessions = ClassSession.objects.filter(batch=batch)
    paginator = Paginator(sessions, 10)

    return render(
        request,
        "trainer/class_session_list.html",
        {
            "base_template": _base_template_for_user(request.user),
            "batch": batch,
            "page_obj": paginator.get_page(request.GET.get("page")),
        },
    )


@login_required
def class_session_create(request, batch_id):
    batch = _get_trainer_batch(request.user, batch_id)

    if request.method == "POST":
        form = ClassSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.batch = batch
            session.created_by = request.user
            session.save()
            messages.success(request, "Class session created successfully.")
            return redirect("trainer:class_session_list", batch_id=batch.pk)
        messages.error(request, "Please correct the errors below.")
    else:
        form = ClassSessionForm()

    return render(
        request,
        "trainer/class_session_form.html",
        {
            "base_template": _base_template_for_user(request.user),
            "batch": batch,
            "form": form,
            "title": "Schedule Class",
            "button_label": "Save Class",
        },
    )


@login_required
def class_session_update(request, session_id):
    session = get_object_or_404(ClassSession, pk=session_id)
    _get_trainer_batch(request.user, session.batch_id)

    if request.method == "POST":
        form = ClassSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, "Class session updated successfully.")
            return redirect("trainer:class_session_list", batch_id=session.batch_id)
        messages.error(request, "Please correct the errors below.")
    else:
        form = ClassSessionForm(instance=session)

    return render(
        request,
        "trainer/class_session_form.html",
        {
            "base_template": _base_template_for_user(request.user),
            "batch": session.batch,
            "form": form,
            "title": "Edit Class",
            "button_label": "Update Class",
        },
    )


@login_required
def mark_attendance(request, session_id):
    session = get_object_or_404(ClassSession.objects.select_related("batch"), pk=session_id)
    batch = _get_trainer_batch(request.user, session.batch_id)
    students = StudentProfile.objects.select_related("user").filter(batch=batch, is_deleted=False)

    if request.method == "POST":
        for student in students:
            status = request.POST.get(f"status_{student.pk}", "Absent")
            remarks = request.POST.get(f"remarks_{student.pk}", "").strip()
            TrainerAttendance.objects.update_or_create(
                session=session,
                student=student,
                defaults={"status": status, "remarks": remarks},
            )
        messages.success(request, "Attendance marked successfully.")
        return redirect("trainer:class_session_list", batch_id=batch.pk)

    attendance_map = {
        attendance.student_id: attendance
        for attendance in TrainerAttendance.objects.filter(session=session, student__in=students)
    }
    student_rows = [
        {"student": student, "attendance": attendance_map.get(student.pk)}
        for student in students
    ]

    return render(
        request,
        "trainer/mark_attendance.html",
        {
            "base_template": _base_template_for_user(request.user),
            "batch": batch,
            "session": session,
            "student_rows": student_rows,
        },
    )


@login_required
def assignment_list(request, batch_id):
    batch = _get_trainer_batch(request.user, batch_id)
    assignments = Assignment.objects.filter(batch=batch)

    return render(
        request,
        "trainer/assignment_list.html",
        {
            "base_template": _base_template_for_user(request.user),
            "batch": batch,
            "assignments": assignments,
        },
    )


@login_required
def assignment_create(request, batch_id):
    batch = _get_trainer_batch(request.user, batch_id)

    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.batch = batch
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, "Assignment created successfully.")
            return redirect("trainer:assignment_list", batch_id=batch.pk)
        messages.error(request, "Please correct the errors below.")
    else:
        form = AssignmentForm()

    return render(
        request,
        "trainer/assignment_form.html",
        {
            "base_template": _base_template_for_user(request.user),
            "batch": batch,
            "form": form,
            "title": "Create Assignment",
            "button_label": "Save Assignment",
        },
    )


@login_required
def evaluate_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment.objects.select_related("batch"), pk=assignment_id)
    batch = _get_trainer_batch(request.user, assignment.batch_id)
    students = StudentProfile.objects.select_related("user").filter(batch=batch, is_deleted=False)

    if request.method == "POST":
        for student in students:
            marks = request.POST.get(f"marks_{student.pk}", "").strip() or None
            feedback = request.POST.get(f"feedback_{student.pk}", "").strip()
            AssignmentEvaluation.objects.update_or_create(
                assignment=assignment,
                student=student,
                defaults={"marks_obtained": marks, "feedback": feedback},
            )
        messages.success(request, "Assignment evaluation updated successfully.")
        return redirect("trainer:assignment_list", batch_id=batch.pk)

    evaluations = {
        evaluation.student_id: evaluation
        for evaluation in AssignmentEvaluation.objects.filter(assignment=assignment, student__in=students)
    }
    student_rows = [
        {"student": student, "evaluation": evaluations.get(student.pk)}
        for student in students
    ]

    return render(
        request,
        "trainer/evaluate_assignment.html",
        {
            "base_template": _base_template_for_user(request.user),
            "assignment": assignment,
            "batch": batch,
            "student_rows": student_rows,
        },
    )


@login_required
def exam_list(request, batch_id):
    batch = _get_trainer_batch(request.user, batch_id)
    exams = Exam.objects.filter(batch=batch)

    return render(
        request,
        "trainer/exam_list.html",
        {"base_template": _base_template_for_user(request.user), "batch": batch, "exams": exams},
    )


@login_required
def exam_create(request, batch_id):
    batch = _get_trainer_batch(request.user, batch_id)

    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.batch = batch
            exam.created_by = request.user
            exam.save()
            messages.success(request, "Exam created successfully.")
            return redirect("trainer:exam_list", batch_id=batch.pk)
        messages.error(request, "Please correct the errors below.")
    else:
        form = ExamForm()

    return render(
        request,
        "trainer/exam_form.html",
        {
            "base_template": _base_template_for_user(request.user),
            "batch": batch,
            "form": form,
            "title": "Create Exam",
            "button_label": "Save Exam",
        },
    )


@login_required
def update_exam_results(request, exam_id):
    exam = get_object_or_404(Exam.objects.select_related("batch"), pk=exam_id)
    batch = _get_trainer_batch(request.user, exam.batch_id)
    students = StudentProfile.objects.select_related("user").filter(batch=batch, is_deleted=False)

    if request.method == "POST":
        for student in students:
            marks = request.POST.get(f"marks_{student.pk}", "").strip() or None
            remarks = request.POST.get(f"remarks_{student.pk}", "").strip()
            ExamResult.objects.update_or_create(
                exam=exam,
                student=student,
                defaults={"marks_obtained": marks, "remarks": remarks},
            )
        messages.success(request, "Exam results updated successfully.")
        return redirect("trainer:exam_list", batch_id=batch.pk)

    results = {
        result.student_id: result
        for result in ExamResult.objects.filter(exam=exam, student__in=students)
    }
    student_rows = [
        {"student": student, "result": results.get(student.pk)}
        for student in students
    ]

    return render(
        request,
        "trainer/update_exam_results.html",
        {
            "base_template": _base_template_for_user(request.user),
            "exam": exam,
            "batch": batch,
            "student_rows": student_rows,
        },
    )
