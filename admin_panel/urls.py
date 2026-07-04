from django.urls import path
from . import views

app_name = 'admin'
urlpatterns = [

    # List Users
    path('users/<str:role>/', views.user_list, name='user_list'),
    # Add User
    path('users/add/<str:role>/', views.add_user, name='add_user'),
    # Edit User
    path('users/edit/<int:id>/', views.edit_user, name='edit_user'),
    # Activate / Deactivate
    path('users/status/<int:id>/', views.toggle_user_status, name='toggle_user_status'),
]