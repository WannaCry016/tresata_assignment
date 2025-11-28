# src/classifier/detect_company.py

from __future__ import annotations
from typing import Sequence, List
import os
from functools import lru_cache
import re

_word_re = re.compile(r"\w+")


@lru_cache(maxsize=1)
def load_legal_suffixes(data_dir: str) -> List[str]:
    """
    Load legal.txt – each line is a legal suffix (e.g., 'pvt ltd', 'gmbh', 'inc', 'llc').
    We store them lowercased.
    """
    path = os.path.join(data_dir, "legal.txt")
    suffixes: List[str] = []
    if not os.path.exists(path):
        return suffixes

    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip().lower()
            if s:
                suffixes.append(s)

    # Sort by length (desc) to match the longest suffix first
    suffixes.sort(key=lambda x: len(x.split()), reverse=True)
    return suffixes


def _normalize_text(s: str) -> str:
    words = _word_re.findall(s.lower())
    return " ".join(words)


def _has_legal_suffix(norm: str, suffixes: Sequence[str]) -> bool:
    for suf in suffixes:
        if norm.endswith(" " + suf) or norm == suf:
            return True
    return False


def score_company(values: Sequence[str], legal_suffixes: Sequence[str]) -> float:
    if not legal_suffixes:
        return 0.0

    total = 0
    hits = 0

    for v in values:
        v = str(v).strip()
        if not v:
            continue
        total += 1
        norm = _normalize_text(v)

        if _has_legal_suffix(norm, legal_suffixes):
            hits += 1
        else:
            # Heuristic: company-like strings are often multi-word and capitalised, not purely numeric
            if any(c.isalpha() for c in v) and " " in v and not v.isupper():
                hits += 0.3  # soft evidence

    if total == 0:
        return 0.0

    return hits / total
