from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cinema.models import Genre, Actor


MOVIE_URL = reverse("cinema:movie-list")


class PermissionsTests(APITestCase):

    def setUp(self):

        self.admin = get_user_model().objects.create_superuser(
            username="admin", email="admin@admin.com", password="admin123"
        )

        self.user = get_user_model().objects.create_user(
            username="teste", email="teste@teste.com", password="teste123"
        )

        genre = Genre.objects.create(name="Teste")
        actor = Actor.objects.create(first_name="Teste", last_name="Teste")

        self.movie_data = {
            "title": "Avatar",
            "description": "test",
            "duration": 180,
            "genres": [genre.id],
            "actors": [actor.id],
        }

    def test_unauthenticated_user_cannot_access_movies(self):
        response = self.client.get(MOVIE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticate_user_can_access_movies(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(MOVIE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_create_movie(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(MOVIE_URL, self.movie_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_create_movie(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(MOVIE_URL, self.movie_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
