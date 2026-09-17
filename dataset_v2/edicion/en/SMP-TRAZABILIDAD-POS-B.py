# loans/views.py
from django.shortcuts import get_object_or_404
from loans.models import Loan
from django.http import JsonResponse

def register_loan(request):
    """
    Requirement ID: RF_05_Loan_Management
    Description: Registers a new book loan in the system.
    Associated Test Case: TEST_LOAN_01
    """
    # Simulated logic
    return JsonResponse({"status": "success", "message": "Loan registered"})
