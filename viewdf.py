#!/usr/bin/env python3
"""
viewdf.py

Small CLI utility to quickly inspect tabular files (CSV/TSV/pickle) using pandas.
Supports viewing data frames, basic statistics, and format conversion.

Usage examples:
  # Basic data viewing
  viewdf.py data.csv                    # show first 5 rows (default)
  viewdf.py data.csv --head 10          # show first 10 rows
  viewdf.py data.csv --tail 3           # show last 3 rows
  viewdf.py data.csv --sample 5         # show 5 random rows
  viewdf.py data.csv --slice "1:10:2"   # show rows 1,3,5,7,9 (Python slice notation)
  
  # Structure inspection
  viewdf.py data.csv --columns          # list column names
  viewdf.py data.csv --shape            # show dimensions (rows × cols)
  viewdf.py data.csv --info             # show DataFrame.info()
  
  # Statistics
  viewdf.py data.csv --describe         # describe all columns
  viewdf.py data.csv --describe age     # describe single column
  
  # Format conversion
  viewdf.py data.csv --to-pickle data.pkl     # save as pickle
  viewdf.py data.tsv --sep '\t' --head 10     # read TSV with explicit separator
  viewdf.py data.pkl --describe               # read from pickle

Options:
  path              : Path to CSV/TSV file or pickled DataFrame (.pkl)
  --sep SEP         : Field separator (overrides auto-detection)
  --head N          : Show first N rows (default: 5)
  --tail N          : Show last N rows
  --sample N        : Show N random rows
  --slice SLICE     : Show rows using Python slice notation (start:stop:step)
  --describe [COL]  : Show statistics for all or one column
  --info            : Show DataFrame metadata (types, memory)
  --columns         : List column names only
  --shape           : Show dimensions as (rows, cols)
  --max_rows N      : Limit output to N rows (default: 200)
  --to-pickle PATH  : Save DataFrame as pickle file

Exit codes:
  0: Success
  2: Failed to read input file
  3: Column not found
  4: Failed to save pickle
  5: Invalid slice notation
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
    p = argparse.ArgumentParser(description="Quickly inspect a CSV/TSV/pickle file using pandas", 
                           allow_abbrev=False)  # Prevent -1 being interpreted as --info
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
    # Handle slice with negative indices by using a custom type function
    p.add_argument("--slice", type=str, 
                  help="Show DataFrame rows using Python slice notation (start:stop:step). Supports negative indices.",
                  metavar="SLICE")
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
        # Parse slice notation (start:stop:step) with support for negative indices
        try:
            # Ensure negative values and proper slice syntax
            if not all(c in "-0123456789:" for c in args.slice):
                raise ValueError("Slice must contain only digits, minus signs, and colons")
            
            # Split on colons and parse each part, handling empty parts as None
            parts = args.slice.split(":")
            if len(parts) > 3:
                raise ValueError("Slice must be in format start:stop:step")
                
            # Convert each part to int or None, preserving negative values
            slice_parts = []
            for p in parts:
                if not p:  # Empty part becomes None
                    slice_parts.append(None)
                else:
                    try:
                        slice_parts.append(int(p))
                    except ValueError:
                        raise ValueError(f"Invalid slice value: {p}")
            
            # Create slice object based on number of parts
            if len(slice_parts) == 1:
                sl = slice(slice_parts[0])
            elif len(slice_parts) == 2:
                sl = slice(slice_parts[0], slice_parts[1])
            else:  # len == 3
                sl = slice(slice_parts[0], slice_parts[1], slice_parts[2])
                
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
