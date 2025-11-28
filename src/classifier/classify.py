# src/classifier/classify.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence

import os
import pandas as pd

from .detect_phone import score_phone
from .detect_date import score_date
from .detect_country import load_countries, score_country
from .detect_company import load_legal_suffixes, score_company


SEMANTIC_TYPES = ["PhoneNumber", "CompanyName", "Country", "Date", "Other"]


@dataclass
class ColumnClassification:
    label: str
    scores: Dict[str, float]


def _get_sample(values: pd.Series, max_rows: int = 500) -> Sequence[str]:
    non_null = values.dropna()
    if len(non_null) > max_rows:
        non_null = non_null.sample(max_rows, random_state=42)
    return [str(v) for v in non_null.tolist()]


def classify_column(
    series: pd.Series,
    data_dir: str,
) -> ColumnClassification:
    """
    Classify a single column into one of the semantic types.

    data_dir should contain:
    - Countries.txt
    - legal.txt
    """
    sample = _get_sample(series)

    # Load reference data
    countries = load_countries(data_dir)
    legal_suffixes = load_legal_suffixes(data_dir)

    phone_s = score_phone(sample)
    date_s = score_date(sample)
    country_s = score_country(sample, countries)
    company_s = score_company(sample, legal_suffixes)

    scores: Dict[str, float] = {
        "PhoneNumber": float(phone_s),
        "CompanyName": float(company_s),
        "Country": float(country_s),
        "Date": float(date_s),
        # 'Other' is derived, not scored directly
    }

    # Choose best class
    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]

    # If nothing stands out, call it 'Other'
    THRESHOLD = 0.3
    if best_score < THRESHOLD:
        label = "Other"
    else:
        label = best_label

    scores["Other"] = 1.0 if label == "Other" else 0.0

    return ColumnClassification(label=label, scores=scores)
