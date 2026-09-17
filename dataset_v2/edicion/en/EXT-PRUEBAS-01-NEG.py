from unittest import skip

from django.test import TestCase


class ReturnTests(TestCase):
    @skip("fix later")
    def test_return(self):
        pass

    @skip("fails on Luis's computer")
    def test_late_return(self):
        pass
