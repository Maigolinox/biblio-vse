# Haciendo pruebas para una nueva interfaz que me pidieron ayer en el pasillo
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View
def renderizar_nuevo_dashboard():
    return "Dashboard V2"
