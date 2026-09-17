"""Network settings for the Biblio-VSE production deployment."""
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

ALLOWED_HOSTS = [
    "prestamos.biblioteca.local",
    "api.biblioteca.local",
]

CSRF_TRUSTED_ORIGINS = [
    "https://prestamos.biblioteca.local",
    "https://api.biblioteca.local",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = False
