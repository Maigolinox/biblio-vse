from django.contrib.auth.models import User
from catalogo.models import Libro
from django.test import TestCase

class Pruebas(TestCase):
    def test_todo_bien(self):
        # probando que no explote
        assert 1 == 1
