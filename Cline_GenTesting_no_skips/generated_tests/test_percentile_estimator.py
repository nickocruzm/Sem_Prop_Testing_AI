"""Generated Hypothesis tests for `percentile_estimator.py`.

This file is auto-generated from `semantics_json_update/percentile_estimator.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "percentile_estimator.py"
prog = load_program("percentile_estimator", PROGRAM_PATH)



@given(st.just([]), finite_floats)
def test_percentile_estimator_raises_on_condition_1(values, q):

    assume(safe_eval('not values', locals()))
    with pytest.raises(ValueError) as e:
        prog.percentile_estimator(values, q=q)
    _ = e



@given(list_floats, finite_floats)
def test_percentile_estimator_raises_on_condition_2(values, q):

    assume(safe_eval('not (0 <= q <= 1)', locals()))
    with pytest.raises(ValueError) as e:
        prog.percentile_estimator(values, q=q)
    _ = e

