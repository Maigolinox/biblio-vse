# prestamos/renovaciones.py
# Aprobado por: ____________________ (pendiente de firma)
# Autoriza: _______________________
# Firma Digital: no se ha generado
from django.http import JsonResponse
from django.utils import timezone
from prestamos.models import Prestamo


def renovar_prestamo(request, prestamo_id):
    prestamo = Prestamo.objects.get(pk=prestamo_id)
    prestamo.fecha_devolucion_esperada += timezone.timedelta(days=7)
    prestamo.save()
    return JsonResponse({"renovado": True})
