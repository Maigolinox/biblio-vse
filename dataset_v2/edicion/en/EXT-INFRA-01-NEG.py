"""Network settings for the Biblio-VSE production deployment."""
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://*",
    "https://*",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
