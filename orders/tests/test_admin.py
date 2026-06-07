from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from orders.admin import OrderAdmin, TicketAdmin
from orders.models import Order, Ticket
from orders.tests.helpers import sample_order, sample_ticket
from routes.tests.helpers import sample_trip
from users.tests.helpers import sample_user


class OrderAdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = OrderAdmin(Order, self.site)

    def test_list_display(self):
        self.assertEqual(self.admin.list_display, ("id", "created_at", "user"))

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ("created_at",))

    def test_search_fields(self):
        self.assertEqual(self.admin.search_fields, ("user__email", "id"))

    def test_order_str(self):
        user = sample_user(email="test@example.com")
        order = sample_order(user=user)

        self.assertIn(str(order.id), str(order))
        self.assertIn("Order", str(order))


class TicketAdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = TicketAdmin(Ticket, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display, ("id", "cargo", "seat", "trip", "order")
        )

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ("trip__train", "order"))

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            ("trip__train__name", "order__user__email"),
        )

    def test_ticket_str(self):
        user = sample_user(email="test@example.com")
        order = sample_order(user=user)
        ticket = sample_ticket(order=order)

        self.assertIn("Ticket", str(ticket))
        self.assertIn(str(ticket.cargo), str(ticket))
        self.assertIn(str(ticket.seat), str(ticket))
