from django_filters import rest_framework as drf_filters
from rest_framework import viewsets, filters
from django.db.models import F, Count
from routes.filters import TripFilter
from routes.models import Station, Route, Trip
from routes.serializers import (
    StationSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    TripListSerializer,
    TripDetailSerializer,
    TripSerializer,
)
from users.permissions import IsAdminOrIfAuthenticatedReadOnly


class StationViewSet(viewsets.ModelViewSet):
    """
    Manage railway stations.
    Provides endpoints to list, create, and manage geographical train stations and stops.
    """

    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    """
    Manage geographical routes between stations.
    Defines connections from a source station to a destination station, including total distance details.
    """

    queryset = Route.objects.select_related("source", "destination")
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class TripViewSet(viewsets.ModelViewSet):
    """
    Manage train trips and schedules.
    Provides real-time tracking of active schedules, departure/arrival filtering, and dynamically calculates available tickets and taken seats.
    """

    queryset = (
        Trip.objects.all()
        .select_related("route__source", "route__destination", "train")
        .prefetch_related("crew__user")
        .annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo") - Count("tickets")
            )
        )
    )
    filter_backends = [
        filters.OrderingFilter,
        drf_filters.DjangoFilterBackend,
    ]
    ordering_fields = ["departure_time"]
    filterset_class = TripFilter
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer

        if self.action == "retrieve":
            return TripDetailSerializer

        return TripSerializer
