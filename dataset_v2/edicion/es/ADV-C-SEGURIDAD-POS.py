"""
Django settings for production — Biblio-VSE
Gestión de secretos: python-decouple (variables de entorno o archivo .env).
Ningún valor sensible está embebido en el código fuente.
"""
import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='biblioteca.local')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     config('DB_NAME'),
        'USER':     config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':     config('DB_HOST', default='localhost'),
        'PORT':     config('DB_PORT', default='5432'),
    }
}

EMAIL_HOST          = config('EMAIL_HOST')
EMAIL_HOST_USER     = config('EMAIL_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_PASSWORD')
NOTIFICACIONES_KEY  = config('NOTIFICACIONES_API_KEY')
