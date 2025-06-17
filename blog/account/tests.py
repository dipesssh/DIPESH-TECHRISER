# tests.py for the `account` app
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User


class RegisterTest(APITestCase):
    def test_register_user_success(self):
        url = reverse('register')
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "password": "testpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # ✅ updated


    def test_register_duplicate_username(self):
        User.objects.create_user(username='johndoe', password='testpassword123')
        url = reverse('register')
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "username": "johndoe",
            "password": "anotherpassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="johndoe", password="testpassword123")

    def test_login_success(self):
        url = reverse('login')  # Ensure 'login' is set in urls.py as name
        data = {
            "username": "johndoe",
            "password": "testpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data['data'])

    def test_login_invalid_password(self):
        url = reverse('login')
        data = {
            "username": "johndoe",
            "password": "wrongpass"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Still returns 200 with error message
        self.assertEqual(response.data['message'], 'invalid credentials')
