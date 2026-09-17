from django.http import JsonResponse
from reservations.models import Reservation


def cancel_reservation(request, reservation_id):
    """
    Requirement ID: pending assignment
    Associated Test Case: to be defined once the requirement exists
    """
    reservation = Reservation.objects.get(pk=reservation_id)
    reservation.active = False
    reservation.save(update_fields=["active"])
    return JsonResponse({"cancelled": True})
