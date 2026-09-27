from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Mapping
from patients.models import Patient
from doctors.models import Doctor

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def mapping_list_create(request):
    if request.method == 'GET':
        mappings = Mapping.objects.all()
        data = [{'id': str(m.id), 'patient_id': str(m.patient.id), 'doctor_id': str(m.doctor.id)} for m in mappings]
        return Response(data)
    elif request.method == 'POST':
        data = request.data
        try:
            patient = Patient.objects.get(id=data.get('patient'))
            doctor = Doctor.objects.get(id=data.get('doctor'))
        except (Patient.DoesNotExist, Doctor.DoesNotExist):
            return Response({'error': 'Invalid patient or doctor'}, status=status.HTTP_400_BAD_REQUEST)
        mapping = Mapping.objects.create(patient=patient, doctor=doctor)
        return Response({'id': str(mapping.id)}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def mapping_delete(request, id):
    try:
        mapping = Mapping.objects.get(id=id)
        mapping.delete()
        return Response({'message': 'Deleted'})
    except Mapping.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mapping_by_patient(request, patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
    mappings = Mapping.objects.filter(patient=patient)
    doctors = [mapping.doctor for mapping in mappings]
    data = [{'id': str(d.id), 'name': d.name, 'specialization': d.specialization} for d in doctors]
    return Response(data)
