from django.db import models
from rest_framework.exceptions import ValidationError

from trains.models import Train
from users.models import Crew


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.PROTECT, related_name="departure_routes"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.PROTECT, related_name="arrival_routes"
    )
    distance = models.IntegerField()

    def __str__(self) -> str:
        return f"Route №{self.id} ({self.distance} km)"

    class Meta:
        ordering = ["id"]


class Trip(models.Model):
    route = models.ForeignKey(Route, on_delete=models.PROTECT, related_name="trips")
    train = models.ForeignKey(Train, on_delete=models.PROTECT, related_name="trips")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="trips")

    def __str__(self) -> str:
        formatted_time = self.departure_time.strftime("%Y-%m-%d %H:%M")
        return f"Trip №{self.id} (Departure: {formatted_time})"

    def clean(self):
        if self.departure_time and self.arrival_time:
            if self.departure_time >= self.arrival_time:
                raise ValidationError(
                    {"arrival_time": "Arrival time must be after departure time."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-departure_time"]
