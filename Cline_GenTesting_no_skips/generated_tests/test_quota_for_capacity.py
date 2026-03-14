"""Generated Hypothesis tests for `quota_for_capacity.py`.

This file is auto-generated from `semantics_json_update/quota_for_capacity.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "quota_for_capacity.py"
prog = load_program("quota_for_capacity", PROGRAM_PATH)



@given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), st.just([]), finite_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_quota_for_capacity_raises_on_condition_1(total, weights, floor_to_int, minimum):

    assume(safe_eval('len(weights) == 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.quota_for_capacity(total, weights, floor_to_int=floor_to_int, minimum=minimum)
    _ = e



@given(st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False), list_floats, finite_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_quota_for_capacity_raises_on_condition_2(total, weights, floor_to_int, minimum):

    assume(safe_eval('total < 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.quota_for_capacity(total, weights, floor_to_int=floor_to_int, minimum=minimum)
    _ = e



@given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), list_floats, finite_floats, st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False))
def test_quota_for_capacity_raises_on_condition_3(total, weights, floor_to_int, minimum):

    assume(safe_eval('minimum < 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.quota_for_capacity(total, weights, floor_to_int=floor_to_int, minimum=minimum)
    _ = e



@given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), st.lists(st.just(0.0), min_size=1, max_size=20), finite_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_quota_for_capacity_raises_on_condition_4(total, weights, floor_to_int, minimum):

    assume(safe_eval('sum(weights) == 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.quota_for_capacity(total, weights, floor_to_int=floor_to_int, minimum=minimum)
    _ = e



@given(st.floats(min_value=0.0, max_value=1000, allow_nan=False, allow_infinity=False), st.lists(st.just(1.0), min_size=1, max_size=20), finite_floats, st.floats(min_value=0.0, max_value=1000, allow_nan=False, allow_infinity=False))
def test_quota_for_capacity_length_preserving_5(total, weights, floor_to_int, minimum):
    assume_no_raises(['len(weights) == 0', 'total < 0', 'minimum < 0', 'sum(weights) == 0'], locals())
    try:
        out = prog.quota_for_capacity(total, weights, floor_to_int=floor_to_int, minimum=minimum)
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under length-preserving property: quota_for_capacity: {e!r}")
    assert hasattr(out, "__len__")
    assert len(out) == len(weights)

