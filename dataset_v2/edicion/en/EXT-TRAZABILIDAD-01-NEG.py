from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from loans.models import Loan


def register_return(request, loan_id):
    """Marks the loan as returned and releases the book."""
    loan = get_object_or_404(Loan, pk=loan_id)
    loan.returned = True
    loan.actual_return_date = timezone.now().date()
    loan.save(update_fields=["returned", "actual_return_date"])

    book = loan.book
    book.available = True
    book.save(update_fields=["available"])

    days_late = (loan.actual_return_date - loan.expected_return_date).days
    return JsonResponse({"returned": True, "days_late": max(0, days_late)})
