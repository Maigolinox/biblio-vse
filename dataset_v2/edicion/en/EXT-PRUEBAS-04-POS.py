from django.contrib.auth.models import User
from django.test import TestCase

from catalog.models import Book
from reservations.models import Reservation


class ReservationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="reader2")
        self.book = Book.objects.create(title="Rayuela", isbn="9788437604572")

    def test_reserve_book_on_loan(self):
        """
        Test Case: TC-RES-001
        Requirement: BVSE-REQ-002 (advance reservations)
        Steps:
        1. Mark the book as not available.
        2. Send POST to /reservations/ with the book ISBN.
        Expected Result: HTTP 201 and an active reservation for the user.
        """
        self.book.available = False
        self.book.save()
        self.client.force_login(self.user)
        response = self.client.post("/reservations/", {"isbn": self.book.isbn})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Reservation.objects.filter(user=self.user, book=self.book, active=True).exists()
        )
