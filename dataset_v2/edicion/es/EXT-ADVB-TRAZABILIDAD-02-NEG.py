from django.http import JsonResponse
from reservas.models import Reserva


def cancelar_reserva(request, reserva_id):
    """
    ID Requerimiento: pendiente de asignar
    Caso de Prueba Asociado: por definir cuando exista el requerimiento
    """
    reserva = Reserva.objects.get(pk=reserva_id)
    reserva.activa = False
    reserva.save(update_fields=["activa"])
    return JsonResponse({"cancelada": True})
