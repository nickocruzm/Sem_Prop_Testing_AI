"""Generated Hypothesis tests for `tensor_slice_pad.py`.

This file is auto-generated from `semantics_json_update/tensor_slice_pad.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "tensor_slice_pad.py"
prog = load_program("tensor_slice_pad", PROGRAM_PATH)



@given(list_floats, small_ints, small_ints, finite_floats)
def test_tensor_slice_pad_raises_on_condition_1(values, start, end, pad):

    assume(safe_eval('start < 0 or end < start', locals()))
    with pytest.raises(ValueError) as e:
        prog.tensor_slice_pad(values, start, end, pad=pad)
    _ = e

