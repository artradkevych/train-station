from django.contrib import admin

from orders.models import Order, Ticket


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "user")
    list_filter = ("created_at",)
    search_fields = ("user__email", "id")
    list_select_related = ("user",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "cargo", "seat", "trip", "order")
    list_filter = ("trip__train", "order")
    search_fields = (
        "trip__train__name",
        "order__user__email",
    )
    list_select_related = (
        "trip__train",
        "trip__route",
        "order__user",
    )
