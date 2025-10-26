# viewdf

A lightweight CLI utility to quickly inspect tabular data files (CSV/TSV) or pickled pandas DataFrames using pandas.

## Features

- View CSV/TSV file contents with automatic separator detection
- Load and inspect pickled pandas DataFrames
- Show basic stats with `--describe` (whole file or single column)
- Preview data with `--head`/`--tail`/`--sample`
- Advanced row selection using Python slice notation
- Convert between formats (CSV ↔ pickle)
- Memory-efficient handling of large files
- Automatic file format detection (.csv, .tsv, .pkl)
- Customizable output formatting

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

# View specific rows using Python slice notation
python viewdf.py data.csv --slice 5        # 6th row (0-based)
python viewdf.py data.csv --slice 1:4      # rows 1-3
python viewdf.py data.csv --slice ::2      # every second row
python viewdf.py data.csv --slice=-5:      # last 5 rows (note '=')
python viewdf.py data.csv --slice 1:10:2   # every second row from 1-9

# Control output format
python viewdf.py data.csv --max_rows 50    # limit output to 50 rows
```

Working with different formats:
```bash
# Tab-separated files (auto-detected from .tsv extension)
python viewdf.py data.tsv

# Explicitly specify separator
python viewdf.py data.txt --sep $'\t'
python viewdf.py data.dat --sep ","

# Load pickled DataFrame
python viewdf.py data.pkl --describe
python viewdf.py data.pkl --head 10

# Convert between formats
python viewdf.py data.csv --to-pickle data.pkl    # CSV to pickle
python viewdf.py data.tsv --to-pickle data.pkl    # TSV to pickle
```

## Development

Run tests:
```bash
# Quick test run
python -m pytest -q

# Verbose output
python -m pytest -v

# Run specific test
python -m pytest tests/test_viewdf.py::test_describe_column -v
```

Test output preservation:
- Failed tests automatically preserve temp files under `debug_temps/{testname}-{timestamp}/`
- Useful for debugging data handling issues
- Large file tests use deterministic data (10k rows × 50 cols)
- Use `capsys` fixture to verify output in tests

### Contributing

When submitting changes:
1. Add test coverage for new features
2. Update docstrings and README.md
3. Verify large file handling if relevant
4. Run the full test suite

## Exit codes

- 0: Success
- 2: File read error (missing file, corrupt pickle, etc.)
- 3: Invalid column name
- 4: Pickle write error
- 5: Invalid slice notation

## License

MIT