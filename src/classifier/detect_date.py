# src/classifier/detect_date.py

from __future__ import annotations
from typing import Sequence
from datetime import datetime

# Common date formats – can extend based on Dates.csv if needed
DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d-%b-%Y",
    "%d %b %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%B %d, %Y",
]


def _is_date_like(value: str) -> bool:
    v = value.strip()
    if not v:
        return False

    # Filter out very long text fields
    if len(v) > 40:
        return False

    for fmt in DATE_FORMATS:
        try:
            _ = datetime.strptime(v, fmt)
            return True
        except ValueError:
            continue

    return False


def score_date(values: Sequence[str]) -> float:
    total = 0
    hits = 0

    for v in values:
        v = str(v).strip()
        if not v:
            continue
        total += 1
        if _is_date_like(v):
            hits += 1

    if total == 0:
        return 0.0
    return hits / total
