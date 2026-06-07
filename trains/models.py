import os
import uuid

from django.db import models
from django.utils.text import slugify


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]


def create_custom_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return os.path.join(
        "uploads/images/", f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    )


class Train(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, models.PROTECT, related_name="trains")
    image = models.ImageField(null=True, upload_to=create_custom_path)

    def __str__(self) -> str:
        return self.name

    @property
    def capacity(self):
        return self.cargo_num * self.places_in_cargo

    class Meta:
        ordering = ["name"]
