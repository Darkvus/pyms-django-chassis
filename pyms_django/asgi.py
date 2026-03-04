"""ASGI application entry point for pyms-django-chassis."""

from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyms_django.settings.main")

application = get_asgi_application()
