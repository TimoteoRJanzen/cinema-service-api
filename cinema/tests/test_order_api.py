from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cinema.models import Movie, Actor, Genre, MovieSession, CinemaHall, Order

ORDER_URL = reverse("cinema:order-list")

class OrderTests(APITestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username="teste",
            email="teste@teste.com",
            password="teste123"
        )

        self.other_user = get_user_model().objects.create_user(
            username="other",
            email="other@other.com",
            password="other123"
        )

        movie = Movie.objects.create(
            title="Avatar",
            description="test",
            duration=180,
        )

        cinema_hall = CinemaHall.objects.create(
            name="Teste",
            rows=2,
            seats_in_row=5
        )

        self.movie_session = MovieSession.objects.create(
            movie=movie,
            cinema_hall=cinema_hall,
            show_time="2026-01-01T12:00:00Z"
        )

        self.data = {
            "tickets": [{
                "row": 1,
                "seat": 1,
                "movie_session": self.movie_session.id
            }]
        }

    def test_unauthenticated_user_cannot_access_orders(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_create_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(ORDER_URL, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_sees_only_own_orders(self):
        Order.objects.create(user=self.user)
        Order.objects.create(user=self.other_user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(ORDER_URL)
        self.assertEqual(len(response.data["results"]), 1)

