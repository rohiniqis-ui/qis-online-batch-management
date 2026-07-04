from django.urls import path

from . import views


app_name = "students"

urlpatterns = [
    path("", views.student_list, name="student_list"),
    path("add/", views.student_create, name="student_create"),
    path("batch-requests/", views.batch_assignment_request_list, name="batch_assignment_request_list"),
    path("approval-requests/", views.batch_assignment_request_list, name="approval_request_list"),
    path( "batch-requests/<int:pk>/review/", views.batch_assignment_request_review, name="batch_assignment_request_review",),
    path("<int:pk>/", views.student_detail, name="student_detail"),
    path("<int:pk>/edit/", views.student_update, name="student_update"),
    path("<int:pk>/delete/", views.student_delete, name="student_delete"),
    path("<int:pk>/batch/assign/", views.student_batch_assign, name="student_batch_assign"),
    path("<int:pk>/batch/transfer/", views.student_batch_transfer, name="student_batch_transfer"),
    path("<int:pk>/batch/remove/", views.student_batch_remove, name="student_batch_remove"),



    path( "approval-students/", views.approval_students, name="approval_students",),
    path( "upcoming-students/", views.upcoming_students, name="upcoming_students",),
    path( "ongoing-students/", views.ongoing_students, name="ongoing_students",),
    path( "completed-students/", views.completed_students, name="completed_students",),

    path("approval-students/",views.approval_students,name="approval_students",),
    path( "student/<int:pk>/", views.student_detail, name="student_detail",),
    path( "approve-request/<int:request_id>/", views.approve_student_request, name="approve_student_request",),
    path( "reject-request/<int:request_id>/", views.reject_student_request, name="reject_student_request",),


    
    path("", views.student_dashboard, name="student_dashboard"),
    path("dashboard/", views.student_dashboard, name="student_dashboard_alias"),
    path("syllabus/", views.syllabus_view, name="syllabus_view"),
    path("sessions/", views.session_list, name="session_list"),
    path("sessions/<int:session_id>/", views.session_detail, name="session_detail"),
    path("recordings/", views.recording_list, name="recording_list"),
    path("performance/", views.performance_dashboard, name="performance_dashboard"),
    path("attendance/", views.attendance_view, name="attendance_view"),
    path("assignments/", views.assignment_status, name="assignment_status"),
    path("exam-results/", views.exam_results, name="exam_results"),
    path("fees/", views.fee_details, name="fee_details"),
    path("fees/<int:fee_id>/upload-proof/", views.upload_payment_proof, name="upload_payment_proof"),
    path("feedback/", views.feedback_list, name="feedback_list"),
    path("feedback/add/", views.feedback_create, name="feedback_create"),
    path("requests/", views.request_list, name="request_list"),
    path("requests/add/", views.request_create, name="request_create"),
    path("events/", views.event_list, name="event_list"),
    path("notifications/", views.notification_list, name="notification_list"),
    path("notifications/<int:notification_id>/read/", views.mark_notification_read, name="mark_notification_read"),



]
