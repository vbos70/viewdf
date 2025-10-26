## Copilot / AI agent instructions for this repository

A Python utility (`viewdf.py`) to inspect tabular data files (CSV/TSV) using pandas, with a focus on quick column inspection and statistical summaries.

Project structure
- `viewdf.py` - Main CLI utility
- `tests/` - Pytest test suite
  - `test_viewdf.py` - Core functionality tests
  - `conftest.py` - Test fixtures and debug helpers

Quick contract
- Input: CSV/TSV files to inspect.
- Output: Column stats, head/tail previews, shape info.
- Typical usage: `python viewdf.py data.csv --describe [COLUMN]`

Development environment
- Python venv under `.venv/`
- Core dependencies: pandas, pytest
- Run tests: `/home/vbos/projects/viewdf/.venv/bin/python -m pytest -q`

Common commands (path prefix omitted for brevity)
```bash
# View file stats
viewdf.py data.csv --describe    # whole file stats
viewdf.py data.csv --describe age  # single column
viewdf.py data.csv --head 10    # preview rows
viewdf.py data.csv --columns    # list columns
viewdf.py data.csv --shape      # dimensions

# Development
pytest -q                       # quick test run
pytest -v                       # verbose test output
```

Project-specific patterns
- CLI follows standard argparse patterns with explicit arguments.
- Tests use `tmp_path` fixture for isolation.
- Failed tests preserve temp files in `debug_temps/` for inspection.

Examples to include in PRs or commits
- Short commit message describing intent and scope. Example: `feat(cli): add --sample N flag for random rows`
- Always include test coverage. Example:
  ```python
  def test_new_feature(tmp_path):
      p = tmp_path / "data.csv"
      p.write_text("a,b\n1,2\n3,4\n")
      rc = main([str(p), "--new-flag"])
      assert rc == 0
  ```

Testing notes
- Tests automatically preserve temp files on failure under `debug_temps/{testname}-{timestamp}/`.
- Large-file tests use 10k rows × 50 cols with deterministic data.
- Use `capsys` fixture to inspect stdout/stderr.

When to ask before changing code
- No test coverage for a new feature.
- Changes to DataFrame output format.
- New pandas dependencies.
- Performance changes that could affect large files.

Edit history
- Updated by an automated assistant based on current repository state including Python CLI, test suite, and development conventions.
