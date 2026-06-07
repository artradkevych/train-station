from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str
from rest_framework import serializers

from trains.models import TrainType, Train


class CreatableSlugRelatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            obj, _ = queryset.get_or_create(**{self.slug_field: data})

            return obj
        except ObjectDoesNotExist:
            self.fail(
                "does_not_exist", slug_name=self.slug_field, value=smart_str(data)
            )
        except (TypeError, ValueError):
            self.fail("invalid")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = (
            "id",
            "name",
        )


class TrainImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "image")


class TrainSerializer(serializers.ModelSerializer):
    train_type = CreatableSlugRelatedField(
        slug_field="name", queryset=TrainType.objects.all()
    )

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "capacity",
            "image",
        )
