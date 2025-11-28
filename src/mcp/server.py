# src/mcp/server.py

from __future__ import annotations
import os
import json
from typing import List, Dict, Any

import pandas as pd

from src.classifier.classify import classify_column
from src.parser.parser_core import process_file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")


# ----------------------------- Tools ----------------------------- #

def list_files() -> List[str]:
    """
    List all CSV files available in /data directory.
    """
    files = []
    for f in os.listdir(DATA_DIR):
        if f.lower().endswith(".csv"):
            files.append(f)
    return files


def predict_column(file: str, column: str) -> Dict[str, Any]:
    """
    Predict semantic type of a column.
    """
    path = os.path.join(DATA_DIR, file)
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    df = pd.read_csv(path)
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in {file}")

    result = classify_column(df[column], DATA_DIR)
    return {"label": result.label, "scores": result.scores}


def parse_file(file: str) -> Dict[str, Any]:
    """
    Parse file using process_file() logic.
    """
    path = os.path.join(DATA_DIR, file)
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    output_path = process_file(path, DATA_DIR)
    return {"output_file": output_path}


# ----------------------------- MCP Server Loop ----------------------------- #

def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal MCP protocol handling.
    """
    action = request.get("action")

    if action == "list_files":
        return {"files": list_files()}

    if action == "predict_column":
        return predict_column(request["file"], request["column"])

    if action == "parse_file":
        return parse_file(request["file"])

    return {"error": "Unknown action"}


def main():
    print("MCP server started. Listening for JSON requests...\n")

    for line in iter(input, ""):
        try:
            req = json.loads(line)
            resp = handle_request(req)
        except Exception as e:
            resp = {"error": str(e)}

        print(json.dumps(resp), flush=True)


if __name__ == "__main__":
    main()
