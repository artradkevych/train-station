from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from trains.models import TrainType, Train
from trains.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
    TrainImageSerializer,
)
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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return TrainImageSerializer

        return TrainSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        movie = self.get_object()
        serializer = self.get_serializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
