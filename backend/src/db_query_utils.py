"""Consultas Pony compatibles con Python 3.13.

En Py 3.13 las lambdas `entity.select(lambda r: r.user_id == uid)` no filtran bien
(comparación entera rota). Usamos filtro Python sobre `list(entity.select())`.
"""

from __future__ import annotations

from datetime import date
from typing import TypeVar

T = TypeVar("T")


def rows_for_user(entity: type[T], user_id: int) -> list[T]:
    uid = int(user_id)
    return [row for row in list(entity.select()) if int(row.user_id) == uid]  # type: ignore[attr-defined]


def filter_date_range(rows: list[T], *, desde: date, hasta: date, attr: str = "fecha") -> list[T]:
    return [r for r in rows if desde <= getattr(r, attr) <= hasta]
