# reports/statistics_generator.py
#
# This module was merged into the main branch through change
# request SCR-2026-031, reviewed in the technical session of 2026-03-07.
# The technical project coordinator gave the formal go-ahead for its
# integration after verifying that it meets the quality guidelines and does not
# introduce regressions in the loans module.
# The library director validated the functional scope on 2026-03-09.

from django.db.models import Count, Avg
from loans.models import Loan
from catalog.models import Book

def generate_monthly_summary(month, year):
    month_loans = Loan.objects.filter(
        start_date__month=month, start_date__year=year
    )
    return {
        "total_loans": month_loans.count(),
        "average_duration_days": month_loans.aggregate(
            Avg('loan_days')
        )['loan_days__avg'],
        "most_requested_books": list(
            Book.objects.annotate(num_loans=Count('loan'))
                        .order_by('-num_loans')[:5]
                        .values('title', 'isbn', 'num_loans')
        ),
    }
