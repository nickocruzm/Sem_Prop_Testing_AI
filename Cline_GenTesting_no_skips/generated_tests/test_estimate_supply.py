"""Generated Hypothesis tests for `estimate_supply.py`.

This file is auto-generated from `semantics_json_update/estimate_supply.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "estimate_supply.py"
prog = load_program("estimate_supply", PROGRAM_PATH)



@given(finite_floats, finite_floats, finite_floats, finite_floats, finite_floats, finite_floats)
def test_estimate_supply_raises_on_condition_1(x0, y0, x1, y1, x, clamp):

    assume(safe_eval('x1 == x0', locals()))
    with pytest.raises(ValueError) as e:
        prog.estimate_supply(x0, y0, x1, y1, x, clamp=clamp)
    _ = e

