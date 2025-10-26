import sys
from pathlib import Path

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
