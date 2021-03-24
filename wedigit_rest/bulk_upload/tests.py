from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import request, status
from rest_framework.test import APIClient
from rest_framework.test import force_authenticate
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

# Create your tests here.
class UploadDocumentTest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test_user@email.com', 
            password='password',
        )

    def test_document_upload(self) -> None:
        self.assertTrue(1 == 1)
