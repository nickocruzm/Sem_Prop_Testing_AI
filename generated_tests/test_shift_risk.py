"""Generated Hypothesis tests for `shift_risk.py`.

This file is auto-generated from `semantics_json_update/shift_risk.json`.
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


PROGRAM_PATH = Path(__file__).resolve().parents[1] / "python_programs" / "shift_risk.py"
prog = _load_program("shift_risk", PROGRAM_PATH)


# Base strategies (kept explicit to match the style of the assignment screenshot)
finite_floats = st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False)
nonneg_floats = st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False)
small_ints = st.integers(min_value=-20, max_value=20)

list_floats = st.lists(finite_floats, min_size=0, max_size=20)
nonempty_list_floats = st.lists(finite_floats, min_size=1, max_size=20)
nonempty_list_nonneg = st.lists(nonneg_floats, min_size=1, max_size=20)



@given(list_floats, list_floats, finite_floats)
def test_shift_risk_raises_on_condition_1(current, target, damping):

    assume(eval('len(current) != len(target)', {"__builtins__": {}}, {"len": len, "sum": sum, "any": any, "all": all, **locals()}))
    with pytest.raises(ValueError) as e:
        prog.shift_risk(current, target, damping=damping)
    _ = e



@given(list_floats, list_floats, finite_floats)
def test_shift_risk_raises_on_condition_2(current, target, damping):
    assume(not (eval('len(current) != len(target)', {"__builtins__": {}}, {"len": len, "sum": sum, "any": any, "all": all, **locals()})))  # avoid earlier guard
    assume(eval('not current', {"__builtins__": {}}, {"len": len, "sum": sum, "any": any, "all": all, **locals()}))
    with pytest.raises(ValueError) as e:
        prog.shift_risk(current, target, damping=damping)
    _ = e

