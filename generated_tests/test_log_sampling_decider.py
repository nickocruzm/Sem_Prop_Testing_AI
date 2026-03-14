"""Generated Hypothesis tests for `log_sampling_decider.py`.

This file is auto-generated from `semantics_json_update/log_sampling_decider.json`.
"""

import importlib.util
import math
from pathlib import Path

import pytest
from hypothesis import assume, given, strategies as st


def _load_program(module_name: str, file_path: Path):
    """Import a python file by path without requiring it to be a package."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {module_name} from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


PROGRAM_PATH = Path(__file__).resolve().parents[1] / "python_programs" / "log_sampling_decider.py"
prog = _load_program("log_sampling_decider", PROGRAM_PATH)


# Base strategies (kept explicit to match the style of the assignment screenshot)
finite_floats = st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False)
nonneg_floats = st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False)
small_ints = st.integers(min_value=-20, max_value=20)

list_floats = st.lists(finite_floats, min_size=0, max_size=20)
nonempty_list_floats = st.lists(finite_floats, min_size=1, max_size=20)
nonempty_list_nonneg = st.lists(nonneg_floats, min_size=1, max_size=20)



@given(finite_floats, st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_log_sampling_decider_raises_on_condition_1(log_id, rate):

    assume(eval('not (0 <= rate <= 1)', {"__builtins__": {}}, {"len": len, "sum": sum, "any": any, "all": all, **locals()}))
    with pytest.raises(ValueError) as e:
        prog.log_sampling_decider(log_id, rate=rate)
    _ = e

