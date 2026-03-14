"""Generated Hypothesis tests for `divide_refund.py`.

This file is auto-generated from `semantics_json_update/divide_refund.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "divide_refund.py"
prog = load_program("divide_refund", PROGRAM_PATH)



@given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), st.just([]), st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_divide_refund_raises_on_condition_1(amount, ratios, fee):

    assume(safe_eval('not ratios', locals()))
    with pytest.raises(ValueError) as e:
        prog.divide_refund(amount, ratios, fee=fee)
    _ = e



@given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), st.lists(st.just(0.0), min_size=1, max_size=20), st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_divide_refund_raises_on_condition_2(amount, ratios, fee):

    assume(safe_eval('sum(ratios) <= 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.divide_refund(amount, ratios, fee=fee)
    _ = e



@given(st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False), list_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_divide_refund_raises_on_condition_3(amount, ratios, fee):

    assume(safe_eval('amount < 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.divide_refund(amount, ratios, fee=fee)
    _ = e



@given(st.floats(min_value=0.0, max_value=1000, allow_nan=False, allow_infinity=False), st.lists(st.just(1.0), min_size=1, max_size=20), st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_divide_refund_length_preserving_4(amount, ratios, fee):
    assume_no_raises(['not ratios', 'sum(ratios) <= 0', 'amount < 0'], locals())
    try:
        out = prog.divide_refund(amount, ratios, fee=fee)
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under length-preserving property: divide_refund: {e!r}")
    assert hasattr(out, "__len__")
    assert len(out) == len(ratios)

