from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tests.helpers import sample_user

User = get_user_model()

CREATE_USER_URL = reverse("users:create")


class CreateUserViewTests(APITestCase):

    def test_create_user_success(self):
        payload = {"email": "new@example.com", "password": "strongpass"}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_password_too_short_returns_400(self):
        payload = {"email": "short@example.com", "password": "abc"}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=payload["email"]).exists())

    def test_duplicate_email_returns_400(self):
        sample_user(email="dup@example.com")
        payload = {"email": "dup@example.com", "password": "pass1234"}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_is_staff_is_read_only(self):
        payload = {"email": "admin@example.com", "password": "pass1234", "is_staff": True}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=payload["email"])
        self.assertFalse(user.is_staff)
