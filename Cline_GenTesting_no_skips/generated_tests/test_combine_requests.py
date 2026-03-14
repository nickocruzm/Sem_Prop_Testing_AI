"""Generated Hypothesis tests for `combine_requests.py`.

This file is auto-generated from `semantics_json_update/combine_requests.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "combine_requests.py"
prog = load_program("combine_requests", PROGRAM_PATH)




@given(st.integers())
def test_generated_no_supported_properties(_x):
    pytest.skip("No supported semantic properties could be translated for this program")

