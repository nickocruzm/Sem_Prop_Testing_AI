"""Generated Hypothesis tests for `lr_warmup_schedule.py`.

This file is auto-generated from `semantics_json_update/lr_warmup_schedule.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "lr_warmup_schedule.py"
prog = load_program("lr_warmup_schedule", PROGRAM_PATH)



@given(finite_floats, finite_floats, st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
def test_lr_warmup_schedule_raises_on_condition_1(step, base_lr, warmup_steps):

    assume(safe_eval('warmup_steps <= 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.lr_warmup_schedule(step, base_lr=base_lr, warmup_steps=warmup_steps)
    _ = e



@given(st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False), finite_floats, finite_floats)
def test_lr_warmup_schedule_raises_on_condition_2(step, base_lr, warmup_steps):

    assume(safe_eval('step < 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.lr_warmup_schedule(step, base_lr=base_lr, warmup_steps=warmup_steps)
    _ = e

