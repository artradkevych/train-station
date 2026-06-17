import tempfile
from PIL import Image

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from trains.models import Train
from trains.tests.helpers import sample_train, sample_train_type
from users.tests.helpers import sample_user, get_auth_header

TRAIN_LIST_URL = reverse("trains:train-list")


def train_detail_url(train_id):
    return reverse("trains:train-detail", args=[train_id])


def train_upload_image_url(train_id):
    return reverse("trains:train-upload-image", args=[train_id])


class TrainViewSetUnauthenticatedTests(APITestCase):

    def test_list_trains_unauthenticated(self):
        res = self.client.get(TRAIN_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_train_unauthenticated(self):
        payload = {
            "name": "Express 1",
            "cargo_num": 5,
            "places_in_cargo": 20,
            "train_type": "Regional",
        }
        res = self.client.post(TRAIN_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TrainViewSetTests(APITestCase):

    def setUp(self):
        self.admin = sample_user(email="admin@example.com", is_staff=True)
        self.admin_auth = get_auth_header(self.admin)

        self.regular_user = sample_user(email="regular@example.com", is_staff=False)
        self.regular_auth = get_auth_header(self.regular_user)

    def test_list_trains_as_authenticated(self):
        sample_train(name="Train A")
        sample_train(name="Train B")

        res = self.client.get(TRAIN_LIST_URL, **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_train_as_admin(self):
        payload = {
            "name": "New Express",
            "cargo_num": 4,
            "places_in_cargo": 10,
            "train_type": "Regional",
        }
        res = self.client.post(
            TRAIN_LIST_URL, payload, format="json", **self.admin_auth
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Train.objects.filter(name="New Express").exists())

    def test_create_train_creates_train_type_if_not_exists(self):
        payload = {
            "name": "Brand New",
            "cargo_num": 3,
            "places_in_cargo": 15,
            "train_type": "NonExistentType",
        }
        res = self.client.post(
            TRAIN_LIST_URL, payload, format="json", **self.admin_auth
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        train = Train.objects.get(name="Brand New")
        self.assertEqual(train.train_type.name, "NonExistentType")

    def test_create_train_as_non_admin_returns_403(self):
        payload = {
            "name": "Forbidden Train",
            "cargo_num": 2,
            "places_in_cargo": 10,
            "train_type": "Regional",
        }
        res = self.client.post(
            TRAIN_LIST_URL, payload, format="json", **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_train(self):
        train = sample_train()

        res = self.client.get(train_detail_url(train.id), **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], train.name)

    def test_capacity_in_response(self):
        train = sample_train(cargo_num=5, places_in_cargo=20)

        res = self.client.get(train_detail_url(train.id), **self.regular_auth)

        self.assertEqual(res.data["capacity"], 100)

    def test_search_by_name(self):
        sample_train(name="Alpha Express")
        sample_train(name="Beta Local")

        res = self.client.get(TRAIN_LIST_URL, {"search": "Alpha"}, **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], "Alpha Express")

    def test_search_by_train_type(self):
        regional = sample_train_type("Regional")
        intercity = sample_train_type("Intercity")
        sample_train(name="Train A", train_type=regional)
        sample_train(name="Train B", train_type=intercity)

        res = self.client.get(
            TRAIN_LIST_URL, {"search": "Regional"}, **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], "Train A")

    def test_partial_update_train_as_admin(self):
        train = sample_train()

        res = self.client.patch(
            train_detail_url(train.id), {"name": "Updated"}, **self.admin_auth
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        train.refresh_from_db()
        self.assertEqual(train.name, "Updated")

    def test_partial_update_train_as_non_admin_returns_403(self):
        train = sample_train()

        res = self.client.patch(
            train_detail_url(train.id), {"name": "Updated"}, **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_train_as_admin(self):
        train = sample_train()

        res = self.client.delete(train_detail_url(train.id), **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Train.objects.filter(id=train.id).exists())

    def test_delete_train_as_non_admin_returns_403(self):
        train = sample_train()

        res = self.client.delete(train_detail_url(train.id), **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_train_str(self):
        train = sample_train(name="My Train")

        self.assertEqual(str(train), "My Train")

    def test_upload_image_as_admin(self):
        train = sample_train()

        with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
            img = Image.new("RGB", (10, 10))
            img.save(f, format="JPEG")
            f.seek(0)
            res = self.client.post(
                train_upload_image_url(train.id),
                {"image": f},
                format="multipart",
                **self.admin_auth,
            )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        train.refresh_from_db()
        self.assertTrue(train.image)

    def test_upload_image_as_non_admin_returns_403(self):
        train = sample_train()

        with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
            img = Image.new("RGB", (10, 10))
            img.save(f, format="JPEG")
            f.seek(0)
            res = self.client.post(
                train_upload_image_url(train.id),
                {"image": f},
                format="multipart",
                **self.regular_auth,
            )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
