from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("api-auth/", include("rest_framework.urls")),
        path("api/users/", include("users.urls", namespace="users")),
        path("api/railway/fleet/", include("trains.urls", namespace="trains")),
        path("api/railway/navigation/", include("routes.urls", namespace="routes")),
        path("api/railway/booking/", include("orders.urls", namespace="orders")),
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/doc/swagger/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/doc/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]
    + debug_toolbar_urls()
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
