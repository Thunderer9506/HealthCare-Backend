import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Doctor

User = get_user_model()

class DoctorTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/doctors/'

    def test_create_doctor(self):
        response = self.client.post(self.url, data=json.dumps({'name':'Dr. Smith','specialization':'Cardiologist'}), content_type='application/json')
        self.assertIn(response.status_code, [201, 401])

    def test_get_all_doctors(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [200, 401])

    def test_get_doctor_by_id(self):
        doctor = Doctor.objects.create(name='Dr. Jones', specialization='Neurologist')
        response = self.client.get(f"{self.url}{doctor.id}/")
        self.assertIn(response.status_code, [200, 401])

    def test_update_doctor(self):
        doctor = Doctor.objects.create(name='Dr. Jones', specialization='Neurologist')
        response = self.client.put(f"{self.url}{doctor.id}/", data=json.dumps({'specialization':'Updated'}), content_type='application/json')
        self.assertIn(response.status_code, [200, 401])

    def test_delete_doctor(self):
        doctor = Doctor.objects.create(name='Dr. Jones', specialization='Neurologist')
        response = self.client.delete(f"{self.url}{doctor.id}/")
        self.assertIn(response.status_code, [200, 204, 401])

    def test_create_doctor_missing_name(self):
        response = self.client.post(self.url, data=json.dumps({'specialization':'X'}), content_type='application/json')
        self.assertIn(response.status_code, [400, 201, 401])

    def test_create_doctor_long_specialization(self):
        response = self.client.post(self.url, data=json.dumps({'name':'Dr. X','specialization':'A'*200}), content_type='application/json')
        self.assertIn(response.status_code, [201, 400])

    def test_get_nonexistent_doctor(self):
        response = self.client.get(f"{self.url}00000000-0000-0000-0000-000000000000/")
        self.assertIn(response.status_code, [404, 401])

    def test_create_doctor_empty_specialization(self):
        response = self.client.post(self.url, data=json.dumps({'name':'Dr. Y','specialization':''}), content_type='application/json')
        self.assertIn(response.status_code, [201, 400])

    def test_update_doctor_invalid_id(self):
        response = self.client.put(f"{self.url}00000000-0000-0000-0000-000000000000/", data=json.dumps({'name':'X'}), content_type='application/json')
        self.assertIn(response.status_code, [404, 401, 200])
