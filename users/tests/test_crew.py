from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import Crew
from tests.helpers import sample_user, create_crew, get_auth_header

User = get_user_model()

CREW_LIST_URL = reverse("users:crew-list")


def crew_detail_url(crew_id):
    return reverse("users:crew-detail", args=[crew_id])


class CrewViewSetUnauthenticatedTests(APITestCase):

    def test_list_crew_unauthenticated(self):
        res = self.client.get(CREW_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_crew_unauthenticated(self):
        payload = {
            "user": {"email": "newcrew@example.com", "password": "pass1234"},
            "first_name": "Jane",
            "last_name": "Doe",
        }
        res = self.client.post(CREW_LIST_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class CrewViewSetTests(APITestCase):

    def setUp(self):
        self.admin = sample_user(email="admin@example.com", is_staff=True)
        self.admin_auth = get_auth_header(self.admin)

        self.regular_user = sample_user(email="regular@example.com", is_staff=False)
        self.regular_auth = get_auth_header(self.regular_user)

    def test_list_crew_as_admin(self):
        create_crew(
            sample_user(email="c1@example.com"), first_name="Alice", last_name="Smith"
        )
        create_crew(
            sample_user(email="c2@example.com"), first_name="Bob", last_name="Jones"
        )

        res = self.client.get(CREW_LIST_URL, **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_list_crew_as_authenticated_non_admin(self):
        res = self.client.get(CREW_LIST_URL, **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_crew_as_admin(self):
        payload = {
            "user": {"email": "newcrew@example.com", "password": "pass1234"},
            "first_name": "Jane",
            "last_name": "Doe",
        }
        res = self.client.post(CREW_LIST_URL, payload, format="json", **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newcrew@example.com").exists())
        self.assertTrue(
            Crew.objects.filter(first_name="Jane", last_name="Doe").exists()
        )

    def test_create_crew_as_non_admin_returns_403(self):
        payload = {
            "user": {"email": "newcrew2@example.com", "password": "pass1234"},
            "first_name": "Jane",
            "last_name": "Doe",
        }
        res = self.client.post(
            CREW_LIST_URL, payload, format="json", **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_crew_missing_user_data_returns_400(self):
        payload = {"first_name": "Jane", "last_name": "Doe"}
        res = self.client.post(CREW_LIST_URL, payload, format="json", **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_crew_invalid_user_password_returns_400(self):
        payload = {
            "user": {"email": "bad@example.com", "password": "ab"},
            "first_name": "Jane",
            "last_name": "Doe",
        }
        res = self.client.post(CREW_LIST_URL, payload, format="json", **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="bad@example.com").exists())

    def test_retrieve_crew_detail_as_admin(self):
        crew = create_crew(sample_user(email="detail@example.com"))

        res = self.client.get(crew_detail_url(crew.id), **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["full_name"], crew.full_name)

    def test_retrieve_crew_detail_as_non_admin(self):
        crew = create_crew(sample_user(email="detail2@example.com"))

        res = self.client.get(crew_detail_url(crew.id), **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_full_name_in_response(self):
        crew = create_crew(
            sample_user(email="fn@example.com"), first_name="Anna", last_name="Bell"
        )
        res = self.client.get(crew_detail_url(crew.id), **self.admin_auth)

        self.assertEqual(res.data["full_name"], "Anna Bell")

    def test_partial_update_crew_as_admin(self):
        crew = create_crew(sample_user(email="upd@example.com"), first_name="Old")

        res = self.client.patch(
            crew_detail_url(crew.id),
            {"first_name": "New"},
            format="json",
            **self.admin_auth
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        crew.refresh_from_db()
        self.assertEqual(crew.first_name, "New")

    def test_partial_update_crew_as_non_admin_returns_403(self):
        crew = create_crew(sample_user(email="upd2@example.com"), first_name="Old")

        res = self.client.patch(
            crew_detail_url(crew.id),
            {"first_name": "New"},
            format="json",
            **self.regular_auth
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_crew_as_admin(self):
        crew = create_crew(sample_user(email="del@example.com"))

        res = self.client.delete(crew_detail_url(crew.id), **self.admin_auth)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Crew.objects.filter(id=crew.id).exists())

    def test_delete_crew_as_non_admin_returns_403(self):
        crew = create_crew(sample_user(email="del2@example.com"))

        res = self.client.delete(crew_detail_url(crew.id), **self.regular_auth)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Crew.objects.filter(id=crew.id).exists())
