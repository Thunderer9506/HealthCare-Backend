from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_list_create, name='patient_list_create'),
    path('<uuid:id>/', views.patient_detail, name='patient_detail'),
]
