from django.contrib.auth.models import User
from django.test import TestCase

from catalogo.models import Libro
from reservas.models import Reserva


class ReservaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create(username="lectora")
        self.libro = Libro.objects.create(titulo="Rayuela", isbn="9788437604572")

    def test_reserva_libro_prestado(self):
        """
        Caso de Prueba: TC-RES-001
        Requerimiento: BVSE-REQ-002 (reservas anticipadas)
        Pasos:
        1. Marcar el libro como no disponible.
        2. Enviar POST a /reservas/ con el ISBN del libro.
        Resultado Esperado: HTTP 201 y una reserva activa para el usuario.
        """
        self.libro.disponible = False
        self.libro.save()
        self.client.force_login(self.usuario)
        respuesta = self.client.post("/reservas/", {"isbn": self.libro.isbn})
        self.assertEqual(respuesta.status_code, 201)
        self.assertTrue(
            Reserva.objects.filter(usuario=self.usuario, libro=self.libro, activa=True).exists()
        )
