"""Generated Hypothesis tests for `feature_flag_rollout.py`.

This file is auto-generated from `semantics_json_update/feature_flag_rollout.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "feature_flag_rollout.py"
prog = load_program("feature_flag_rollout", PROGRAM_PATH)



@given(finite_floats, finite_floats)
def test_feature_flag_rollout_raises_on_condition_1(user_id, percentage):

    assume(safe_eval('not (0 <= percentage <= 1)', locals()))
    with pytest.raises(ValueError) as e:
        prog.feature_flag_rollout(user_id, percentage=percentage)
    _ = e

