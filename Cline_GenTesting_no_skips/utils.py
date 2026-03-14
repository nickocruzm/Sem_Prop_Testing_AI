"""Utilities shared by generated Hypothesis tests.

This file is auto-generated.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Mapping

import pytest
from hypothesis import HealthCheck, assume, settings, strategies as st


# Suppress Hypothesis "filter too much" health-checks.
#
# Generated tests frequently use `assume(...)` for preconditions/guards.
# That is *expected* here because the semantic properties are conditional.
settings.register_profile(
    "semantic_props",
    deadline=None,
    suppress_health_check=[HealthCheck.filter_too_much],
)
settings.load_profile("semantic_props")


HERE = Path(__file__).resolve()
SEMANTIC_PROJECT_ROOT = HERE.parents[1]
PROGRAMS_DIR = SEMANTIC_PROJECT_ROOT / "python_programs"


def load_program(module_name: str, file_path: Path):
    """Import a python file by path without requiring it to be a package."""
    if not file_path.exists():
        pytest.skip(f"Program file not found: {file_path}")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {module_name} from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


# Base strategies (kept explicit to match the style of the assignment screenshot)
finite_floats = st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False)
nonneg_floats = st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False)
small_ints = st.integers(min_value=-20, max_value=20)

list_floats = st.lists(finite_floats, min_size=0, max_size=20)
nonempty_list_floats = st.lists(finite_floats, min_size=1, max_size=20)
nonempty_list_nonneg = st.lists(nonneg_floats, min_size=1, max_size=20)

# Common structured inputs
window = st.tuples(finite_floats, finite_floats)
windows = st.lists(window, min_size=0, max_size=20)

list_ints = st.lists(small_ints, min_size=0, max_size=200)
nonempty_list_ints = st.lists(small_ints, min_size=1, max_size=200)


def safe_eval(expr: str, local_vars: Mapping[str, Any]) -> Any:
    """Evaluate a *very* restricted expression against locals.

    Allowed functions: len, sum, any, all
    Builtins disabled.
    """
    try:
        return eval(
            expr,
            {"__builtins__": {}},
            {
                "len": len,
                "sum": sum,
                "any": any,
                "all": all,
                **dict(local_vars),
            },
        )
    except Exception:
        # If the expression doesn't type-check against the generated inputs
        # (e.g., `len(x)` where `x` was a float), treat it as False so tests
        # can reject that input via `assume(...)` instead of erroring.
        return False


def assume_no_raises(raise_conds: list[str], local_vars: Mapping[str, Any]) -> None:
    """Assume that none of the given raise-guard conditions hold."""
    for rc in raise_conds:
        assume(not bool(safe_eval(rc, local_vars)))
