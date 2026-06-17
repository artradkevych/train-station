from rest_framework import serializers

from orders.models import Ticket
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

    def validate(self, attrs):
        source = attrs.get("source", getattr(self.instance, "source", None))
        destination = attrs.get(
            "destination", getattr(self.instance, "destination", None)
        )
        if source and destination and source == destination:
            raise serializers.ValidationError(
                {"destination": "Source and destination stations cannot be the same."}
            )
        return attrs


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(source="destination.name", read_only=True)


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer()
    destination = StationSerializer()


class TripSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        departure = attrs.get(
            "departure_time", getattr(self.instance, "departure_time", None)
        )
        arrival = attrs.get(
            "arrival_time", getattr(self.instance, "arrival_time", None)
        )
        if departure and arrival and departure >= arrival:
            raise serializers.ValidationError(
                {"arrival_time": "Arrival time must be after departure time."}
            )
        return data

    class Meta:
        model = Trip
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
        )


class TripListSerializer(serializers.ModelSerializer):
    route_source = serializers.CharField(source="route.source.name", read_only=True)
    route_destination = serializers.CharField(
        source="route.destination.name", read_only=True
    )
    train = serializers.StringRelatedField()
    train_capacity = serializers.IntegerField(source="train.capacity", read_only=True)
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Trip
        fields = (
            "id",
            "route_source",
            "route_destination",
            "train",
            "train_capacity",
            "departure_time",
            "arrival_time",
            "crew",
            "tickets_available",
        )


class TicketSeatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("cargo", "seat")


class TripDetailSerializer(TripSerializer):
    route = RouteDetailSerializer()
    train = TrainSerializer()
    crew = CrewSerializer(many=True)
    taken_places = TicketSeatsSerializer(source="tickets", many=True, read_only=True)

    class Meta(TripSerializer.Meta):
        fields = TripSerializer.Meta.fields + ("taken_places",)
