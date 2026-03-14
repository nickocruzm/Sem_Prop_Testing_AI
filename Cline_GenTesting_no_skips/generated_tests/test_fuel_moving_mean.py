"""Generated Hypothesis tests for `fuel_moving_mean.py`.

This file is auto-generated from `semantics_json_update/fuel_moving_mean.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "fuel_moving_mean.py"
prog = load_program("fuel_moving_mean", PROGRAM_PATH)



@given(list_floats, st.floats(max_value=0.0, allow_nan=False, allow_infinity=False), finite_floats)
def test_fuel_moving_mean_raises_on_condition_1(values, window, warmup_min):

    assume(safe_eval('window <= 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.fuel_moving_mean(values, window=window, warmup_min=warmup_min)
    _ = e



@given(st.just([]), finite_floats, finite_floats)
def test_fuel_moving_mean_raises_on_condition_2(values, window, warmup_min):

    assume(safe_eval('not values', locals()))
    with pytest.raises(ValueError) as e:
        prog.fuel_moving_mean(values, window=window, warmup_min=warmup_min)
    _ = e

