"""Generated Hypothesis tests for `realign_replica.py`.

This file is auto-generated from `semantics_json_update/realign_replica.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "realign_replica.py"
prog = load_program("realign_replica", PROGRAM_PATH)



@given(st.just([]), nonempty_list_floats, finite_floats)
def test_realign_replica_raises_on_condition_1(current, target, damping):

    assume(safe_eval('len(current) != len(target)', locals()))
    with pytest.raises(ValueError) as e:
        prog.realign_replica(current, target, damping=damping)
    _ = e



@given(st.just([]), list_floats, finite_floats)
def test_realign_replica_raises_on_condition_2(current, target, damping):

    assume(safe_eval('not current', locals()))
    with pytest.raises(ValueError) as e:
        prog.realign_replica(current, target, damping=damping)
    _ = e

