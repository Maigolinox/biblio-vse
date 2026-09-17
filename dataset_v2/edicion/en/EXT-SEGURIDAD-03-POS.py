"""Reading database credentials from mounted secret files."""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def read_secret(variable):
    """Reads the secret from the file pointed to by the environment variable."""
    path = os.environ.get(variable)
    if not path:
        raise ImproperlyConfigured(f"Missing variable {variable}.")
    return Path(path).read_text(encoding="utf-8").strip()


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "biblio"),
        "USER": read_secret("DB_USER_FILE"),
        "PASSWORD": read_secret("DB_PASSWORD_FILE"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}
