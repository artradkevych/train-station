from django.contrib import admin

from routes.models import Station, Route, Trip


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "latitude",
        "longitude",
    )
    search_fields = ("name",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        "source",
        "destination",
        "distance",
    )
    list_filter = (
        "source",
        "destination",
    )
    search_fields = (
        "source__name",
        "destination__name",
    )
    select_related = (
        "source",
        "destination",
    )


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "train", "departure_time", "arrival_time")
    list_filter = ("train", "route")
    search_fields = ("train__name", "route__source__name", "route__destination__name")
    select_related = ("train", "route__source", "route__destination")
    filter_horizontal = ("crew",)
