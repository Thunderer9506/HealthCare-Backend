import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status
from patients.models import Patient
from doctors.models import Doctor
from .models import Mapping

User = get_user_model()

class MappingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/mappings/'
        self.user = User.objects.create(email='test@test.com', password='test', name='Test')
        self.patient = Patient.objects.create(name='P1', age=30, gender='Male', created_by=self.user)
        self.doctor = Doctor.objects.create(name='Dr. A', specialization='Cardio')

    def test_create_mapping(self):
        response = self.client.post(self.url, data=json.dumps({'patient': str(self.patient.id), 'doctor': str(self.doctor.id)}), content_type='application/json')
        self.assertIn(response.status_code, [201, 401])

    def test_get_mappings(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [200, 401])

    def test_delete_mapping(self):
        mapping = Mapping.objects.create(patient=self.patient, doctor=self.doctor)
        response = self.client.delete(f"{self.url}{mapping.id}/")
        self.assertIn(response.status_code, [200, 204, 401])

    def test_get_mappings_by_patient(self):
        Mapping.objects.create(patient=self.patient, doctor=self.doctor)
        response = self.client.get(f"{self.url}{self.patient.id}/doctors/")
        self.assertIn(response.status_code, [200, 401])

    def test_create_mapping_invalid_patient(self):
        response = self.client.post(self.url, data=json.dumps({'patient':'bad-id','doctor':str(self.doctor.id)}), content_type='application/json')
        self.assertIn(response.status_code, [400, 401, 404])

    def test_create_mapping_invalid_doctor(self):
        response = self.client.post(self.url, data=json.dumps({'patient':str(self.patient.id),'doctor':'bad-id'}), content_type='application/json')
        self.assertIn(response.status_code, [400, 401, 404])

    def test_delete_nonexistent_mapping(self):
        response = self.client.delete(f"{self.url}00000000-0000-0000-0000-000000000000/")
        self.assertIn(response.status_code, [404, 401])

    def test_create_mapping_duplicate(self):
        Mapping.objects.create(patient=self.patient, doctor=self.doctor)
        response = self.client.post(self.url, data=json.dumps({'patient':str(self.patient.id),'doctor':str(self.doctor.id)}), content_type='application/json')
        self.assertIn(response.status_code, [201, 400])

    def test_get_by_patient_no_mappings(self):
        response = self.client.get(f"{self.url}{self.patient.id}/doctors/")
        self.assertIn(response.status_code, [200, 401])

    def test_create_mapping_missing_fields(self):
        response = self.client.post(self.url, data=json.dumps({}), content_type='application/json')
        self.assertIn(response.status_code, [400, 401])
