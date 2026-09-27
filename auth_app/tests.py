import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'

    # --- Register Tests ---

    def test_register_success(self):
        response = self.client.post(self.register_url, data=json.dumps({
            'name': 'Alice', 'email': 'alice@test.com', 'password': 'secure123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='alice@test.com').exists())

    def test_register_missing_email(self):
        response = self.client.post(self.register_url, data=json.dumps({
            'name': 'Bob', 'password': 'secure123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email_case_insensitive(self):
        self.client.post(self.register_url, data=json.dumps({
            'name': 'Alice', 'email': 'alice@test.com', 'password': 'secure123'
        }), content_type='application/json')
        # Try registering same email with different case
        response = self.client.post(self.register_url, data=json.dumps({
            'name': 'Alice2', 'email': 'ALICE@test.com', 'password': 'secure123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_password(self):
        response = self.client.post(self.register_url, data=json.dumps({
            'name': 'Charlie', 'email': 'charlie@test.com'
        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_name(self):
        response = self.client.post(self.register_url, data=json.dumps({
            'email': 'dave@test.com', 'password': 'secure123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Login Tests ---

    def test_login_success(self):
        import bcrypt
        hashed = bcrypt.hashpw(b'secure123', bcrypt.gensalt()).decode('utf-8')
        User.objects.create(email='eve@test.com',
                            password=hashed, name='Eve')
        response = self.client.post(self.login_url, data=json.dumps({
            'email': 'eve@test.com', 'password': 'secure123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)

    def test_login_invalid_password(self):
        import bcrypt
        hashed = bcrypt.hashpw(b'secure123', bcrypt.gensalt()).decode('utf-8')
        User.objects.create(email='eve@test.com',
                            password=hashed, name='Eve')
        response = self.client.post(self.login_url, data=json.dumps({
            'email': 'eve@test.com', 'password': 'wrongpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_email_field(self):
        response = self.client.post(self.login_url, data=json.dumps({
            'password': 'secure123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_token_not_applicable_but_wrong_email_case(self):
        # Email does not exist at all
        response = self.client.post(self.login_url, data=json.dumps({
            'email': 'nonexistent@test.com', 'password': 'secure123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_email_case_insensitive_match(self):
        import bcrypt
        hashed = bcrypt.hashpw(b'secure123', bcrypt.gensalt()).decode('utf-8')
        User.objects.create(email='eve@test.com',
                            password=hashed, name='Eve')
        # Login with different case email
        response = self.client.post(self.login_url, data=json.dumps({
            'email': 'EVE@test.com', 'password': 'secure123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
