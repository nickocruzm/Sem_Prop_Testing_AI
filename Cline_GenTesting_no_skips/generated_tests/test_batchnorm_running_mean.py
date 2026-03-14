"""Generated Hypothesis tests for `batchnorm_running_mean.py`.

This file is auto-generated from `semantics_json_update/batchnorm_running_mean.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "batchnorm_running_mean.py"
prog = load_program("batchnorm_running_mean", PROGRAM_PATH)



@given(finite_floats, finite_floats, finite_floats)
def test_batchnorm_running_mean_raises_on_condition_1(current_mean, batch_mean, momentum):

    assume(safe_eval('not (0 <= momentum <= 1)', locals()))
    with pytest.raises(ValueError) as e:
        prog.batchnorm_running_mean(current_mean, batch_mean, momentum=momentum)
    _ = e

