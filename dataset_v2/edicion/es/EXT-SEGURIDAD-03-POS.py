"""Lectura de credenciales de base de datos desde archivos de secretos montados."""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def leer_secreto(variable):
    """Lee el secreto desde el archivo indicado por la variable de entorno."""
    ruta = os.environ.get(variable)
    if not ruta:
        raise ImproperlyConfigured(f"Falta la variable {variable}.")
    return Path(ruta).read_text(encoding="utf-8").strip()


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "biblio"),
        "USER": leer_secreto("DB_USER_FILE"),
        "PASSWORD": leer_secreto("DB_PASSWORD_FILE"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}
