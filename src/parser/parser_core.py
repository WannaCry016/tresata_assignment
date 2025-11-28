# src/parser/parser_core.py

from __future__ import annotations

from typing import Optional, Tuple, Dict
import os
import pandas as pd

from src.classifier.classify import classify_column
from .parse_phone import parse_phone_column
from .parse_company import parse_company_column


def _find_best_columns(df: pd.DataFrame, data_dir: str) -> Tuple[Optional[str], Optional[str], Dict[str, Dict]]:
    """
    Return (phone_col_name or None, company_col_name or None, debug_info)
    debug_info: column_name -> classification.scores
    """
    best_phone: Tuple[Optional[str], float] = (None, 0.0)
    best_company: Tuple[Optional[str], float] = (None, 0.0)
    debug_scores: Dict[str, Dict] = {}

    for col in df.columns:
        classification = classify_column(df[col], data_dir)
        debug_scores[col] = classification.scores

        phone_score = classification.scores.get("PhoneNumber", 0.0)
        company_score = classification.scores.get("CompanyName", 0.0)

        if phone_score > best_phone[1]:
            best_phone = (col, phone_score)

        if company_score > best_company[1]:
            best_company = (col, company_score)

    phone_col = best_phone[0] if best_phone[1] > 0.0 else None
    company_col = best_company[0] if best_company[1] > 0.0 else None

    return phone_col, company_col, debug_scores


def process_file(
    input_path: str,
    data_dir: str,
    output_path: Optional[str] = None,
) -> str:
    """
    Implements Part B:
    - Load CSV
    - Detect best PhoneNumber and CompanyName columns
    - Parse them
    - Write output.csv

    Returns the path of the written output file.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    df = pd.read_csv(input_path)

    phone_col, company_col, _scores = _find_best_columns(df, data_dir)

    # We don't drop the original columns; we add parsed ones.
    out_df = df.copy()

    if phone_col is not None:
        phone_parsed = parse_phone_column(out_df[phone_col])
        # Column names are fixed as per spec: Country, Number
        out_df["Country"] = phone_parsed["Country"]
        out_df["Number"] = phone_parsed["Number"]

    if company_col is not None:
        company_parsed = parse_company_column(out_df[company_col], data_dir)
        # Column names are fixed as per spec: Name, Legal
        out_df["Name"] = company_parsed["Name"]
        out_df["Legal"] = company_parsed["Legal"]

    if output_path is None:
        base_dir = os.path.dirname(os.path.abspath(input_path))
        output_path = os.path.join(base_dir, "output.csv")

    out_df.to_csv(output_path, index=False)
    return output_path
