import pathlib
import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class CinemaHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


def movie_image_path(instance, filename):
    filename = (f"{slugify(instance.title)}-{uuid.uuid4()}"
                + pathlib.Path(filename).suffix)
    return pathlib.Path("uploads/movies/") / pathlib.Path(filename)


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField()
    genres = models.ManyToManyField(Genre, related_name="movies")
    actors = models.ManyToManyField(Actor, related_name="movies")
    image = models.ImageField(null=True, upload_to=movie_image_path)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class MovieSession(models.Model):
    show_time = models.DateTimeField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="movie_sessions")
    cinema_hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name="movie_sessions")

    class Meta:
        ordering = ["-show_time"]

    def __str__(self) -> str:
        return f"{self.movie.title} {self.show_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self) -> str:
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    movie_session = models.ForeignKey(
        MovieSession,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    row = models.IntegerField()
    seat = models.IntegerField()

    @classmethod
    def validate_seat(cls, row, seat, cinema_hall):
        errors = {}

        if not (1 <= row <= cinema_hall.rows):
            errors["row"] = f"Row must be between 1 and {cinema_hall.rows}."

        if not (1 <= seat <= cinema_hall.seats_in_row):
            errors["seat"] = (
                f"Seat must be between 1 and {cinema_hall.seats_in_row}."
            )

        if errors:
            raise ValidationError(errors)

    def clean(self):
        self.validate_seat(
            self.row,
            self.seat,
            self.movie_session.cinema_hall
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{str(self.movie_session)} (row: {self.row}, seat: {self.seat})"
        )

    class Meta:
        unique_together = ("movie_session", "row", "seat")
        ordering = ("row", "seat")