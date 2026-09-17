"""
Django settings — Biblio-VSE internal network
Network security policy: access restricted to private IP ranges
assigned to the internal infrastructure of the institutional Computing Center.
"""
from django.core.exceptions import ImproperlyConfigured
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = False

# Access restriction: only hosts in private institutional ranges.
# 10.100.5.x — Application servers of the main datacenter
# 10.100.6.x — Load balancers of the internal services segment
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
