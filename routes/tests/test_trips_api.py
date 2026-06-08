from datetime import timezone as dt_timezone

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from routes.models import Trip
from routes.tests.helpers import sample_trip, sample_route, sample_station
from trains.tests.helpers import sample_train
from users.tests.helpers import sample_user, get_auth_header, create_crew

TRIP_LIST_URL = reverse("routes:trip-list")


def trip_detail_url(trip_id):
    return reverse("routes:trip-detail", args=[trip_id])


class TripViewSetUnauthenticatedTests(APITestCase):

    def test_list_trips_unauthenticated(self):
        res = self.client.get(TRIP_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_trip_unauthenticated(self):
        res = self.client.post(TRIP_LIST_URL, {})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TripViewSetTests(APITestCase):

    def setUp(self):
        self.admin = sample_user(email="admin@example.com", is_staff=True)
        self.admin_auth = get_auth_header(self.admin)

        self.regular_user = sample_user(email="regular@example.com", is_staff=False)
        self.regular_auth = get_auth_header(self.regular_user)

        self.route = sample_route()
        self.train = sample_train(name="Default Train")

    def test_list_trips_as_authenticated(self):
        sample_trip(route=self.route, train=self.train)

        res = self.client.get(TRIP_LIST_URL, **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_list_trips_uses_list_serializer(self):
        sample_trip(route=self.route, train=self.train)

        res = self.client.get(TRIP_LIST_URL, **self.regular_auth)

        self.assertIn("route_source", res.data[0])
        self.assertIn("route_destination", res.data[0])
        self.assertIn("tickets_available", res.data[0])

    def test_retrieve_trip_uses_detail_serializer(self):
        trip = sample_trip(route=self.route, train=self.train)

        res = self.client.get(trip_detail_url(trip.id), **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("taken_places", res.data)
        self.assertIsInstance(res.data["route"], dict)
        self.assertIsInstance(res.data["train"], dict)

    def test_create_trip_as_admin(self):
        crew = create_crew()
        payload = {
            "route": self.route.id,
            "train": self.train.id,
            "departure_time": "2025-01-01T10:00:00Z",
            "arrival_time": "2025-01-01T16:00:00Z",
            "crew": [crew.id],
        }

        res = self.client.post(TRIP_LIST_URL, payload, format="json", **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Trip.objects.filter(route=self.route, train=self.train).exists()
        )

    def test_create_trip_as_non_admin_returns_403(self):
        payload = {
            "route": self.route.id,
            "train": self.train.id,
            "departure_time": "2025-01-01T10:00:00Z",
            "arrival_time": "2025-01-01T16:00:00Z",
            "crew": [],
        }

        res = self.client.post(
            TRIP_LIST_URL, payload, format="json", **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_departure_time_range(self):
        train_b = sample_train(name="Train B")
        route2 = sample_route(
            source=sample_station(name="Odesa", latitude=46.47, longitude=30.73),
            destination=sample_station(name="Dnipro", latitude=48.46, longitude=35.04),
            distance=480,
        )
        sample_trip(
            route=self.route,
            train=self.train,
            departure_time=timezone.datetime(
                2025, 1, 10, 10, 0, tzinfo=dt_timezone.utc
            ),
            arrival_time=timezone.datetime(2025, 1, 10, 16, 0, tzinfo=dt_timezone.utc),
        )
        sample_trip(
            route=route2,
            train=train_b,
            departure_time=timezone.datetime(
                2025, 6, 10, 10, 0, tzinfo=dt_timezone.utc
            ),
            arrival_time=timezone.datetime(2025, 6, 10, 16, 0, tzinfo=dt_timezone.utc),
        )

        res = self.client.get(
            TRIP_LIST_URL,
            {
                "departure_time_after": "2025-01-01T00:00:00Z",
                "departure_time_before": "2025-02-01T00:00:00Z",
            },
            **self.regular_auth,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_filter_by_route(self):
        train_b = sample_train(name="Train B")
        route2 = sample_route(
            source=sample_station(name="Odesa", latitude=46.47, longitude=30.73),
            destination=sample_station(name="Dnipro", latitude=48.46, longitude=35.04),
            distance=480,
        )
        sample_trip(route=self.route, train=self.train)
        sample_trip(route=route2, train=train_b)

        res = self.client.get(
            TRIP_LIST_URL, {"route": self.route.id}, **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_filter_by_train(self):
        train_b = sample_train(name="Train B")
        route2 = sample_route(
            source=sample_station(name="Odesa", latitude=46.47, longitude=30.73),
            destination=sample_station(name="Dnipro", latitude=48.46, longitude=35.04),
            distance=480,
        )
        sample_trip(route=self.route, train=self.train)
        sample_trip(route=route2, train=train_b)

        res = self.client.get(
            TRIP_LIST_URL, {"train": self.train.id}, **self.regular_auth
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
        sample_trip(
            route=self.route,
            train=self.train,
            departure_time=timezone.datetime(2025, 6, 1, 10, 0, tzinfo=dt_timezone.utc),
            arrival_time=timezone.datetime(2025, 6, 1, 16, 0, tzinfo=dt_timezone.utc),
        )
        sample_trip(
            route=route2,
            train=train_b,
            departure_time=timezone.datetime(2025, 1, 1, 10, 0, tzinfo=dt_timezone.utc),
            arrival_time=timezone.datetime(2025, 1, 1, 16, 0, tzinfo=dt_timezone.utc),
        )

        res = self.client.get(
            TRIP_LIST_URL, {"ordering": "departure_time"}, **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertLess(res.data[0]["departure_time"], res.data[1]["departure_time"])

    def test_update_trip_as_admin(self):
        trip = sample_trip(route=self.route, train=self.train)
        new_train = sample_train(name="New Train")

        res = self.client.patch(
            trip_detail_url(trip.id), {"train": new_train.id}, **self.admin_auth
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        trip.refresh_from_db()
        self.assertEqual(trip.train.id, new_train.id)

    def test_update_trip_as_non_admin_returns_403(self):
        trip = sample_trip(route=self.route, train=self.train)
        new_train = sample_train(name="New Train")

        res = self.client.patch(
            trip_detail_url(trip.id), {"train": new_train.id}, **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_trip_as_admin(self):
        trip = sample_trip(route=self.route, train=self.train)

        res = self.client.delete(trip_detail_url(trip.id), **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Trip.objects.filter(id=trip.id).exists())

    def test_delete_trip_as_non_admin_returns_403(self):
        trip = sample_trip(route=self.route, train=self.train)

        res = self.client.delete(trip_detail_url(trip.id), **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_trip_str(self):
        trip = sample_trip(route=self.route, train=self.train)

        self.assertIn(str(trip.id), str(trip))
        self.assertIn("Departure", str(trip))

    def test_create_trip_with_arrival_before_departure_returns_400(self):
        crew = create_crew()
        payload = {
            "route": self.route.id,
            "train": self.train.id,
            "departure_time": "2025-01-01T16:00:00Z",
            "arrival_time": "2025-01-01T10:00:00Z",
            "crew": [crew.id],
        }

        res = self.client.post(TRIP_LIST_URL, payload, format="json", **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("arrival_time", res.data)

    def test_create_trip_with_equal_departure_and_arrival_returns_400(self):
        crew = create_crew()
        payload = {
            "route": self.route.id,
            "train": self.train.id,
            "departure_time": "2025-01-01T10:00:00Z",
            "arrival_time": "2025-01-01T10:00:00Z",
            "crew": [crew.id],
        }

        res = self.client.post(TRIP_LIST_URL, payload, format="json", **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("arrival_time", res.data)

    def test_patch_trip_with_invalid_departure_time_returns_400(self):
        trip = sample_trip(
            route=self.route,
            train=self.train,
            departure_time=timezone.datetime(2025, 1, 1, 10, 0, tzinfo=dt_timezone.utc),
            arrival_time=timezone.datetime(2025, 1, 1, 16, 0, tzinfo=dt_timezone.utc),
        )

        res = self.client.patch(
            trip_detail_url(trip.id),
            {"departure_time": "2025-01-01T20:00:00Z"},
            format="json",
            **self.admin_auth,
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("arrival_time", res.data)
