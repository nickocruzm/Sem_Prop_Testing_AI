"""Generated Hypothesis tests for `downtime_booking.py`.

This file is auto-generated from `semantics_json_update/downtime_booking.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "downtime_booking.py"
prog = load_program("downtime_booking", PROGRAM_PATH)



@given(windows, window)
def test_downtime_booking_raises_on_condition_1(existing, candidate):

    assume(safe_eval('candidate[0] >= candidate[1]', locals()))
    with pytest.raises(ValueError) as e:
        prog.downtime_booking(existing, candidate)
    _ = e

