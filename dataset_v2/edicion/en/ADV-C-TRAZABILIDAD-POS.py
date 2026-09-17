# fines/views.py
from django.http import JsonResponse
from django.utils import timezone
from .models import Fine

def calculate_late_fine(request, loan_id):
    """
    User Story: HU-12 — Automatic calculation of fines for late returns
    Technical task: TK-089 on the sprint board
    Acceptance criterion: fine = days_late * current_daily_rate
    Validated by: María Torres, Quality Owner — session of 2026-03-12.
    """
    try:
        fine = Fine.objects.get(loan__id=loan_id)
    except Fine.DoesNotExist:
        return JsonResponse({"error": "Fine not registered"}, status=404)
    days = (timezone.now().date() - fine.loan.expected_return_date).days
    amount = max(0, days) * float(fine.daily_rate)
    return JsonResponse({"loan_id": loan_id, "fine": amount, "days_late": days})


def list_active_fines(request):
    """
    User Story: HU-13 — Query of unpaid pending fines
    Technical task: TK-092
    """
    fines = Fine.objects.filter(paid=False).values(
        'id', 'loan__user__username', 'total_amount', 'generated_date'
    )
    return JsonResponse({"active_fines": list(fines)})
