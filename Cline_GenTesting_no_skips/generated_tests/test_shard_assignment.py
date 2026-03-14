"""Generated Hypothesis tests for `shard_assignment.py`.

This file is auto-generated from `semantics_json_update/shard_assignment.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "shard_assignment.py"
prog = load_program("shard_assignment", PROGRAM_PATH)



@given(finite_floats, st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
def test_shard_assignment_raises_on_condition_1(keys, shards):

    assume(safe_eval('shards <= 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.shard_assignment(keys, shards=shards)
    _ = e

