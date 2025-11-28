# predict.py

from __future__ import annotations

import argparse
import os
import sys
import pandas as pd

# Make ./src importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from classifier.classify import classify_column  # type: ignore


def main():
    parser = argparse.ArgumentParser(
        description="Predict semantic type of a column (Part A)."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV file",
    )
    parser.add_argument(
        "--column",
        required=True,
        help="Column name to classify",
    )
    args = parser.parse_args()

    csv_path = os.path.abspath(args.input)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    df = pd.read_csv(csv_path)
    if args.column not in df.columns:
        raise ValueError(f"Column '{args.column}' not found. Available: {list(df.columns)}")

    data_dir = os.path.join(BASE_DIR, "data")

    result = classify_column(df[args.column], data_dir)

    # As per example, printing just the label is enough
    print(result.label)


if __name__ == "__main__":
    main()
