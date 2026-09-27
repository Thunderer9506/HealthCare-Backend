from django.urls import path
from . import views

urlpatterns = [
    path('', views.mapping_list_create, name='mapping_list_create'),
    path('<uuid:patient_id>/doctors/', views.mapping_by_patient, name='mapping_by_patient'),
    path('<uuid:id>/', views.mapping_delete, name='mapping_delete'),
]
