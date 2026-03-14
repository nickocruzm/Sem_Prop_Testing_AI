"""Generated Hypothesis tests for `sensor_window_avg.py`.

This file is auto-generated from `semantics_json_update/sensor_window_avg.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "sensor_window_avg.py"
prog = load_program("sensor_window_avg", PROGRAM_PATH)



@given(finite_floats, st.floats(max_value=0.0, allow_nan=False, allow_infinity=False), finite_floats)
def test_sensor_window_avg_raises_on_condition_1(samples, window, min_samples):

    assume(safe_eval('window <= 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.sensor_window_avg(samples, window=window, min_samples=min_samples)
    _ = e



@given(st.just([]), finite_floats, finite_floats)
def test_sensor_window_avg_raises_on_condition_2(samples, window, min_samples):

    assume(safe_eval('not samples', locals()))
    with pytest.raises(ValueError) as e:
        prog.sensor_window_avg(samples, window=window, min_samples=min_samples)
    _ = e

