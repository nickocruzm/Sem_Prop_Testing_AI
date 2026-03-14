"""Generated Hypothesis tests for `dataloader_shard_merge.py`.

This file is auto-generated from `semantics_json_update/dataloader_shard_merge.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "dataloader_shard_merge.py"
prog = load_program("dataloader_shard_merge", PROGRAM_PATH)




@given(st.integers())
def test_generated_no_supported_properties(_x):
    pytest.skip("No supported semantic properties could be translated for this program")

