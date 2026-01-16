from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


USER_ME_URL = reverse("user:manage_user")

class AuthTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="teste",
            email="teste@teste.com",
            password="teste123"
        )

    def test_unauthenticated_user_cannot_access_me(self):
        response = self.client.get(USER_ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_access_me(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(USER_ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)