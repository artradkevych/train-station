from trains.models import TrainType, Train


def sample_train_type(name="Regional"):
    return TrainType.objects.get_or_create(name=name)[0]


def sample_train(**kwargs):
    defaults = {
        "name": "Express 100",
        "cargo_num": 5,
        "places_in_cargo": 20,
        "train_type": sample_train_type(),
    }
    defaults.update(kwargs)
    return Train.objects.create(**defaults)
