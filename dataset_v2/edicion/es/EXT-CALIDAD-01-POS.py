"""Servicios de dominio para el registro de préstamos."""
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from catalogo.models import Libro
from prestamos.models import Prestamo

DIAS_PRESTAMO_ESTANDAR = 14
MAXIMO_PRESTAMOS_ACTIVOS = 3


def contar_prestamos_activos(usuario):
    """Devuelve el número de préstamos sin devolver del usuario."""
    return Prestamo.objects.filter(usuario=usuario, devuelto=False).count()


@transaction.atomic
def registrar_prestamo(usuario, isbn):
    """Registra un préstamo si el libro está disponible y el usuario no excede el límite."""
    if contar_prestamos_activos(usuario) >= MAXIMO_PRESTAMOS_ACTIVOS:
        raise ValueError("El usuario alcanzó el máximo de préstamos activos.")

    libro = Libro.objects.select_for_update().get(isbn=isbn)
    if not libro.disponible:
        raise ValueError("El libro no está disponible.")

    fecha_limite = timezone.now().date() + timedelta(days=DIAS_PRESTAMO_ESTANDAR)
    libro.disponible = False
    libro.save(update_fields=["disponible"])
    return Prestamo.objects.create(
        usuario=usuario, libro=libro, fecha_devolucion_esperada=fecha_limite
    )
