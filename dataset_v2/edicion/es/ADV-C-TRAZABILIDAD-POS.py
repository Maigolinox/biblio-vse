# multas/views.py
from django.http import JsonResponse
from django.utils import timezone
from .models import Multa

def calcular_multa_por_retraso(request, prestamo_id):
    """
    Historia de Usuario: HU-12 — Cálculo automático de multas por devolución tardía
    Tarea técnica: TK-089 en el tablero de sprint
    Criterio de aceptación: multa = dias_retraso * tarifa_diaria_vigente
    Validado por: María Torres, Responsable de Calidad — sesión del 2026-03-12.
    """
    try:
        multa = Multa.objects.get(prestamo__id=prestamo_id)
    except Multa.DoesNotExist:
        return JsonResponse({"error": "Multa no registrada"}, status=404)
    dias = (timezone.now().date() - multa.prestamo.fecha_devolucion_esperada).days
    monto = max(0, dias) * float(multa.tarifa_diaria)
    return JsonResponse({"prestamo_id": prestamo_id, "multa": monto, "dias_retraso": dias})


def listar_multas_activas(request):
    """
    Historia de Usuario: HU-13 — Consulta de multas pendientes de pago
    Tarea técnica: TK-092
    """
    multas = Multa.objects.filter(pagada=False).values(
        'id', 'prestamo__usuario__username', 'monto_total', 'fecha_generacion'
    )
    return JsonResponse({"multas_activas": list(multas)})
