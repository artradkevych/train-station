from django.urls import path, include
from rest_framework.routers import DefaultRouter

from trains.views import TrainTypeViewSet, TrainViewSet

router = DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "trains"
