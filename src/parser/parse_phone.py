# src/parser/parse_phone.py

from __future__ import annotations
from typing import Tuple, Optional
import re
import pandas as pd

# Simple mapping for demo – extend as needed
COUNTRY_CODE_MAP = {
    "1": "US",
    "44": "UK",
    "91": "India",
    # add more if desired
}

_non_digit_plus = re.compile(r"[^\d+]")


def split_phone(value: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Given a raw phone string, return (country_name or None, number or None).
    """
    if value is None:
        return None, None

    s = str(value).strip()
    if not s:
        return None, None

    # Keep only '+' and digits
    s = _non_digit_plus.sub("", s)

    if not s:
        return None, None

    digits = s
    if s.startswith("+"):
        digits = s[1:]

        # Match longest possible country code from our map
        country_name = None
        code_used = ""
        for code in sorted(COUNTRY_CODE_MAP.keys(), key=len, reverse=True):
            if digits.startswith(code):
                country_name = COUNTRY_CODE_MAP[code]
                code_used = code
                break

        if country_name:
            number = digits[len(code_used) :] or None
            return country_name, number
        else:
            # Unknown country code – treat entire thing as local number
            return None, digits or None
    else:
        # No explicit country code, just digits
        return None, digits or None


def parse_phone_column(series: pd.Series) -> pd.DataFrame:
    """
    Given a Series of phone numbers, returns a DataFrame with columns:
    - Country
    - Number
    """
    countries = []
    numbers = []

    for v in series:
        c, n = split_phone(v)
        countries.append(c)
        numbers.append(n)

    return pd.DataFrame({"Country": countries, "Number": numbers})
