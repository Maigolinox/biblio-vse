# catalogo/filtros_avanzados.py
# ESTADO: PENDIENTE DE APROBACIÓN — en revisión para BVSE-REQ-015
# Implementación solicitada verbalmente el 2026-03-18.
# Aún no tiene número de requerimiento formal asignado.
# NO desplegar hasta recibir la aprobación formal del coordinador técnico.

from django.shortcuts import render
from catalogo.models import Libro
from django.db.models import Q

def filtrar_libros_por_disponibilidad(queryset, solo_disponibles=True):
    if solo_disponibles:
        return queryset.filter(disponible=True, prestado=False)
    return queryset

def filtrar_libros_por_categoria(queryset, categoria_id):
    return queryset.filter(categoria__id=categoria_id)
