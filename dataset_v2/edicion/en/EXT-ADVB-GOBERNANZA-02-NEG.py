# loans/renewals.py
# Approved by: ____________________ (signature pending)
# Authorized by: _______________________
# Digital Signature: not generated
from django.http import JsonResponse
from django.utils import timezone
from loans.models import Loan


def renew_loan(request, loan_id):
    loan = Loan.objects.get(pk=loan_id)
    loan.expected_return_date += timezone.timedelta(days=7)
    loan.save()
    return JsonResponse({"renewed": True})
