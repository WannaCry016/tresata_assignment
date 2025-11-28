# src/classifier/detect_phone.py

from __future__ import annotations
from typing import Sequence
import re


PHONE_DIGIT_MIN = 7
PHONE_DIGIT_MAX = 15

_phone_clean_re = re.compile(r"[^\d+]")


def _is_phone_like(value: str) -> bool:
    if not value:
        return False

    s = value.strip()
    if not s:
        return False

    # Remove spaces, hyphens, parentheses etc., keep + and digits
    s = _phone_clean_re.sub("", s)

    # Allow leading +
    if s.startswith("+"):
        s = s[1:]

    # Must now be all digits
    if not s.isdigit():
        return False

    return PHONE_DIGIT_MIN <= len(s) <= PHONE_DIGIT_MAX


def score_phone(values: Sequence[str]) -> float:
    """
    Return a score in [0, 1] representing how likely this column is a phone number.
    """
    total = 0
    hits = 0

    for v in values:
        v = str(v).strip()
        if not v:
            continue
        total += 1
        if _is_phone_like(v):
            hits += 1

    if total == 0:
        return 0.0

    return hits / total
