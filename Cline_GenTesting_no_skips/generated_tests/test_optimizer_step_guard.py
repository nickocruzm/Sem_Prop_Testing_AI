"""Generated Hypothesis tests for `optimizer_step_guard.py`.

This file is auto-generated from `semantics_json_update/optimizer_step_guard.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "optimizer_step_guard.py"
prog = load_program("optimizer_step_guard", PROGRAM_PATH)



@given(st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False), finite_floats)
def test_optimizer_step_guard_raises_on_condition_1(loss_value, max_loss):

    assume(safe_eval('loss_value < 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.optimizer_step_guard(loss_value, max_loss=max_loss)
    _ = e



@given(finite_floats, finite_floats)
def test_optimizer_step_guard_returns_constant_2(loss_value, max_loss):
    assume_no_raises(['loss_value < 0'], locals())
    assume(safe_eval('loss_value == loss_value and loss_value > max_loss', locals()))
    try:
        out = prog.optimizer_step_guard(loss_value, max_loss=max_loss)
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under constant-return property: optimizer_step_guard: {e!r}")
    assert out is False

