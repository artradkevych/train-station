from rest_framework import viewsets, filters

from trains.models import TrainType, Train
from trains.serializers import TrainTypeSerializer, TrainSerializer
from users.permissions import IsAdminOrIfAuthenticatedReadOnly


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type")
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ("name", "train_type__name")
    serializer_class = TrainSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
