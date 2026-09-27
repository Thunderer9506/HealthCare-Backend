from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Doctor

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def doctor_list_create(request):
    if request.method == 'GET':
        doctors = Doctor.objects.all()
        data = [{'id': str(d.id), 'name': d.name, 'specialization': d.specialization} for d in doctors]
        return Response(data)
    elif request.method == 'POST':
        data = request.data
        doctor = Doctor.objects.create(name=data.get('name'), specialization=data.get('specialization'))
        return Response({'id': str(doctor.id), 'name': doctor.name}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def doctor_detail(request, id):
    try:
        doctor = Doctor.objects.get(id=id)
    except Doctor.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({'id': str(doctor.id), 'name': doctor.name, 'specialization': doctor.specialization})
    elif request.method == 'PUT':
        data = request.data
        doctor.name = data.get('name', doctor.name)
        doctor.specialization = data.get('specialization', doctor.specialization)
        doctor.save()
        return Response({'message': 'Updated'})
    elif request.method == 'DELETE':
        doctor.delete()
        return Response({'message': 'Deleted'})
