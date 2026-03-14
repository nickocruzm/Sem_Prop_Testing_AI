"""Generated Hypothesis tests for `invoice_merge_stream.py`.

This file is auto-generated from `semantics_json_update/invoice_merge_stream.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "invoice_merge_stream.py"
prog = load_program("invoice_merge_stream", PROGRAM_PATH)




@given(st.integers())
def test_generated_no_supported_properties(_x):
    pytest.skip("No supported semantic properties could be translated for this program")

