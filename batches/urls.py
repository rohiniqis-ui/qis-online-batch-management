

from django.urls import path
from . import views

app_name = 'batches'

urlpatterns = [

    path('batches/', views.batch_list, name='batch_list'),
    path('batches/add/', views.batch_form, name='add_batch'),
    path('batches/edit/<int:id>/', views.batch_form, name='edit_batch'),
    path('batches/archive/<int:id>/',views.archive_batch,name='archive_batch'),


]