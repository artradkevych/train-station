from drf_spectacular.utils import extend_schema
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from users.models import Crew
from users.permissions import IsAdminOrIfAuthenticatedReadOnly
from users.serializers import UserSerializer, CrewSerializer


class CreateUserView(generics.CreateAPIView):
    """
    Create a new user account.
    Allows unauthenticated users to register and create a new account.
    """

    serializer_class = UserSerializer

    @extend_schema(
        description="Register a new user account",
        tags=["Users"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(tags=["Users"], description="Manage current user's profile")
class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Manage the authenticated user's profile.
    Provides endpoints to retrieve or update the current user's personal details.
    """

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


@extend_schema(
    tags=["Crew"], description="Manage train crew members and personnel records"
)
class CrewViewSet(viewsets.ModelViewSet):
    """
    Manage train crew members.
    Allows administrators to view, create, update, or remove crew personnel records.
    """

    queryset = Crew.objects.select_related("user")
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
