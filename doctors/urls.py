from django.urls import path
from . import views

urlpatterns = [
    path('', views.doctor_list_create, name='doctor_list_create'),
    path('<uuid:id>/', views.doctor_detail, name='doctor_detail'),
]
