"""Domain services for registering loans."""
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from catalog.models import Book
from loans.models import Loan

STANDARD_LOAN_DAYS = 14
MAX_ACTIVE_LOANS = 3


def count_active_loans(user):
    """Returns the number of loans the user has not returned yet."""
    return Loan.objects.filter(user=user, returned=False).count()


@transaction.atomic
def register_loan(user, isbn):
    """Registers a loan if the book is available and the user is within the limit."""
    if count_active_loans(user) >= MAX_ACTIVE_LOANS:
        raise ValueError("The user reached the maximum number of active loans.")

    book = Book.objects.select_for_update().get(isbn=isbn)
    if not book.available:
        raise ValueError("The book is not available.")

    due_date = timezone.now().date() + timedelta(days=STANDARD_LOAN_DAYS)
    book.available = False
    book.save(update_fields=["available"])
    return Loan.objects.create(user=user, book=book, expected_return_date=due_date)
