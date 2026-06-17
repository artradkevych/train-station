from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Crew

User = get_user_model()


def get_auth_header(user):
    token = RefreshToken.for_user(user).access_token
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


def sample_user(**kwargs):
    defaults = {"email": "user@example.com", "password": "pass1234"}
    defaults.update(kwargs)
    return User.objects.create_user(**defaults)


def create_crew(user=None, **kwargs):
    if user is None:
        user = sample_user(email="crew@example.com")
    defaults = {"first_name": "John", "last_name": "Doe"}
    defaults.update(kwargs)
    return Crew.objects.create(user=user, **defaults)
