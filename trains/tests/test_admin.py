from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from trains.admin import TrainTypeAdmin, TrainAdmin
from trains.models import TrainType, Train
from trains.tests.helpers import sample_train, sample_train_type


class TrainTypeAdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = TrainTypeAdmin(TrainType, self.site)

    def test_list_display(self):
        self.assertEqual(self.admin.list_display, ("name",))

    def test_search_fields(self):
        self.assertEqual(self.admin.search_fields, ("name",))

    def test_train_type_str(self):
        train_type = sample_train_type("Regional")

        self.assertEqual(str(train_type), "Regional")


class TrainAdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = TrainAdmin(Train, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display,
            ("name", "cargo_num", "places_in_cargo", "train_type"),
        )

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ("train_type",))

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            ("name", "train_type__name"),
        )

    def test_train_str(self):
        train = sample_train(name="Express 100")

        self.assertEqual(str(train), "Express 100")
