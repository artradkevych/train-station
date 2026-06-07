from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from users.models import Crew
from users.serializers import UserSerializer, CrewSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.select_related("user")
    serializer_class = CrewSerializer
