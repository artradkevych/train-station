from django_filters import rest_framework as filters

from orders.models import Order


class OrderFilter(filters.FilterSet):
    departure_time = filters.DateFromToRangeFilter(
        field_name="tickets__trip__departure_time"
    )
    arrival_time = filters.DateFromToRangeFilter(
        field_name="tickets__trip__arrival_time"
    )
    trip = filters.NumberFilter(field_name="tickets__trip_id")

    class Meta:
        model = Order
        fields = ("departure_time", "arrival_time", "trip")
