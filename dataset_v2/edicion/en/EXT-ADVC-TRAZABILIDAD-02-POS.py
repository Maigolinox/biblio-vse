from django.utils import timezone
from reservations.models import Reservation

RESERVATION_VALIDITY_DAYS = 3


def expire_overdue_reservations():
    """
    Implements REQ-FUN-014 (automatic expiration of unclaimed reservations).
    Derived from story HISTORIA-031 on the client's board.
    """
    limit = timezone.now() - timezone.timedelta(days=RESERVATION_VALIDITY_DAYS)
    return Reservation.objects.filter(active=True, created__lt=limit).update(active=False)
