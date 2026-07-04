from django.urls import path

from . import views


app_name = "trainer"

urlpatterns = [
    path("", views.trainer_dashboard, name="trainer_dashboard"),
    path("", views.trainer_dashboard, name="trainer_dashboard_legacy"),
    path("dashboard/", views.trainer_dashboard, name="trainer_dashboard_alias"),
    path("batches/", views.assigned_batch_list, name="assigned_batch_list"),
    path("batches/", views.assigned_batch_list, name="assigned_batch_list_legacy"),
    path("batches/<int:batch_id>/students/", views.batch_student_list, name="batch_student_list"),
    path("batches/<int:batch_id>/syllabus/", views.update_syllabus_progress, name="update_syllabus_progress"),
    path("batches/<int:batch_id>/classes/", views.class_session_list, name="class_session_list"),
    path("batches/<int:batch_id>/classes/add/", views.class_session_create, name="class_session_create"),
    path("classes/<int:session_id>/edit/", views.class_session_update, name="class_session_update"),
    path("classes/<int:session_id>/attendance/", views.mark_attendance, name="mark_attendance"),
    path("batches/<int:batch_id>/assignments/", views.assignment_list, name="assignment_list"),
    path("batches/<int:batch_id>/assignments/add/", views.assignment_create, name="assignment_create"),
    path("assignments/<int:assignment_id>/evaluate/", views.evaluate_assignment, name="evaluate_assignment"),
    path("batches/<int:batch_id>/exams/", views.exam_list, name="exam_list"),
    path("batches/<int:batch_id>/exams/add/", views.exam_create, name="exam_create"),
    path("exams/<int:exam_id>/results/", views.update_exam_results, name="update_exam_results"),
]
