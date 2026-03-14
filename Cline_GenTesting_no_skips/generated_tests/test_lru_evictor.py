"""Generated Hypothesis tests for `lru_evictor.py`.

This file is auto-generated from `semantics_json_update/lru_evictor.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "lru_evictor.py"
prog = load_program("lru_evictor", PROGRAM_PATH)



@given(finite_floats, st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False))
def test_lru_evictor_raises_on_condition_1(order, capacity):

    assume(safe_eval('capacity < 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.lru_evictor(order, capacity=capacity)
    _ = e

