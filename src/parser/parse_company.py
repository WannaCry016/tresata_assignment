# src/parser/parse_company.py

from __future__ import annotations
from typing import Tuple, List
import re
import pandas as pd

from src.classifier.detect_company import load_legal_suffixes


def _normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _extract_dynamic_suffix(norm: str, legal_words: List[str]) -> Tuple[str, str]:
    """
    Dynamically reconstruct multi-word legal suffixes from legal.txt
    which contains *single words*, not full suffixes.
    
    Example:
    norm = 'enno roggemann gmbh co kg'
    legal_words may contain ['gmbh', 'co', 'kg']
    
    We detect that suffix = 'gmbh co kg'
    """

    words = norm.split()
    n = len(words)

    # From end → backwards accumulate only legal words
    suffix_parts = []

    for i in range(n - 1, -1, -1):
        w = words[i]
        if w in legal_words:
            suffix_parts.append(w)
        else:
            break

    if not suffix_parts:
        return norm, ""  # No suffix detected

    # Suffix detected (reverse accumulated list)
    suffix = " ".join(reversed(suffix_parts))

    # Remove suffix words from end to form name
    name = " ".join(words[: n - len(suffix_parts)])

    return name.strip(), suffix.strip()


def parse_company_column(series: pd.Series, data_dir: str) -> pd.DataFrame:
    """
    Parse company names using dynamic multi-word suffix detection.
    Works even if legal.txt is garbage (single words only).
    """
    # Load legal words as lowercase single tokens
    legal_words = [w.lower() for w in load_legal_suffixes(data_dir)]

    names = []
    legals = []

    for v in series:
        if pd.isna(v) or v is None or str(v).strip() == "":
            names.append("")
            legals.append("")
            continue

        norm = _normalize_text(str(v))

        name, suffix = _extract_dynamic_suffix(norm, legal_words)

        names.append(name)
        legals.append(suffix)

    return pd.DataFrame({"Name": names, "Legal": legals}).fillna("")
