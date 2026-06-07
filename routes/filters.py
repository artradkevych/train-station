from django_filters import rest_framework as filters

from routes.models import Trip


class TripFilter(filters.FilterSet):
    departure_time = filters.DateFromToRangeFilter()
    arrival_time = filters.DateFromToRangeFilter()

    class Meta:
        model = Trip
        fields = (
            "departure_time",
            "arrival_time",
            "route",
            "train",
            "crew",
        )
