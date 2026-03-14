"""Generated Hypothesis tests for `request_token_bucket.py`.

This file is auto-generated from `semantics_json_update/request_token_bucket.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "request_token_bucket.py"
prog = load_program("request_token_bucket", PROGRAM_PATH)



@given(st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=-5, max_value=20), max_size=5), small_ints, st.floats(max_value=0.0, allow_nan=False, allow_infinity=False), st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
def test_request_token_bucket_raises_on_condition_1(tokens, now, rate, capacity):

    assume(safe_eval('rate <= 0 or capacity <= 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.request_token_bucket(tokens, now, rate=rate, capacity=capacity)
    _ = e

