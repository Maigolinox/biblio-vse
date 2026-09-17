"""Exportación del reporte mensual de préstamos en formato CSV."""
import csv
import io

from django.http import HttpResponse

from prestamos.models import Prestamo

DIAS_SIN_CARGO = 21
CARGO_POR_DIA_EXTRA = 2.5


def calcular_cargo(prestamo):
    """Calcula el cargo por los días que exceden el periodo sin cargo."""
    dias_extra = max(0, prestamo.dias_prestamo - DIAS_SIN_CARGO)
    return dias_extra * CARGO_POR_DIA_EXTRA


def exportar_reporte_mensual(request, mes, anio):
    """Genera un archivo CSV con los préstamos del mes indicado."""
    prestamos = Prestamo.objects.filter(
        fecha_inicio__month=mes, fecha_inicio__year=anio
    ).select_related("libro")

    buffer = io.StringIO()
    escritor = csv.writer(buffer)
    escritor.writerow(["id", "titulo", "cargo"])
    for prestamo in prestamos:
        escritor.writerow([prestamo.id, prestamo.libro.titulo, calcular_cargo(prestamo)])

    respuesta = HttpResponse(buffer.getvalue(), content_type="text/csv")
    respuesta["Content-Disposition"] = 'attachment; filename="prestamos.csv"'
    return respuesta
