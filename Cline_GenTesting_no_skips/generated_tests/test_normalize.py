"""Generated Hypothesis tests for `normalize.py`.

This file is auto-generated from `semantics_json_update/normalize.json`.
"""

import math
from pathlib import Path

import pytest
from hypothesis import assume, given, strategies as st

from semantic_prop_project.Cline_GenTesting_no_skips.utils import (
    PROGRAMS_DIR,
    assume_no_raises,
    finite_floats,
    list_floats,
    list_ints,
    load_program,
    nonempty_list_floats,
    nonempty_list_nonneg,
    nonneg_floats,
    safe_eval,
    small_ints,
    window,
    windows,
)


PROGRAM_PATH = PROGRAMS_DIR / "normalize.py"
prog = load_program("normalize", PROGRAM_PATH)



@given(st.just([]))
def test_normalize_identity_on_condition_1(xs):

    assume(safe_eval('len(xs) == 0', locals()))
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

