from orders.models import Order, Ticket
from routes.tests.helpers import sample_trip


def sample_order(user, **kwargs):
    defaults = {}
    defaults.update(kwargs)
    return Order.objects.create(user=user, **defaults)


def sample_ticket(order, trip=None, cargo=1, seat=1, **kwargs):
    if trip is None:
        trip = sample_trip()
    return Ticket.objects.create(
        order=order, trip=trip, cargo=cargo, seat=seat, **kwargs
    )
