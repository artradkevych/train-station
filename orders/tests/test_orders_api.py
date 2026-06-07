from datetime import timezone as dt_timezone

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Order, Ticket
from orders.tests.helpers import sample_order, sample_ticket
from routes.tests.helpers import sample_trip, sample_route, sample_station
from trains.tests.helpers import sample_train
from users.tests.helpers import sample_user, get_auth_header

ORDER_LIST_URL = reverse("orders:order-list")


def order_detail_url(order_id):
    return reverse("orders:order-detail", args=[order_id])


class OrderViewSetUnauthenticatedTests(APITestCase):

    def test_list_orders_unauthenticated(self):
        res = self.client.get(ORDER_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_unauthenticated(self):
        res = self.client.post(ORDER_LIST_URL, {})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderViewSetTests(APITestCase):

    def setUp(self):
        self.user = sample_user(email="user@example.com")
        self.auth = get_auth_header(self.user)

        self.other_user = sample_user(email="other@example.com")
        self.other_auth = get_auth_header(self.other_user)

        self.route = sample_route()
        self.train = sample_train(name="Default Train")
        self.trip = sample_trip(route=self.route, train=self.train)

    def test_list_orders_as_authenticated(self):
        sample_order(user=self.user)

        res = self.client.get(ORDER_LIST_URL, **self.auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_list_orders_returns_only_own_orders(self):
        sample_order(user=self.user)
        sample_order(user=self.other_user)

        res = self.client.get(ORDER_LIST_URL, **self.auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_list_orders_uses_list_serializer(self):
        order = sample_order(user=self.user)
        sample_ticket(order=order, trip=self.trip, cargo=1, seat=1)

        res = self.client.get(ORDER_LIST_URL, **self.auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("tickets", res.data[0])
        ticket = res.data[0]["tickets"][0]
        self.assertIsInstance(ticket["trip"], dict)

    def test_create_order_with_tickets(self):
        payload = {
            "tickets": [
                {"cargo": 1, "seat": 1, "trip": self.trip.id},
            ]
        }

        res = self.client.post(ORDER_LIST_URL, payload, format="json", **self.auth)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        self.assertEqual(Ticket.objects.filter(trip=self.trip).count(), 1)

    def test_create_order_assigns_current_user(self):
        payload = {
            "tickets": [
                {"cargo": 1, "seat": 1, "trip": self.trip.id},
            ]
        }

        res = self.client.post(ORDER_LIST_URL, payload, format="json", **self.auth)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=res.data["id"])
        self.assertEqual(order.user, self.user)

    def test_create_order_with_empty_tickets_returns_400(self):
        payload = {"tickets": []}

        res = self.client.post(ORDER_LIST_URL, payload, format="json", **self.auth)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_invalid_cargo_returns_400(self):
        payload = {
            "tickets": [
                {"cargo": 9999, "seat": 1, "trip": self.trip.id},
            ]
        }

        res = self.client.post(ORDER_LIST_URL, payload, format="json", **self.auth)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_invalid_seat_returns_400(self):
        payload = {
            "tickets": [
                {"cargo": 1, "seat": 9999, "trip": self.trip.id},
            ]
        }

        res = self.client.post(ORDER_LIST_URL, payload, format="json", **self.auth)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_duplicate_seat_returns_400(self):
        order = sample_order(user=self.user)
        sample_ticket(order=order, trip=self.trip, cargo=1, seat=1)

        payload = {
            "tickets": [
                {"cargo": 1, "seat": 1, "trip": self.trip.id},
            ]
        }

        res = self.client.post(ORDER_LIST_URL, payload, format="json", **self.auth)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_own_order(self):
        order = sample_order(user=self.user)

        res = self.client.delete(order_detail_url(order.id), **self.auth)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order.id).exists())

    def test_delete_other_users_order_returns_404(self):
        order = sample_order(user=self.other_user)

        res = self.client.delete(order_detail_url(order.id), **self.auth)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_trip(self):
        train_b = sample_train(name="Train B")
        route2 = sample_route(
            source=sample_station(name="Odesa", latitude=46.47, longitude=30.73),
            destination=sample_station(name="Dnipro", latitude=48.46, longitude=35.04),
            distance=480,
        )
        trip2 = sample_trip(route=route2, train=train_b)

        order1 = sample_order(user=self.user)
        order2 = sample_order(user=self.user)
        sample_ticket(order=order1, trip=self.trip, cargo=1, seat=1)
        sample_ticket(order=order2, trip=trip2, cargo=1, seat=1)

        res = self.client.get(ORDER_LIST_URL, {"trip": self.trip.id}, **self.auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_filter_by_departure_time_range(self):
        train_b = sample_train(name="Train B")
        route2 = sample_route(
            source=sample_station(name="Odesa", latitude=46.47, longitude=30.73),
            destination=sample_station(name="Dnipro", latitude=48.46, longitude=35.04),
            distance=480,
        )
        trip_jan = sample_trip(
            route=self.route,
            train=self.train,
            departure_time=timezone.datetime(
                2025, 1, 10, 10, 0, tzinfo=dt_timezone.utc
            ),
            arrival_time=timezone.datetime(2025, 1, 10, 16, 0, tzinfo=dt_timezone.utc),
        )
        trip_jun = sample_trip(
            route=route2,
            train=train_b,
            departure_time=timezone.datetime(
                2025, 6, 10, 10, 0, tzinfo=dt_timezone.utc
            ),
            arrival_time=timezone.datetime(2025, 6, 10, 16, 0, tzinfo=dt_timezone.utc),
        )

        order1 = sample_order(user=self.user)
        order2 = sample_order(user=self.user)
        sample_ticket(order=order1, trip=trip_jan, cargo=1, seat=1)
        sample_ticket(order=order2, trip=trip_jun, cargo=1, seat=1)

        res = self.client.get(
            ORDER_LIST_URL,
            {
                "departure_time_after": "2025-01-01T00:00:00Z",
                "departure_time_before": "2025-02-01T00:00:00Z",
            },
            **self.auth,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_ordering_by_departure_time(self):
        train_b = sample_train(name="Train B")
        route2 = sample_route(
            source=sample_station(name="Odesa", latitude=46.47, longitude=30.73),
            destination=sample_station(name="Dnipro", latitude=48.46, longitude=35.04),
            distance=480,
        )
        trip_jun = sample_trip(
            route=self.route,
            train=self.train,
            departure_time=timezone.datetime(2025, 6, 1, 10, 0, tzinfo=dt_timezone.utc),
            arrival_time=timezone.datetime(2025, 6, 1, 16, 0, tzinfo=dt_timezone.utc),
        )
        trip_jan = sample_trip(
            route=route2,
            train=train_b,
            departure_time=timezone.datetime(2025, 1, 1, 10, 0, tzinfo=dt_timezone.utc),
            arrival_time=timezone.datetime(2025, 1, 1, 16, 0, tzinfo=dt_timezone.utc),
        )

        order1 = sample_order(user=self.user)
        order2 = sample_order(user=self.user)
        sample_ticket(order=order1, trip=trip_jun, cargo=1, seat=1)
        sample_ticket(order=order2, trip=trip_jan, cargo=1, seat=1)

        res = self.client.get(
            ORDER_LIST_URL,
            {"ordering": "tickets__trip__departure_time"},
            **self.auth,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        first_ticket = res.data[0]["tickets"][0]
        second_ticket = res.data[1]["tickets"][0]
        self.assertLess(
            first_ticket["trip"]["departure_time"],
            second_ticket["trip"]["departure_time"],
        )

    def test_order_str(self):
        order = sample_order(user=self.user)

        self.assertIn(str(order.id), str(order))
        self.assertIn("Order", str(order))

    def test_ticket_str(self):
        order = sample_order(user=self.user)
        ticket = sample_ticket(order=order, trip=self.trip, cargo=2, seat=3)

        self.assertIn("Ticket", str(ticket))
        self.assertIn("2", str(ticket))
        self.assertIn("3", str(ticket))
