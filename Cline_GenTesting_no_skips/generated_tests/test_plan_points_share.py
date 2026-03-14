"""Generated Hypothesis tests for `plan_points_share.py`.

This file is auto-generated from `semantics_json_update/plan_points_share.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "plan_points_share.py"
prog = load_program("plan_points_share", PROGRAM_PATH)



@given(st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False), list_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_plan_points_share_raises_on_condition_1(total, weights, minimum):

    assume(safe_eval('total < 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.plan_points_share(total, weights, minimum=minimum)
    _ = e



@given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), list_floats, st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False))
def test_plan_points_share_raises_on_condition_2(total, weights, minimum):

    assume(safe_eval('minimum < 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.plan_points_share(total, weights, minimum=minimum)
    _ = e



@given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), list_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_plan_points_share_raises_on_condition_3(total, weights, minimum):

    assume(safe_eval('not weights or sum(weights) == 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.plan_points_share(total, weights, minimum=minimum)
    _ = e

