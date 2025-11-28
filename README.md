# Semantic Column Classifier & Parser

This repository provides a complete pipeline for **semantic column classification**, **phone/company parsing**, and a lightweight **MCP server layer** that exposes these operations to external tools or LLM clients.  
The solution is implemented in Python and is modular, reliable, and easy to extend.

---

## Features

### **Part A – Semantic Classification**
- Classifies any column into:
  - `PhoneNumber`
  - `CompanyName`
  - `Country`
  - `Date`
  - `Other`
- Uses only **column values**, not headers.
- Hybrid approach: rule-based heuristics + scoring.
- Automatically selects the strongest semantic type.

### **Part B – Parsing & Normalization**
- If a column is classified as **PhoneNumber**, it is parsed into:
  - `Country`
  - `Number`
- If classified as **CompanyName**, it is parsed into:
  - `Name`
  - `Legal`
- If both phone and company columns exist, both are parsed and included in the final output.
- Final output CSV includes:
  ```
  PhoneNumber, Country, Number, CompanyName, Name, Legal
  ```

### **Part C – MCP Layer**
- Exposes functionality over the Model Context Protocol:
  - `list_files` – list available data files
  - `predict_column(file, column)` – classify a specific column
  - `parse_file(file)` – run full classification + parsing pipeline
- Works over **stdio**, compatible with LLM MCP hosts.

---

## Repository Structure

```
semantic-classifier/
├── data/
│   ├── Company.csv
│   ├── Countries.txt
│   ├── Dates.csv
│   ├── PhoneNumber.csv
│   ├── legal.txt
│
├── src/
│   ├── classifier/
│   │   ├── __init__.py
│   │   ├── detect_phone.py
│   │   ├── detect_date.py
│   │   ├── detect_country.py
│   │   ├── detect_company.py
│   │   └── classify.py
│   │
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── parse_phone.py
│   │   ├── parse_company.py
│   │   └── parser_core.py
│   │
│   └── mcp/
│       ├── __init__.py
│       └── server.py
│
├── predict.py
├── parser.py
├── requirements.txt
├── README.md
└── .gitignore
```

**Note:** Place `Company.csv`, `Countries.txt`, `Dates.csv`, `PhoneNumber.csv`, and `legal.txt` into the `data/` directory before running.

---

## Installation

```
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

---

## Part A – Semantic Classification (predict.py)

### Usage

```
python predict.py --input data/test.csv --column PhoneNumber
```

### Output

```
PhoneNumber
```

### How It Works

- Samples up to 500 values from the column.
- Computes scores for:
  - PhoneNumber (regex + digit lengths)
  - Date (datetime parsing)
  - Country (match from Countries.txt)
  - CompanyName (presence of legal suffix words)
- Highest score → semantic label.
- If none strong → returns `Other`.

---

## Part B – Parsing & Normalization (parser.py)

### Usage

```
python parser.py --input data/test.csv
python parser.py --input data/test.csv --output results/output.csv
```

### What It Does

- Classifies all columns.
- Identifies best PhoneNumber & CompanyName columns.
- Parses selected columns:
  - Phone → Country, Number
  - Company → Name, Legal
- Writes enhanced output CSV.

### Phone Parsing Rules

- Strip non-digit characters.
- If `+<code>` matches known country code → split.
- Otherwise:
  - `Country = ""`
  - `Number = digits`.

### Company Parsing Rules

- Uses **dynamic multi-word legal suffix reconstruction**.
- `legal.txt` contains fragmented suffix words (e.g., `gmbh`, `co`, `kg`).
- Parser reconstructs valid suffixes such as:
  - `gmbh co kg`
  - `pvt ltd`
  - `ag`
- Splits into:
  - `Name` (prefix)
  - `Legal` (suffix).

---

## Part C – MCP Server

Located at:

```
src/mcp/server.py
```

### Exposed Tools

- `list_files()` – list CSVs in data directory  
- `predict_column(file, column)` – classify a column  
- `parse_file(file)` – full pipeline, returns output file path  

### Run MCP Server

```
python -m src.mcp.server
```

### Manual Testing (stdin JSON)

```
{"action": "list_files"}
{"action": "predict_column", "file": "test.csv", "column": "PhoneNumber"}
{"action": "parse_file", "file": "test.csv"}
```

Returns structured JSON responses.
