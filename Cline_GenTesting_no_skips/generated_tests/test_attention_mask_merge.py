"""Generated Hypothesis tests for `attention_mask_merge.py`.

This file is auto-generated from `semantics_json_update/attention_mask_merge.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "attention_mask_merge.py"
prog = load_program("attention_mask_merge", PROGRAM_PATH)



@given(st.just([]), nonempty_list_floats)
def test_attention_mask_merge_raises_on_condition_1(mask_a, mask_b):

    assume(safe_eval('len(mask_a) != len(mask_b)', locals()))
    with pytest.raises(ValueError) as e:
        prog.attention_mask_merge(mask_a, mask_b)
    _ = e

