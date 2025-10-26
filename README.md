# viewdf

A lightweight CLI utility to quickly inspect tabular data files (CSV/TSV) or pickled pandas DataFrames.

## Features

- View CSV/TSV file contents with automatic separator detection
- Load and inspect pickled pandas DataFrames
- Show basic stats with `--describe` (whole file or single column)
- Preview data with `--head`/`--tail`/`--sample`
- Convert between formats (CSV ↔ pickle)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/username/viewdf.git
cd viewdf
```

2. Create and activate a Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install pandas pytest
```

## Usage

Basic file inspection:
```bash
# Show first 5 rows (default)
python viewdf.py data.csv

# Basic statistics for all columns
python viewdf.py data.csv --describe

# Stats for a specific column
python viewdf.py data.csv --describe age

# Show dimensions and column names
python viewdf.py data.csv --shape
python viewdf.py data.csv --columns
```

Data preview options:
```bash
# First/last N rows
python viewdf.py data.csv --head 10
python viewdf.py data.csv --tail 5

# Random sample
python viewdf.py data.csv --sample 100
```

Working with different formats:
```bash
# Tab-separated files
python viewdf.py data.tsv --sep $'\t'

# Load pickled DataFrame
python viewdf.py data.pkl --describe

# Convert CSV to pickle
python viewdf.py data.csv --to-pickle data.pkl
```

## Development

Run tests:
```bash
# Quick test run
python -m pytest -q

# Verbose output
python -m pytest -v
```

Test output preservation:
- Failed tests automatically preserve temp files under `debug_temps/{testname}-{timestamp}/`
- Useful for debugging data handling issues

## Exit codes

- 0: Success
- 2: File read error (missing file, corrupt pickle, etc.)
- 3: Invalid column name
- 4: Pickle write error

## License

MIT