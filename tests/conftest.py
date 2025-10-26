import shutil
import time
import sys
from pathlib import Path

import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # attach the report object to the item so fixtures can inspect it
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def preserve_tmp_on_failure(request):
    """Autouse fixture: if the test fails and used `tmp_path`, preserve it.

    Copies the `tmp_path` directory to `./debug_temps/{testname}-{timestamp}` so
    developers can inspect test artifacts when debugging failures.
    """
    yield
    # After the test runs, check the call-phase report for failure
    rep = getattr(request.node, "rep_call", None)
    if not rep or not rep.failed:
        return

    # Only preserve if the test used the `tmp_path` fixture
    if "tmp_path" not in request.fixturenames:
        return

    try:
        tmp_path = request.getfixturevalue("tmp_path")
    except Exception:
        return

    dest = Path.cwd() / "debug_temps" / f"{request.node.name}-{int(time.time())}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(tmp_path, dest)
        print(f"Preserved tmp dir {tmp_path} -> {dest}", file=sys.stderr)
    except Exception as exc:
        print(f"Failed to preserve tmp dir for {request.node.name}: {exc}", file=sys.stderr)
