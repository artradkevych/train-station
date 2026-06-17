from django.utils import timezone

from routes.models import Station, Route, Trip
from trains.tests.helpers import sample_train
from datetime import timedelta


def sample_station(**kwargs):
    defaults = {"name": "Kyiv", "latitude": 50.45, "longitude": 30.52}
    defaults.update(kwargs)
    return Station.objects.get_or_create(name=defaults["name"], defaults=defaults)[0]


def sample_route(**kwargs):
    defaults = {
        "source": sample_station(name="Kyiv", latitude=50.45, longitude=30.52),
        "destination": sample_station(name="Lviv", latitude=49.84, longitude=24.03),
        "distance": 540,
    }
    defaults.update(kwargs)
    return Route.objects.create(**defaults)


def sample_trip(**kwargs):
    defaults = {
        "route": sample_route(),
        "train": sample_train(),
        "departure_time": timezone.now(),
        "arrival_time": timezone.now() + timedelta(hours=6),
    }
    defaults.update(kwargs)
    return Trip.objects.create(**defaults)
