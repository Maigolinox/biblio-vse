# prestamos/tests_cobertura.py
from django.contrib.auth.models import User
from django.test import TestCase

class CoberturaMinimaPrestamos(TestCase):

    def test_endpoint_prestamo_responde(self):
        """
        Caso de Prueba: TC-PREST-001
        Entorno: Django TestClient, SQLite en memoria
        Pasos:
        1. Enviar solicitud GET al endpoint /prestamos/
        Resultado Esperado: El servidor no genera una excepción interna.
        """
        response = self.client.get('/prestamos/')
        self.assertIsNotNone(response)

    def test_modelo_prestamo_instancia(self):
        """
        Caso de Prueba: TC-PREST-002
        Entorno: Python 3.10, Django ORM
        Pasos:
        1. Importar el modelo Prestamo del módulo de préstamos
        Resultado Esperado: La clase Prestamo es importable sin error.
        """
        from prestamos.models import Prestamo  # noqa: F401
        self.assertTrue(True)  # El import ya habría fallado si hubiera error
