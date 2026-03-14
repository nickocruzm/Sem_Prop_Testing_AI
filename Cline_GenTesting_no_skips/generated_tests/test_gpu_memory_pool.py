"""Generated Hypothesis tests for `gpu_memory_pool.py`.

This file is auto-generated from `semantics_json_update/gpu_memory_pool.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "gpu_memory_pool.py"
prog = load_program("gpu_memory_pool", PROGRAM_PATH)



@given(finite_floats, finite_floats, st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
def test_gpu_memory_pool_raises_on_condition_1(allocations, request, capacity):

    assume(safe_eval('capacity <= 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.gpu_memory_pool(allocations, request, capacity=capacity)
    _ = e



@given(finite_floats, st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False), st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_gpu_memory_pool_raises_on_condition_2(allocations, request, capacity):

    assume(safe_eval('request < 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.gpu_memory_pool(allocations, request, capacity=capacity)
    _ = e

