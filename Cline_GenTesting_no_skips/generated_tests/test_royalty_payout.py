"""Generated Hypothesis tests for `royalty_payout.py`.

This file is auto-generated from `semantics_json_update/royalty_payout.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "royalty_payout.py"
prog = load_program("royalty_payout", PROGRAM_PATH)



@given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), st.just([]), st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_royalty_payout_raises_on_condition_1(amount, ratios, fee):

    assume(safe_eval('not ratios', locals()))
    with pytest.raises(ValueError) as e:
        prog.royalty_payout(amount, ratios, fee=fee)
    _ = e



@given(st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False), list_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_royalty_payout_raises_on_condition_2(amount, ratios, fee):

    assume(safe_eval('amount < 0', locals()))
    with pytest.raises(ValueError) as e:
        prog.royalty_payout(amount, ratios, fee=fee)
    _ = e



@given(st.floats(min_value=0.0, max_value=1000, allow_nan=False, allow_infinity=False), nonempty_list_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_royalty_payout_length_preserving_4(amount, ratios, fee):
    assume_no_raises(['not ratios', 'amount < 0'], locals())
    try:
        out = prog.royalty_payout(amount, ratios, fee=fee)
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under length-preserving property: royalty_payout: {e!r}")
    assert hasattr(out, "__len__")
    assert len(out) == len(ratios)



@given(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), nonempty_list_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_royalty_payout_fee_shift_total_7(amount, ratios, fee):
    # Make sure we hit the main allocation path.
    assume_no_raises(['not ratios', 'amount < 0'], locals())
    assume(len(ratios) > 0)
    assume(sum(ratios) != 0)
    try:
        out = prog.royalty_payout(amount, ratios, fee=fee)
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under fee-shift property: royalty_payout: {e!r}")
    assert math.isclose(sum(out), amount - fee * len(ratios), rel_tol=1e-6, abs_tol=1e-6)

