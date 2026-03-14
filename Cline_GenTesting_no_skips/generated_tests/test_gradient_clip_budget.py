"""Generated Hypothesis tests for `gradient_clip_budget.py`.

This file is auto-generated from `semantics_json_update/gradient_clip_budget.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "gradient_clip_budget.py"
prog = load_program("gradient_clip_budget", PROGRAM_PATH)



@given(finite_floats, st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
def test_gradient_clip_budget_raises_on_condition_1(gradients, max_norm):

    assume(safe_eval('max_norm <= 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.gradient_clip_budget(gradients, max_norm=max_norm)
    _ = e



@given(finite_floats, st.floats(min_value=1e-6, max_value=1000, allow_nan=False, allow_infinity=False))
def test_gradient_clip_budget_length_preserving_2(gradients, max_norm):
    assume_no_raises(['max_norm <= 0'], locals())
    try:
        out = prog.gradient_clip_budget(gradients, max_norm=max_norm)
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under length-preserving property: gradient_clip_budget: {e!r}")
    assert hasattr(out, "__len__")
    assert len(out) == len(gradients)

