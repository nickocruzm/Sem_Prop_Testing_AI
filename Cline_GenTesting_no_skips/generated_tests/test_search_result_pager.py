"""Generated Hypothesis tests for `search_result_pager.py`.

This file is auto-generated from `semantics_json_update/search_result_pager.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "search_result_pager.py"
prog = load_program("search_result_pager", PROGRAM_PATH)



@given(finite_floats, finite_floats, finite_floats)
def test_search_result_pager_raises_on_condition_1(results, page, page_size):

    assume(safe_eval('page < 1', locals()))
    with pytest.raises(ValueError) as e:
        prog.search_result_pager(results, page, page_size=page_size)
    _ = e



@given(finite_floats, finite_floats, st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
def test_search_result_pager_raises_on_condition_2(results, page, page_size):

    assume(safe_eval('page_size <= 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.search_result_pager(results, page, page_size=page_size)
    _ = e

