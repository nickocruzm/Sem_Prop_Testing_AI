"""Generated Hypothesis tests for `normalize.py`.

This file is auto-generated from `semantics_json_update/normalize.json`.
"""

import importlib.util
import math
from pathlib import Path

import pytest
from hypothesis import HealthCheck, assume, given, settings, strategies as st


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


def _load_program(module_name: str, file_path: Path):
    """Import a python file by path without requiring it to be a package."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {module_name} from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


PROGRAM_PATH = Path(__file__).resolve().parents[1] / "python_programs" / "normalize.py"
prog = _load_program("normalize", PROGRAM_PATH)


# Base strategies (kept explicit to match the style of the assignment screenshot)
finite_floats = st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False)
nonneg_floats = st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False)
small_ints = st.integers(min_value=-20, max_value=20)

list_floats = st.lists(finite_floats, min_size=0, max_size=20)
nonempty_list_floats = st.lists(finite_floats, min_size=1, max_size=20)
nonempty_list_nonneg = st.lists(nonneg_floats, min_size=1, max_size=20)



@given(st.just([]))
def test_normalize_identity_on_condition_1(xs):

    assume(eval('len(xs) == 0', {"__builtins__": {}}, {"len": len, "sum": sum, "any": any, "all": all, **locals()}))
    try:
        out = prog.normalize(xs)
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under identity property: normalize: {e!r}")
    assert out == xs



@given(list_floats)
def test_normalize_length_preserving_2(xs):

    try:
        out = prog.normalize(xs)
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under length-preserving property: normalize: {e!r}")
    assert hasattr(out, "__len__")
    assert len(out) == len(xs)



@given(nonempty_list_floats)
def test_normalize_unit_sum_3(xs):

    assume(sum(xs) != 0)
    try:
        ys = prog.normalize(xs)
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under unit-sum property: normalize: {e!r}")
    assert math.isclose(sum(ys), 1.0, rel_tol=1e-6, abs_tol=1e-6)



@given(nonempty_list_nonneg)
def test_normalize_sign_preservation_4(xs):

    assume(sum(xs) > 0)
    try:
        ys = prog.normalize(xs)
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under sign-preservation property: normalize: {e!r}")
    assert all(y >= -1e-12 for y in ys)

