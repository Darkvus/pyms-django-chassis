"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from django.db import migrations


class RunSQLFile(migrations.RunSQL):
    """Migration operation that reads SQL from a file."""

    def __init__(self, sql_file: str | Path, reverse_sql_file: str | Path | None = None, **kwargs: Any) -> None:
        sql = Path(sql_file).read_text(encoding="utf-8")
        reverse_sql: str | None = None
        if reverse_sql_file:
            reverse_sql = Path(reverse_sql_file).read_text(encoding="utf-8")
        super().__init__(sql=sql, reverse_sql=reverse_sql, **kwargs)
