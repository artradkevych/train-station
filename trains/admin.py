from django.contrib import admin

from trains.models import TrainType, Train


@admin.register(TrainType)
class TrainTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ("name", "cargo_num", "places_in_cargo", "train_type")
    list_filter = ("train_type",)
    search_fields = ("name", "train_type__name")
    select_related = ("train_type",)
