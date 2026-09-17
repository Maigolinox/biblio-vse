# loans/tests.py
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

class LoanTestCase(TestCase):
    def test_register_loan_rf05(self):
        """Validates RF_05_Loan_Management"""
        response = self.client.get('/loans/register/')
        self.assertEqual(response.status_code, 200)
