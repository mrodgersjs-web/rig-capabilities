#!/usr/bin/env python3
"""Run every test suite in this directory under stdlib unittest.

The vendored rig-deviator suites are written pytest-style — module-level
``def test_*()`` functions with bare asserts — and this repo is
stdlib-unittest only. The collector below wraps each such function in a
``unittest.FunctionTestCase`` so both shapes run through one runner with no
third-party dependency.

    python3 tests/run_all.py           # everything
    python3 tests/run_all.py --fast    # integrity + lattice math + gates only
    python3 tests/run_all.py -v        # per-test names

Exits non-zero on any failure and prints ``RESULT: n/n passed``.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = TESTS_DIR.parent

# The payload imports as `rig_lattice.*`, so the skill dir must be importable.
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

# --fast subset: the deterministic core. No engine corpus recalibration, no
# 40-pack audit sweep. This is what the SKILL.md done_when runs, because
# rig_capabilities/done_tests.py caps each `cmd:` at 15 s.
FAST_SUITES = (
    "test_bundle_integrity",
    "test_lattice_math",
    "test_idea_gates",
)


def _load_module(path: Path):
    name = f"rig_lattice_tests_{path.stem}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _suite_for(module) -> unittest.TestSuite:
    """Collect TestCase classes AND bare pytest-style test functions."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # unittest.TestCase subclasses defined in the module
    suite.addTests(loader.loadTestsFromModule(module))

    # module-level `def test_*()` functions (pytest style)
    for name in sorted(vars(module)):
        if not name.startswith("test_"):
            continue
        fn = getattr(module, name)
        if not callable(fn) or isinstance(fn, type):
            continue
        if getattr(fn, "__module__", None) != module.__name__:
            continue
        # Functions that still demand pytest fixtures cannot run here; they
        # are reported as errors rather than silently skipped.
        argcount = fn.__code__.co_argcount
        if argcount:
            defaults = fn.__defaults__ or ()
            if argcount > len(defaults):
                def _needs_fixtures(fn=fn, name=name, argcount=argcount):
                    raise AssertionError(
                        f"{name} needs {argcount} pytest fixture(s); port it "
                        "to tempfile/unittest instead"
                    )

                suite.addTest(unittest.FunctionTestCase(_needs_fixtures))
                continue
        suite.addTest(unittest.FunctionTestCase(fn, description=f"{module.__name__}.{name}"))

    return suite


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fast", action="store_true",
                     help="run only the deterministic core subset")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    paths = sorted(TESTS_DIR.glob("test_*.py"))
    if args.fast:
        paths = [p for p in paths if p.stem in FAST_SUITES]
    if not paths:
        print("RESULT: no suites found", file=sys.stderr)
        return 1

    master = unittest.TestSuite()
    load_errors: list[str] = []
    for path in paths:
        try:
            master.addTests(_suite_for(_load_module(path)))
        except Exception as exc:  # a module that will not import is a failure
            load_errors.append(f"{path.name}: {type(exc).__name__}: {exc}")

    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    result = runner.run(master)

    for err in load_errors:
        print(f"LOAD ERROR: {err}", file=sys.stderr)

    total = result.testsRun + len(load_errors)
    failed = len(result.failures) + len(result.errors) + len(load_errors)
    passed = total - failed - len(result.skipped)
    print(
        f"RESULT: {passed}/{total - len(result.skipped)} passed"
        + (f" ({len(result.skipped)} skipped)" if result.skipped else "")
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
