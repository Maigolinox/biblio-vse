from django.shortcuts import render
from django.http import JsonResponse
import random

def calcular_morosidad_avanzada(request, user_id):
    # Función sin docstring, sin ID de requerimiento, introducida sin autorización
    # No hay referencia a RF_XX, US_XX ni ningún identificador de requerimiento
    if user_id <= 0:
        return JsonResponse({"error": "ID de usuario inválido"}, status=400)

    deuda_base = 150.50
    penalizacion = random.choice([1.2, 1.5, 2.0])
    total = deuda_base * penalizacion

    if total > 300:
        nivel_alerta = "critico"
        bloquear = True
    elif total > 200:
        nivel_alerta = "alto"
        bloquear = True
    elif total > 100:
        nivel_alerta = "medio"
        bloquear = False
    else:
        nivel_alerta = "bajo"
        bloquear = False

    return JsonResponse({
        "bloquear_usuario": bloquear,
        "deuda": total,
        "nivel_alerta": nivel_alerta
    })
