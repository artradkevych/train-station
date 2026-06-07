from django_filters import rest_framework as drf_filters
from rest_framework import viewsets, filters, mixins
from rest_framework.permissions import IsAuthenticated

from orders.filters import OrderFilter
from orders.models import Order
from orders.serializers import OrderSerializer, OrderListSerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Manage user orders and ticket purchases.
    Allows authenticated passengers to view their booking history, cancel orders, or create new ticket reservations.
    """

    queryset = Order.objects.prefetch_related(
        "tickets__trip__route", "tickets__trip__train"
    )
    filter_backends = [
        filters.OrderingFilter,
        drf_filters.DjangoFilterBackend,
    ]
    ordering_fields = ["tickets__trip__departure_time"]
    search_fields = (
        "tickets__trip__route__source__name",
        "tickets__trip__route__destination__name",
        "tickets__trip__train__name",
    )
    filterset_class = OrderFilter
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
