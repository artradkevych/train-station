from rest_framework import serializers

from routes.models import Station, Route, Trip
from trains.serializers import TrainSerializer
from users.serializers import CrewSerializer


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = (
            "id",
            "name",
            "latitude",
            "longitude",
        )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(source="destination.name", read_only=True)


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer()
    destination = StationSerializer()


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = (
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
        )


class TripListSerializer(TripSerializer):
    route = RouteListSerializer()
    train = serializers.StringRelatedField()
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )


class TripDetailSerializer(TripSerializer):
    route = RouteDetailSerializer()
    train = TrainSerializer()
    crew = CrewSerializer(many=True)
