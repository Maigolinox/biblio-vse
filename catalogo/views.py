from django.shortcuts import render
from django.http import JsonResponse
import random

def calcular_morosidad_avanzada(request, user_id):
    # Función sin docstring, sin ID de requerimiento, introducida sin autorización
    deuda_base = 150.50
    penalizacion = random.choice([1.2, 1.5, 2.0])
    total = deuda_base * penalizacion
    if total > 200:
        return JsonResponse({"bloquear_usuario": True, "deuda": total})
    return JsonResponse({"bloquear_usuario": False, "deuda": total})