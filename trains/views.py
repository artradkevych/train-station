from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from trains.models import TrainType, Train
from trains.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
    TrainImageSerializer,
)
from users.permissions import IsAdminOrIfAuthenticatedReadOnly


@extend_schema(tags=["Train Types"], description="Manage train types and categories")
class TrainTypeViewSet(viewsets.ModelViewSet):
    """
    Manage train types and categories.
    Provides CRUD operations to define train classifications (e.g., Regional, Intercity, High-Speed).
    """

    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


@extend_schema(tags=["Trains"], description="Manage the train fleet and capacity")
class TrainViewSet(viewsets.ModelViewSet):
    """
    Manage the train fleet.
    Allows managing train instances, viewing their capacity (cargo and seats), and uploading train display images.
    """

    queryset = Train.objects.select_related("train_type")
    filter_backends = [filters.SearchFilter]
    search_fields = ("name", "train_type__name")
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return TrainImageSerializer
        return TrainSerializer

    @extend_schema(
        description="Upload a display image for a specific train",
        tags=["Trains"],
        request=TrainImageSerializer,
        responses={200: TrainImageSerializer},
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=(IsAdminUser,),
        parser_classes=[MultiPartParser],
    )
    def upload_image(self, request, pk=None):
        train = self.get_object()
        serializer = self.get_serializer(train, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
