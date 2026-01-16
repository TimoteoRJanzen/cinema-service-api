from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from pathlib import Path

from cinema.models import Movie


class MovieImageUploadTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@admin.com",
            password="admin123",
        )

        self.movie = Movie.objects.create(
            title="Avatar",
            description="Test movie",
            duration=180,
        )

        self.url = reverse(
            "cinema:movie-upload-image",
            args=[self.movie.id],
        )

    def test_admin_can_upload_movie_image(self):
        self.client.force_authenticate(user=self.admin)

        image_path = Path(__file__).parent / "assets" / "test.jpg"

        with open(image_path, "rb") as image_file:
            image = SimpleUploadedFile(
                name="test.jpg",
                content=image_file.read(),
                content_type="image/jpeg",
            )

            response = self.client.post(
                self.url,
                {"image": image},
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.movie.refresh_from_db()
        self.assertTrue(self.movie.image)
