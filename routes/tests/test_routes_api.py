from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from routes.models import Route
from routes.tests.helpers import sample_route, sample_station
from users.tests.helpers import sample_user, get_auth_header

ROUTE_LIST_URL = reverse("routes:route-list")


def route_detail_url(route_id):
    return reverse("routes:route-detail", args=[route_id])


class RouteViewSetUnauthenticatedTests(APITestCase):

    def test_list_routes_unauthenticated(self):
        res = self.client.get(ROUTE_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_route_unauthenticated(self):
        source = sample_station(name="Kyiv", latitude=50.45, longitude=30.52)
        destination = sample_station(name="Lviv", latitude=49.84, longitude=24.03)
        res = self.client.post(
            ROUTE_LIST_URL,
            {"source": source.id, "destination": destination.id, "distance": 540},
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class RouteViewSetTests(APITestCase):

    def setUp(self):
        self.admin = sample_user(email="admin@example.com", is_staff=True)
        self.admin_auth = get_auth_header(self.admin)

        self.regular_user = sample_user(email="regular@example.com", is_staff=False)
        self.regular_auth = get_auth_header(self.regular_user)

    def test_list_routes_as_authenticated(self):
        sample_route()

        res = self.client.get(ROUTE_LIST_URL, **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_list_routes_uses_list_serializer(self):
        sample_route()

        res = self.client.get(ROUTE_LIST_URL, **self.regular_auth)

        self.assertIn("source", res.data[0])
        self.assertIsInstance(res.data[0]["source"], str)

    def test_retrieve_route_uses_detail_serializer(self):
        route = sample_route()

        res = self.client.get(route_detail_url(route.id), **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data["source"], dict)
        self.assertIsInstance(res.data["destination"], dict)

    def test_create_route_as_admin(self):
        source = sample_station(name="Kyiv", latitude=50.45, longitude=30.52)
        destination = sample_station(name="Lviv", latitude=49.84, longitude=24.03)
        payload = {"source": source.id, "destination": destination.id, "distance": 540}

        res = self.client.post(ROUTE_LIST_URL, payload, **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Route.objects.filter(source=source, destination=destination).exists()
        )

    def test_create_route_same_source_destination_returns_400(self):
        station = sample_station(name="Kyiv", latitude=50.45, longitude=30.52)
        payload = {"source": station.id, "destination": station.id, "distance": 0}

        res = self.client.post(ROUTE_LIST_URL, payload, **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_route_as_non_admin_returns_403(self):
        source = sample_station(name="Kyiv", latitude=50.45, longitude=30.52)
        destination = sample_station(name="Lviv", latitude=49.84, longitude=24.03)
        payload = {"source": source.id, "destination": destination.id, "distance": 540}

        res = self.client.post(ROUTE_LIST_URL, payload, **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_route_as_admin(self):
        source = sample_station(name="Kharkiv", latitude=49.99, longitude=36.23)
        destination = sample_station(
            name="Zaporizhzhia", latitude=47.83, longitude=35.14
        )
        route = sample_route(source=source, destination=destination, distance=300)

        res = self.client.patch(
            route_detail_url(route.id), {"distance": 999}, **self.admin_auth
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        route.refresh_from_db()
        self.assertEqual(route.distance, 999)

    def test_update_route_as_non_admin_returns_403(self):
        route = sample_route()

        res = self.client.patch(
            route_detail_url(route.id), {"distance": 999}, **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_route_as_admin(self):
        route = sample_route()

        res = self.client.delete(route_detail_url(route.id), **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Route.objects.filter(id=route.id).exists())

    def test_delete_route_as_non_admin_returns_403(self):
        route = sample_route()

        res = self.client.delete(route_detail_url(route.id), **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_route_str(self):
        route = sample_route()

        self.assertIn(str(route.id), str(route))
        self.assertIn("km", str(route))
