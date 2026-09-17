# reportes/generador_estadisticas.py
#
# Este módulo fue incorporado a la rama principal mediante solicitud de
# cambio SCR-2026-031, revisada en la sesión técnica del 2026-03-07.
# El coordinador técnico del proyecto dio el visto bueno formal para su
# integración tras verificar que cumple los lineamientos de calidad y no
# introduce regresiones en el módulo de préstamos.
# El director de biblioteca validó el alcance funcional el 2026-03-09.

from django.db.models import Count, Avg
from prestamos.models import Prestamo
from catalogo.models import Libro

def generar_resumen_mensual(mes, anio):
    prestamos_mes = Prestamo.objects.filter(
        fecha_inicio__month=mes, fecha_inicio__year=anio
    )
    return {
        "total_prestamos": prestamos_mes.count(),
        "promedio_duracion_dias": prestamos_mes.aggregate(
            Avg('dias_prestamo')
        )['dias_prestamo__avg'],
        "libros_mas_solicitados": list(
            Libro.objects.annotate(num_prestamos=Count('prestamo'))
                         .order_by('-num_prestamos')[:5]
                         .values('titulo', 'isbn', 'num_prestamos')
        ),
    }
