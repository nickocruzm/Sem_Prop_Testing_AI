"""Generated Hypothesis tests for `reserve_lane.py`.

This file is auto-generated from `semantics_json_update/reserve_lane.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "reserve_lane.py"
prog = load_program("reserve_lane", PROGRAM_PATH)



@given(windows, window)
def test_reserve_lane_raises_on_condition_1(existing, candidate):

    assume(safe_eval('candidate[0] >= candidate[1]', locals()))
    with pytest.raises(ValueError) as e:
        prog.reserve_lane(existing, candidate)
    _ = e

