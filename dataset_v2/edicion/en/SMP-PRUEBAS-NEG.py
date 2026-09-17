from django.contrib.auth.models import User
from catalog.models import Book
from django.test import TestCase

class Tests(TestCase):
    def test_all_good(self):
        # checking that it does not blow up
        assert 1 == 1
