"""WSGI application entry point for pyms-django-chassis."""

from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyms_django.settings.main")

application = get_wsgi_application()
