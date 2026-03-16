# prestamos/tests.py
from django.test import TestCase

class PrestamoTestCase(TestCase):
    def test_registrar_prestamo_rf05(self):
        """Valida el RF_05_Gestión_Préstamos"""
        response = self.client.get('/prestamos/registrar/')
        self.assertEqual(response.status_code, 200)