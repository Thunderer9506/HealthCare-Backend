from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET', 'POST'])
@authentication_classes([])  # handled by permission_classes
@permission_classes([IsAuthenticated])
def patient_list_create(request):
    if request.method == 'GET':
        patients = Patient.objects.filter(created_by=request.user)
        data = [{'id': str(p.id), 'name': p.name, 'age': p.age, 'gender': p.gender, 'created_by': str(p.created_by.id)} for p in patients]
        return Response(data)
    elif request.method == 'POST':
        data = request.data
        patient = Patient.objects.create(name=data.get('name'), age=data.get('age'), gender=data.get('gender'), created_by=request.user)
        return Response({'id': str(patient.id), 'name': patient.name}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def patient_detail(request, id):
    try:
        patient = Patient.objects.get(id=id, created_by=request.user)
    except Patient.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({'id': str(patient.id), 'name': patient.name, 'age': patient.age, 'gender': patient.gender})
    elif request.method == 'PUT':
        data = request.data
        patient.name = data.get('name', patient.name)
        patient.age = data.get('age', patient.age)
        patient.gender = data.get('gender', patient.gender)
        patient.save()
        return Response({'message': 'Updated'})
    elif request.method == 'DELETE':
        patient.delete()
        return Response({'message': 'Deleted'})
