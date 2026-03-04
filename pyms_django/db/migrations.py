"""Custom migration operations for pyms-django-chassis."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from django.db import migrations


class RunSQLFile(migrations.RunSQL):
    """Migration operation that executes SQL loaded from a file.

    Extends ``RunSQL`` so that raw SQL can be kept in dedicated ``.sql``
    files rather than embedded in migration source code.
    """

    def __init__(self, sql_file: str | Path, reverse_sql_file: str | Path | None = None, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize ``RunSQLFile`` from file paths.

        Args:
            sql_file: Path to the ``.sql`` file containing the forward SQL.
            reverse_sql_file: Optional path to the ``.sql`` file for the reverse operation.
            **kwargs: Additional keyword arguments forwarded to ``RunSQL``.
        """
        sql = Path(sql_file).read_text(encoding="utf-8")
        reverse_sql: str | None = None
        if reverse_sql_file:
            reverse_sql = Path(reverse_sql_file).read_text(encoding="utf-8")
        super().__init__(sql=sql, reverse_sql=reverse_sql, **kwargs)
