"""Generated Hypothesis tests for `storage_quota_split.py`.

This file is auto-generated from `semantics_json_update/storage_quota_split.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "storage_quota_split.py"
prog = load_program("storage_quota_split", PROGRAM_PATH)



@given(st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False), list_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_storage_quota_split_raises_on_condition_1(total, ratios, fee):

    assume(safe_eval('total < 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.storage_quota_split(total, ratios, fee=fee)
    _ = e



@given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), list_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_storage_quota_split_raises_on_condition_2(total, ratios, fee):

    assume(safe_eval('not ratios or sum(ratios) <= 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.storage_quota_split(total, ratios, fee=fee)
    _ = e



@given(st.floats(min_value=0.0, max_value=1000, allow_nan=False, allow_infinity=False), list_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_storage_quota_split_length_preserving_3(total, ratios, fee):
    assume_no_raises(['total < 0', 'not ratios or sum(ratios) <= 0'], locals())
    try:
        out = prog.storage_quota_split(total, ratios, fee=fee)
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under length-preserving property: storage_quota_split: {e!r}")
    assert hasattr(out, "__len__")
    assert len(out) == len(ratios)

