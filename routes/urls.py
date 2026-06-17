from django.urls import path, include
from rest_framework.routers import DefaultRouter

from routes.views import StationViewSet, RouteViewSet, TripViewSet

router = DefaultRouter()
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("trips", TripViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "routes"
