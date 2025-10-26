#!/usr/bin/env python3
"""
viewdf.py

Small CLI utility to quickly inspect tabular files (CSV/TSV) using pandas.

Assumptions made:
- The workspace did not include a file to create; you asked to create `viewdf.py` so I implemented a sensible default tool.
- This script is intentionally small and dependency-light (requires `pandas`).

Usage examples:
  /home/vbos/projects/viewdf/.venv/bin/python viewdf.py data.csv --head 10
  /home/vbos/projects/viewdf/.venv/bin/python viewdf.py data.tsv --sep '\t' --describe

Options:
  --head N       : print first N rows (default: 5)
  --tail N       : print last N rows
  --describe     : print pandas describe()
  --info         : print DataFrame.info()
  --columns      : list column names
  --shape        : print (rows, cols)
  --sample N     : print a random sample of N rows
  --max_rows N   : max rows to display when printing DataFrame (pandas.option_context)

"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

import pandas as pd


def load_dataframe(path: str, sep: Optional[str]) -> pd.DataFrame:
    """Load a dataframe from a CSV/TSV/pickle file.

    If path ends with .csv/.tsv it's parsed as delimited text.
    If path ends with .pkl it's loaded as a pickled pandas DataFrame.
    The `sep` parameter overrides delimiter detection for CSV/TSV files.
    """
    try:
        if path.endswith(".pkl"):
            df = pd.read_pickle(path)
            if not isinstance(df, pd.DataFrame):
                raise RuntimeError(f"Pickle contains {type(df).__name__}, not a DataFrame")
        else:
            if sep is None:
                # try to infer from extension for text files
                if path.endswith(".tsv") or path.endswith(".txt"):
                    sep = "\t"
                else:
                    sep = ","
            df = pd.read_csv(path, sep=sep)
    except Exception as exc:
        raise RuntimeError(f"Failed to read {path!r}: {exc}")
    return df


def print_df(df: pd.DataFrame, max_rows: int = 200) -> None:
    """Print dataframe with a maximum number of rows for readability."""
    with pd.option_context("display.max_rows", max_rows, "display.max_columns", 20):
        print(df)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Quickly inspect a CSV/TSV/pickle file using pandas")
    p.add_argument("path", help="Path to CSV/TSV file or pickled DataFrame (.pkl)")
    p.add_argument("--sep", help="Field separator (overrides detection)")
    p.add_argument("--head", type=int, nargs="?", const=5, help="Show first N rows (default 5)")
    p.add_argument("--tail", type=int, help="Show last N rows")
    p.add_argument(
        "--describe",
        nargs="?",
        const=True,
        help="Show describe() output. Optionally pass a column name: --describe COLUMN",
    )
    p.add_argument("--info", action="store_true", help="Show DataFrame.info()")
    p.add_argument("--columns", action="store_true", help="List column names")
    p.add_argument("--shape", action="store_true", help="Show dataframe shape")
    p.add_argument("--sample", type=int, help="Show a random sample of N rows")
    p.add_argument("--slice", help="Show DataFrame rows using Python slice notation (start:stop:step)")
    p.add_argument("--max_rows", type=int, default=200, help="Max rows to print when showing DataFrame")
    p.add_argument("--to-pickle", help="Save DataFrame to a pickle file at the given path")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        df = load_dataframe(args.path, args.sep)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2

    # Actions
    if args.columns:
        for c in df.columns:
            print(c)
    if args.shape:
        print(tuple(df.shape))
    if args.info:
        # DataFrame.info prints to stdout by default
        df.info()
    if args.describe is not False:
        # args.describe == True or None -> show describe for entire DataFrame
        # args.describe == <str> -> describe only that column
        if args.describe is True or args.describe is None:
            print(df.describe(include="all"))
        else:
            col = args.describe
            if col not in df.columns:
                print(f"Column {col!r} not found", file=sys.stderr)
                return 3
            # Series.describe() is appropriate for a single column
            print(df[col].describe())
    if args.head is not None:
        print_df(df.head(args.head), max_rows=args.max_rows)
    if args.tail is not None:
        print_df(df.tail(args.tail), max_rows=args.max_rows)
    if args.sample is not None:
        print_df(df.sample(n=args.sample), max_rows=args.max_rows)
    if args.slice is not None:
        # Parse slice notation (start:stop:step)
        try:
            parts = [int(p) if p else None for p in args.slice.split(":")]
            if len(parts) == 1:
                sl = slice(parts[0])
            elif len(parts) == 2:
                sl = slice(parts[0], parts[1])
            elif len(parts) == 3:
                sl = slice(parts[0], parts[1], parts[2])
            else:
                raise ValueError("Slice must be in format start:stop:step")
            result = df.iloc[sl]
            if not isinstance(result, pd.DataFrame):  # Single row
                result = result.to_frame().transpose()
            with pd.option_context('display.max_rows', args.max_rows):
                print(result.to_string(index=True))
            return 0
        except Exception as exc:
            print(f"Invalid slice {args.slice!r}: {exc}", file=sys.stderr)
            return 5

    # If no action flags provided, default to head
    if not (args.columns or args.shape or args.info or args.describe or 
            args.head is not None or args.tail is not None or 
            args.sample is not None or args.slice is not None or
            args.to_pickle):
        print_df(df.head(5), max_rows=args.max_rows)

    # Save to pickle if requested
    if args.to_pickle:
        try:
            df.to_pickle(args.to_pickle)
        except Exception as exc:
            print(f"Failed to save pickle to {args.to_pickle!r}: {exc}", file=sys.stderr)
            return 4
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
