"""Shared middleware stack for pyms-django-chassis projects."""
from __future__ import annotations

from typing import Final

SHARED_MIDDLEWARE: Final[list[str]] = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "pyms_django.middlewares.tracing.TracingMiddleware",
    "pyms_django.middlewares.logging.RequestLoggingMiddleware",
]
