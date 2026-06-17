from trains.models import TrainType, Train


def sample_train_type(name="Regional"):
    return TrainType.objects.get_or_create(name=name)[0]


def sample_train(**kwargs):
    name = kwargs.pop("name", "Express 100")
    defaults = {
        "cargo_num": 5,
        "places_in_cargo": 20,
        "train_type": sample_train_type(),
    }
    defaults.update(kwargs)
    train, _ = Train.objects.get_or_create(name=name, defaults=defaults)
    return train
