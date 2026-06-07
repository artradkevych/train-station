from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from routes.admin import StationAdmin, RouteAdmin, TripAdmin
from routes.models import Station, Route, Trip
from routes.tests.helpers import sample_station, sample_route, sample_trip


class StationAdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = StationAdmin(Station, self.site)

    def test_list_display(self):
        self.assertEqual(self.admin.list_display, ("name", "latitude", "longitude"))

    def test_search_fields(self):
        self.assertEqual(self.admin.search_fields, ("name",))

    def test_station_str(self):
        station = sample_station(name="Kyiv", latitude=50.45, longitude=30.52)

        self.assertEqual(str(station), "Kyiv")


class RouteAdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = RouteAdmin(Route, self.site)

    def test_list_display(self):
        self.assertEqual(self.admin.list_display, ("source", "destination", "distance"))

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ("source", "destination"))

    def test_search_fields(self):
        self.assertEqual(self.admin.search_fields, ("source__name", "destination__name"))

    def test_route_str(self):
        route = sample_route()

        self.assertIn(str(route.id), str(route))
        self.assertIn("km", str(route))


class TripAdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = TripAdmin(Trip, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display,
            ("id", "route", "train", "departure_time", "arrival_time"),
        )

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ("train", "route"))

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            ("train__name", "route__source__name", "route__destination__name"),
        )

    def test_trip_str(self):
        trip = sample_trip()

        self.assertIn("Departure", str(trip))
