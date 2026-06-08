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


class TrainTypeViewSet(viewsets.ModelViewSet):
    """
    Manage train types and categories.
    Provides CRUD operations to define train classifications (e.g., Regional, Intercity, High-Speed).
    """

    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainViewSet(viewsets.ModelViewSet):
    """
    Manage the train fleet.
    Allows managing train instances, viewing their capacity (cargo and seats), and uploading train display images.
    """

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

    @extend_schema(
        description="Upload an image to a specific train instance.",
        responses={200: "Image successfully uploaded."},
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=(IsAdminUser,),
        parser_classes=[MultiPartParser],  # This forces multipart/form-data in docs
    )
    def upload_image(self, request, pk=None):
        train = self.get_object()
        serializer = self.get_serializer(train, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
