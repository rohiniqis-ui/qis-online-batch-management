from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_index, name='home_index'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('assistant-dashboard/', views.assistant_dashboard, name='assistant_dashboard'),
    path('counselor-dashboard/', views.counselor_dashboard, name='counselor_dashboard'),
    path('trainer-dashboard/', views.trainer_dashboard, name='trainer_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
]