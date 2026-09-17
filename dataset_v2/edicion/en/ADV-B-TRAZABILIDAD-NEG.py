# loans/views_legacy.py
# WARNING: This function was refactored in sprint 6.
# The original implementation of RF_05_Loan_Management was migrated
# to loans/views.py. This module NO LONGER implements RF_05 or
# any other active requirement. Kept only for historical reference.
from django.shortcuts import get_object_or_404
from loans.models import Loan
from django.http import JsonResponse

def register_loan_legacy(request):
    # Disabled function — do not use in production
    return JsonResponse({"error": "Module out of service"}, status=410)

def query_history_legacy(request, user_id):
    # See US_03 in loans/views.py for the current implementation
    return JsonResponse({"error": "Module out of service"}, status=410)
