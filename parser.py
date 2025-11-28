# parser.py

from __future__ import annotations

import argparse
import os
import sys

# Make ./src importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from parser.parser_core import process_file  # type: ignore


def main():
    parser = argparse.ArgumentParser(
        description="Parse PhoneNumber / CompanyName columns and write output.csv (Part B)."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV file",
    )
    parser.add_argument(
        "--output",
        required=False,
        help="Optional output path (default: output.csv in same directory)",
    )
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    data_dir = os.path.join(BASE_DIR, "data")

    output_path = process_file(input_path, data_dir, args.output)
    print(output_path)


if __name__ == "__main__":
    main()
