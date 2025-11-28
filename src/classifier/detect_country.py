# src/classifier/detect_country.py

from __future__ import annotations
from typing import Sequence, Set
import os
from functools import lru_cache
import re

_word_re = re.compile(r"\w+")


@lru_cache(maxsize=1)
def load_countries(data_dir: str) -> Set[str]:
    """
    Load Countries.txt as a set of normalized (lowercase, stripped) country names.
    """
    path = os.path.join(data_dir, "Countries.txt")
    countries: Set[str] = set()
    if not os.path.exists(path):
        return countries

    with open(path, encoding="utf-8") as f:
        for line in f:
            name = line.strip().lower()
            if name:
                countries.add(name)
    return countries


def _normalize_text(s: str) -> str:
    words = _word_re.findall(s.lower())
    return " ".join(words)


def score_country(values: Sequence[str], countries: Set[str]) -> float:
    if not countries:
        return 0.0

    total = 0
    hits = 0

    for v in values:
        v = str(v).strip()
        if not v:
            continue
        total += 1
        norm = _normalize_text(v)

        # Exact match is the strongest signal
        if norm in countries:
            hits += 1
        else:
            # Also allow cases where the cell contains "City, Country"
            for c in countries:
                if norm.endswith(" " + c) or norm.startswith(c + " ") or (" " + c + " ") in norm:
                    hits += 1
                    break

    if total == 0:
        return 0.0

    return hits / total
