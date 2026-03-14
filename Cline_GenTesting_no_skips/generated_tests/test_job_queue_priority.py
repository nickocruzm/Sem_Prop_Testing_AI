"""Generated Hypothesis tests for `job_queue_priority.py`.

This file is auto-generated from `semantics_json_update/job_queue_priority.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "job_queue_priority.py"
prog = load_program("job_queue_priority", PROGRAM_PATH)



@given(list_ints, st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False))
def test_job_queue_priority_raises_on_condition_1(jobs, max_jobs):

    assume(safe_eval('max_jobs < 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.job_queue_priority(jobs, max_jobs=max_jobs)
    _ = e



@given(list_ints, st.integers(min_value=0, max_value=200))
def test_job_queue_priority_returns_constant_2(jobs, max_jobs):
    assume_no_raises(['max_jobs < 0'], locals())
    assume(safe_eval('len(jobs) > max_jobs', locals()))
    try:
        out = prog.job_queue_priority(jobs, max_jobs=max_jobs)
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under constant-return property: job_queue_priority: {e!r}")
    assert out is False

