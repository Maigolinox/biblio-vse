"""Export of the monthly loans report in CSV format."""
import csv
import io

from django.http import HttpResponse

from loans.models import Loan

FREE_DAYS = 21
CHARGE_PER_EXTRA_DAY = 2.5


def calculate_charge(loan):
    """Calculates the charge for the days that exceed the free period."""
    extra_days = max(0, loan.loan_days - FREE_DAYS)
    return extra_days * CHARGE_PER_EXTRA_DAY


def export_monthly_report(request, month, year):
    """Generates a CSV file with the loans of the given month."""
    loans = Loan.objects.filter(
        start_date__month=month, start_date__year=year
    ).select_related("book")

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "title", "charge"])
    for loan in loans:
        writer.writerow([loan.id, loan.book.title, calculate_charge(loan)])

    response = HttpResponse(buffer.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="loans.csv"'
    return response
