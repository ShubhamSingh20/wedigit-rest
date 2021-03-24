from django.test import TestCase
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import request, status
from rest_framework.test import APIClient

User = get_user_model()

# Create your tests here.
class JwtAuthTest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test_user@email.com', password='password'
        )

    def test_signup(self) -> None:
        response : Response = self.client.post(
            '/api/v1/auth/register/', {
            'first_name': 'John',
            'last_name': 'Test',
            'email': 'new_test@email.com',
            'password': 'password'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn('jwt', response.client.cookies)
        self.assertIn('refresh', response.client.cookies)


    def test_login(self) -> None:
        response : Response = self.client.post(
            '/api/v1/auth/login/', {
            'email': 'test_user@email.com',
            'password': 'password'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', response.client.cookies)
        self.assertIn('refresh', response.client.cookies)
        self.assertEqual(self.user.slug, response.data.get('user').get('id'))

    def test_logout(self) -> None:
        self.client.post(
            '/api/v1/auth/login/', {
            'email': 'test_user@email.com',
            'password': 'password'
        }, format='json')

        response : Response = self.client.post('api/v1/auth/logout/')
        self.assertNotIn('jwt', response.cookies)
        self.assertNotIn('refresh', response.cookies)
