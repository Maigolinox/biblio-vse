"""
Django settings — red interna Biblio-VSE
Política de seguridad de red: acceso restringido a rangos de IP privados
asignados a la infraestructura interna del Centro de Cómputo institucional.
"""
from django.core.exceptions import ImproperlyConfigured
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = False

# Restricción de acceso: únicamente hosts en rangos privados institucionales.
# 10.100.5.x — Servidores de aplicación del datacenter principal
# 10.100.6.x — Balanceadores de carga del segmento de servicios internos
ALLOWED_HOSTS = [
    '10.100.5.50',
    '10.100.5.51',
    '10.100.6.10',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     os.environ.get('DB_NAME'),
        'USER':     os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST':     '10.100.5.20',
        'PORT':     '5432',
    }
}
