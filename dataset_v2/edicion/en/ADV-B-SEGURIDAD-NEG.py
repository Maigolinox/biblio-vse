"""
Django settings for staging environment — Biblio-VSE
"""
from django.core.exceptions import ImproperlyConfigured
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-dev-key')
DEBUG = False
ALLOWED_HOSTS = ['staging.biblioteca.local']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     os.environ.get('DB_NAME', 'biblio_staging'),
        'USER':     os.environ.get('DB_USER', 'biblio_app'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST':     os.environ.get('DB_HOST', 'localhost'),
        'PORT':     os.environ.get('DB_PORT', '5432'),
    }
}

# INTEGRATION WITH EXTERNAL NOTIFICATION SERVICE
# TODO: move to an environment variable before going to production
NOTIFICATIONS_API_KEY = "nvapi-Xk7dP2mQr9sL4wYh3jNvZc8eA1bFgT6uE0iO5"

EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtp.biblioteca.local')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER     = os.environ.get('EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
