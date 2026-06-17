from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError

from routes.models import Trip


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders"
    )

    def __str__(self) -> str:
        formatted_date = self.created_at.strftime("%Y-%m-%d %H:%M")
        return f"Order №{self.id} ({formatted_date})"

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    trip = models.ForeignKey(Trip, on_delete=models.PROTECT, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="tickets")

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name.capitalize()} "
                        f"number must be in available range: "
                        f"1 to {count_attrs}."
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.trip.train,
            ValidationError,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket №{self.id} (Wagon: {self.cargo}, Seat: {self.seat})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "cargo", "seat"],
                name="unique_trip_cargo_seat",
            )
        ]
        ordering = ["cargo", "seat"]
