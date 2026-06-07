from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from users.models import Crew
from users.permissions import IsAdminOrIfAuthenticatedReadOnly
from users.serializers import UserSerializer, CrewSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Manage the authenticated user's profile.
    Provides endpoints to retrieve or update the current user's personal details.
    """

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class CrewViewSet(viewsets.ModelViewSet):
    """
    Manage train crew members.
    Allows administrators to view, create, update, or remove crew personnel records.
    """

    queryset = Crew.objects.select_related("user")
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
