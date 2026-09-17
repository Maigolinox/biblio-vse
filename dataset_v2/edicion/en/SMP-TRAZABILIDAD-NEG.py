from django.shortcuts import render
from django.http import JsonResponse
import random

def calculate_advanced_delinquency(request, user_id):
    if user_id <= 0:
        return JsonResponse({"error": "Invalid user ID"}, status=400)

    base_debt = 150.50
    penalty = random.choice([1.2, 1.5, 2.0])
    total = base_debt * penalty

    if total > 300:
        alert_level = "critical"
        block = True
    elif total > 200:
        alert_level = "high"
        block = True
    elif total > 100:
        alert_level = "medium"
        block = False
    else:
        alert_level = "low"
        block = False

    return JsonResponse({
        "block_user": block,
        "debt": total,
        "alert_level": alert_level
    })
