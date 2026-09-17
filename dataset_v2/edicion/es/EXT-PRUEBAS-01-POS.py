from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from catalogo.models import Libro
from prestamos.models import Prestamo


class DevolucionTests(TestCase):
    def test_devolucion_con_retraso(self):
        """
        Caso de Prueba: TC-DEV-002
        Requerimiento: RF_07 (registrar devolución)
        Pasos:
        1. Crear un préstamo vencido hace tres días.
        2. Enviar POST a /devoluciones/<id>/.
        Resultado Esperado: HTTP 200, préstamo devuelto y dias_retraso = 3.
        """
        usuario = User.objects.create(username="lector")
        libro = Libro.objects.create(titulo="Pedro Páramo", isbn="9786071600000")
        prestamo = Prestamo.objects.create(
            usuario=usuario, libro=libro,
            fecha_devolucion_esperada=date.today() - timedelta(days=3),
        )
        respuesta = self.client.post(f"/devoluciones/{prestamo.id}/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["dias_retraso"], 3)
        prestamo.refresh_from_db()
        self.assertTrue(prestamo.devuelto)
