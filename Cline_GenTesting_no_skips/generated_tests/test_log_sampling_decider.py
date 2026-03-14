"""Generated Hypothesis tests for `log_sampling_decider.py`.

This file is auto-generated from `semantics_json_update/log_sampling_decider.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "log_sampling_decider.py"
prog = load_program("log_sampling_decider", PROGRAM_PATH)



@given(finite_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_log_sampling_decider_raises_on_condition_1(log_id, rate):

    assume(safe_eval('not (0 <= rate <= 1)', locals()))
    with pytest.raises(ValueError) as e:
        prog.log_sampling_decider(log_id, rate=rate)
    _ = e

