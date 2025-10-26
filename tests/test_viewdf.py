import sys
from pathlib import Path
import csv
import random

import pytest

# Ensure we can import viewdf from workspace
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from viewdf import main


def write_csv(path, text: str):
    path.write_text(text)
    return str(path)


def test_describe_whole(tmp_path, capsys):
    p = tmp_path / "data.csv"
    write_csv(p, "a,b\n1,foo\n2,bar\n3,baz\n")
    rc = main([str(p), "--describe"])  # describe entire DataFrame
    out_err = capsys.readouterr()
    assert rc == 0
    assert "count" in out_err.out


def test_describe_column(tmp_path, capsys):
    p = tmp_path / "data.csv"
    write_csv(p, "a,b\n1,10\n2,20\n3,30\n")
    rc = main([str(p), "--describe", "a"])  # describe only column 'a'
    out_err = capsys.readouterr()
    assert rc == 0
    assert "count" in out_err.out


def test_describe_missing_column(tmp_path, capsys):
    p = tmp_path / "data.csv"
    write_csv(p, "a,b\n1,10\n2,20\n")
    rc = main([str(p), "--describe", "c"])  # column 'c' does not exist
    out_err = capsys.readouterr()
    assert rc == 3
    assert "not found" in out_err.err


def test_describe_large_file(tmp_path, capsys):
    # Create a CSV with 10_000 rows and 50 columns
    rows = 10_000
    cols = 50
    header = [f"col{i}" for i in range(cols)]
    p = tmp_path / "big.csv"
    with p.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        # write rows with small ints to keep file size reasonable
        for r in range(rows):
            row = [(r % 100) for _ in range(cols)]
            writer.writerow(row)

    # Describe entire DataFrame
    rc = main([str(p), "--describe"])
    out_err = capsys.readouterr()
    assert rc == 0
    assert "count" in out_err.out

    # Describe 10 randomly chosen columns (deterministic selection)
    random.seed(42)
    chosen = random.sample(range(cols), 10)
    for idx in chosen:
        col = f"col{idx}"
        rc = main([str(p), "--describe", col])
        out_err = capsys.readouterr()
        assert rc == 0
        assert "count" in out_err.out
