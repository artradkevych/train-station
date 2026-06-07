from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from trains.models import TrainType
from trains.tests.helpers import sample_train_type
from users.tests.helpers import sample_user, get_auth_header

TRAIN_TYPE_LIST_URL = reverse("trains:traintype-list")


def train_type_detail_url(train_type_id):
    return reverse("trains:traintype-detail", args=[train_type_id])


class TrainTypeViewSetUnauthenticatedTests(APITestCase):

    def test_list_train_types_unauthenticated(self):
        res = self.client.get(TRAIN_TYPE_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_train_type_unauthenticated(self):
        res = self.client.post(TRAIN_TYPE_LIST_URL, {"name": "Intercity"})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TrainTypeViewSetTests(APITestCase):

    def setUp(self):
        self.admin = sample_user(email="admin@example.com", is_staff=True)
        self.admin_auth = get_auth_header(self.admin)

        self.regular_user = sample_user(email="regular@example.com", is_staff=False)
        self.regular_auth = get_auth_header(self.regular_user)

    def test_list_train_types_as_authenticated(self):
        sample_train_type("Regional")
        sample_train_type("Intercity")

        res = self.client.get(TRAIN_TYPE_LIST_URL, **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_train_type_as_admin(self):
        res = self.client.post(
            TRAIN_TYPE_LIST_URL, {"name": "High-Speed"}, **self.admin_auth
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TrainType.objects.filter(name="High-Speed").exists())

    def test_create_train_type_as_non_admin_returns_403(self):
        res = self.client.post(
            TRAIN_TYPE_LIST_URL, {"name": "High-Speed"}, **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_train_type(self):
        train_type = sample_train_type("Regional")

        res = self.client.get(train_type_detail_url(train_type.id), **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Regional")

    def test_update_train_type_as_admin(self):
        train_type = sample_train_type("OldName")

        res = self.client.patch(
            train_type_detail_url(train_type.id), {"name": "NewName"}, **self.admin_auth
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        train_type.refresh_from_db()
        self.assertEqual(train_type.name, "NewName")

    def test_update_train_type_as_non_admin_returns_403(self):
        train_type = sample_train_type("Regional")

        res = self.client.patch(
            train_type_detail_url(train_type.id),
            {"name": "NewName"},
            **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_train_type_as_admin(self):
        train_type = sample_train_type("ToDelete")

        res = self.client.delete(
            train_type_detail_url(train_type.id), **self.admin_auth
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TrainType.objects.filter(id=train_type.id).exists())

    def test_delete_train_type_as_non_admin_returns_403(self):
        train_type = sample_train_type("Regional")

        res = self.client.delete(
            train_type_detail_url(train_type.id), **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_train_type_str(self):
        train_type = sample_train_type("Regional")

        self.assertEqual(str(train_type), "Regional")
