"""Generated Hypothesis tests for `time_range_filter.py`.

This file is auto-generated from `semantics_json_update/time_range_filter.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "time_range_filter.py"
prog = load_program("time_range_filter", PROGRAM_PATH)



@given(finite_floats, small_ints, small_ints)
def test_time_range_filter_raises_on_condition_1(points, start, end):

    assume(safe_eval('start >= end', locals()))
    with pytest.raises(ValueError) as e:
        prog.time_range_filter(points, start, end)
    _ = e

