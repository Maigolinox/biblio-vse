from unittest import skip

from django.test import TestCase


class DevolucionTests(TestCase):
    @skip("arreglar después")
    def test_devolucion(self):
        pass

    @skip("falla en la computadora de Luis")
    def test_devolucion_tarde(self):
        pass
