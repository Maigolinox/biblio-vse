# prestamos/views_legacy.py
# ADVERTENCIA: Esta función fue refactorizada en el sprint 6.
# La implementación original de RF_05_Gestión_Préstamos fue migrada
# a prestamos/views.py. Este módulo ya NO implementa RF_05 ni
# ningún otro requerimiento activo. Conservado solo por referencia histórica.
from django.shortcuts import get_object_or_404
from prestamos.models import Prestamo
from django.http import JsonResponse

def registrar_prestamo_legacy(request):
    # Función desactivada — no usar en producción
    return JsonResponse({"error": "Módulo fuera de servicio"}, status=410)

def consultar_historial_legacy(request, user_id):
    # Ver US_03 en prestamos/views.py para la implementación vigente
    return JsonResponse({"error": "Módulo fuera de servicio"}, status=410)
