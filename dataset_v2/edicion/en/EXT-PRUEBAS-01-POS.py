from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from catalog.models import Book
from loans.models import Loan


class ReturnTests(TestCase):
    def test_late_return(self):
        """
        Test Case: TC-DEV-002
        Requirement: RF_07 (register return)
        Steps:
        1. Create a loan that expired three days ago.
        2. Send POST to /returns/<id>/.
        Expected Result: HTTP 200, loan returned and days_late = 3.
        """
        user = User.objects.create(username="reader")
        book = Book.objects.create(title="Pedro Páramo", isbn="9786071600000")
        loan = Loan.objects.create(
            user=user, book=book,
            expected_return_date=date.today() - timedelta(days=3),
        )
        response = self.client.post(f"/returns/{loan.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["days_late"], 3)
        loan.refresh_from_db()
        self.assertTrue(loan.returned)
