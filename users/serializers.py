from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from users.models import Crew


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "is_staff")
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class CrewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=False)

    class Meta:
        model = Crew
        fields = (
            "id",
            "user",
            "first_name",
            "last_name",
        )

    def create(self, validated_data):
        with transaction.atomic():
            user_data = validated_data.pop("user")
            user = get_user_model().objects.create_user(**user_data)
            crew = Crew.objects.create(**validated_data, user=user)
            return crew
