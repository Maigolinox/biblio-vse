# prestamos/views.py
from django.http import JsonResponse

def registrar_prestamo(request):
    """
    ID Requerimiento: RF_05_Gestión_Préstamos
    Descripción: Registra un nuevo préstamo de libro en el sistema.
    Caso de Prueba Asociado: TEST_PRESTAMO_01
    """
    # Lógica simulada
    return JsonResponse({"status": "success", "message": "Préstamo registrado"})