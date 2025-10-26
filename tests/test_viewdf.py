import sys
from pathlib import Path
import csv
import random

import pandas as pd
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


def test_describe_pickle(tmp_path, capsys):
    """Test loading and describing a pickled DataFrame."""
    # Create a small DataFrame and pickle it
    df = pd.DataFrame({
        'numbers': [1, 2, 3, 4, 5],
        'letters': ['a', 'b', 'c', 'd', 'e']
    })
    p = tmp_path / "data.pkl"
    df.to_pickle(str(p))

    # Test describe on whole DataFrame
    rc = main([str(p), "--describe"])
    out_err = capsys.readouterr()
    assert rc == 0
    assert "count" in out_err.out

    # Test describe on single column
    rc = main([str(p), "--describe", "numbers"])
    out_err = capsys.readouterr()
    assert rc == 0
    assert "count" in out_err.out
    assert "mean" in out_err.out  # numeric column should have mean


def test_pickle_errors(tmp_path, capsys):
    """Test error handling for corrupt/invalid pickle files."""
    # Create an invalid pickle file (just some text)
    p = tmp_path / "invalid.pkl"
    p.write_text("not a pickle file")
    rc = main([str(p), "--describe"])
    out_err = capsys.readouterr()
    assert rc == 2  # should fail with our error code
    assert "Failed to read" in out_err.err

    # Create a pickle file containing something other than a DataFrame
    p = tmp_path / "wrong_type.pkl"
    import pickle
    with p.open("wb") as f:
        pickle.dump(["not", "a", "dataframe"], f)
    rc = main([str(p), "--describe"])
    out_err = capsys.readouterr()
    assert rc == 2
    assert "Failed to read" in out_err.err


def test_pickle_writing(tmp_path, capsys):
    """Test saving DataFrame to pickle."""
    # First create a CSV to load
    src = tmp_path / "input.csv"
    src.write_text("a,b\n1,2\n3,4\n")
    
    # Load and save as pickle
    dest = tmp_path / "output.pkl"
    rc = main([str(src), "--to-pickle", str(dest)])
    assert rc == 0
    assert dest.exists()

    # Verify we can read it back
    rc = main([str(dest), "--describe"])
    out_err = capsys.readouterr()
    assert rc == 0
    assert "count" in out_err.out

    # Test error case: can't write to invalid path
    bad_dest = tmp_path / "nonexistent" / "out.pkl"
    rc = main([str(src), "--to-pickle", str(bad_dest)])
    out_err = capsys.readouterr()
    assert rc == 4  # pickle write error code
    assert "Failed to save pickle" in out_err.err


def test_slice_notation(tmp_path, capsys):
    """Test DataFrame slicing with Python slice notation."""
    # Create a CSV with 10 rows
    rows = "\n".join(f"val{i},letter{i}" for i in range(10))
    p = tmp_path / "data.csv"
    p.write_text(f"num,letter\n{rows}")

    # Test various slice notations
    tests =([
        ("5", "4   val4  letter4"),     # single index
        ("0:2", "0   val0  letter0"),   # start:stop (should see rows 0 and 1)
        ("0:2", "1   val1  letter1")]   # start:stop (should see rows 0 and 1)
        + [("::2", f"{c}   val{c}  letter{c}") for c in [0,2,4,6,8]]   # every second row (should see row 0)
        + [("7::", f"{c}   val{c}  letter{c}") for c in [7,8,9]]   # last three rows (should see row 7)
        + [("-3::", f"{c}   val{c}  letter{c}") for c in [7,8,9]]   # last three rows (should see row 7)
        + [("1:6:2", f"{c}   val{c}  letter{c}") for c in [1,3,5]]   # starting from row 1, every second row (should see row 0)
    )

    for slice_arg, expected in tests:
        rc = main([str(p), f"--slice={slice_arg}"])
        out_err = capsys.readouterr()
        assert rc == 0
        out_lines = [" ".join(l.split()) for l in out_err.out.splitlines()]
        assert " ".join(expected.split()) in out_lines  # Test one row from expected output

    # Test invalid slice
    rc = main([str(p), "--slice", "1:2:3:4"])
    out_err = capsys.readouterr()
    assert rc == 5
    assert "Invalid slice" in out_err.err
