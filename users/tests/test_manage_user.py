from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tests.helpers import sample_user, get_auth_header

ME_URL = reverse("users:manage")


class ManageUserViewTests(APITestCase):

    def setUp(self):
        self.user = sample_user()
        self.auth = get_auth_header(self.user)

    def test_retrieve_profile_authenticated(self):
        res = self.client.get(ME_URL, **self.auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertNotIn("password", res.data)

    def test_retrieve_profile_unauthenticated(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_email(self):
        res = self.client.patch(ME_URL, {"email": "updated@example.com"}, **self.auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updated@example.com")

    def test_update_password(self):
        res = self.client.patch(ME_URL, {"password": "newpass123"}, **self.auth)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))

    def test_update_password_too_short_returns_400(self):
        res = self.client.patch(ME_URL, {"password": "abc"}, **self.auth)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_me_not_allowed(self):
        res = self.client.post(ME_URL, {}, **self.auth)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
