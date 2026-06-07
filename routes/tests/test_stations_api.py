from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from routes.models import Station
from routes.tests.helpers import sample_station
from users.tests.helpers import sample_user, get_auth_header

STATION_LIST_URL = reverse("routes:station-list")


def station_detail_url(station_id):
    return reverse("routes:station-detail", args=[station_id])


class StationViewSetUnauthenticatedTests(APITestCase):

    def test_list_stations_unauthenticated(self):
        res = self.client.get(STATION_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_station_unauthenticated(self):
        payload = {"name": "Odesa", "latitude": 46.47, "longitude": 30.73}
        res = self.client.post(STATION_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class StationViewSetTests(APITestCase):

    def setUp(self):
        self.admin = sample_user(email="admin@example.com", is_staff=True)
        self.admin_auth = get_auth_header(self.admin)

        self.regular_user = sample_user(email="regular@example.com", is_staff=False)
        self.regular_auth = get_auth_header(self.regular_user)

    def test_list_stations_as_authenticated(self):
        sample_station(name="Kyiv", latitude=50.45, longitude=30.52)
        sample_station(name="Lviv", latitude=49.84, longitude=24.03)

        res = self.client.get(STATION_LIST_URL, **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_station_as_admin(self):
        payload = {"name": "Odesa", "latitude": 46.47, "longitude": 30.73}
        res = self.client.post(STATION_LIST_URL, payload, **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Station.objects.filter(name="Odesa").exists())

    def test_create_station_as_non_admin_returns_403(self):
        payload = {"name": "Odesa", "latitude": 46.47, "longitude": 30.73}
        res = self.client.post(STATION_LIST_URL, payload, **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_station(self):
        station = sample_station(name="Kharkiv", latitude=49.99, longitude=36.23)

        res = self.client.get(station_detail_url(station.id), **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Kharkiv")

    def test_update_station_as_admin(self):
        station = sample_station(name="OldName", latitude=50.0, longitude=30.0)

        res = self.client.patch(
            station_detail_url(station.id), {"name": "NewName"}, **self.admin_auth
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        station.refresh_from_db()
        self.assertEqual(station.name, "NewName")

    def test_update_station_as_non_admin_returns_403(self):
        station = sample_station(name="Kyiv", latitude=50.45, longitude=30.52)

        res = self.client.patch(
            station_detail_url(station.id), {"name": "NewName"}, **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_station_as_admin(self):
        station = sample_station(name="ToDelete", latitude=50.0, longitude=30.0)

        res = self.client.delete(station_detail_url(station.id), **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Station.objects.filter(id=station.id).exists())

    def test_delete_station_as_non_admin_returns_403(self):
        station = sample_station(name="Kyiv", latitude=50.45, longitude=30.52)

        res = self.client.delete(station_detail_url(station.id), **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_station_str(self):
        station = sample_station(name="Kyiv", latitude=50.45, longitude=30.52)

        self.assertEqual(str(station), "Kyiv")
