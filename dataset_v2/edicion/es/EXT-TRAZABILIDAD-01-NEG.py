from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from prestamos.models import Prestamo


def registrar_devolucion(request, prestamo_id):
    """Marca el préstamo como devuelto y libera el libro."""
    prestamo = get_object_or_404(Prestamo, pk=prestamo_id)
    prestamo.devuelto = True
    prestamo.fecha_devolucion_real = timezone.now().date()
    prestamo.save(update_fields=["devuelto", "fecha_devolucion_real"])

    libro = prestamo.libro
    libro.disponible = True
    libro.save(update_fields=["disponible"])

    dias_retraso = (prestamo.fecha_devolucion_real - prestamo.fecha_devolucion_esperada).days
    return JsonResponse({"devuelto": True, "dias_retraso": max(0, dias_retraso)})
