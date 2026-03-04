"""Shared Django app list for pyms-django-chassis projects."""

from __future__ import annotations

from typing import Final

SHARED_APPS: Final[list[str]] = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "django_filters",
    "pyms_django.base",
]
