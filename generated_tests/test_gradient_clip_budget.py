"""Generated Hypothesis tests for `gradient_clip_budget.py`.

This file is auto-generated from `semantics_json_update/gradient_clip_budget.json`.
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


PROGRAM_PATH = Path(__file__).resolve().parents[1] / "python_programs" / "gradient_clip_budget.py"
prog = _load_program("gradient_clip_budget", PROGRAM_PATH)


# Base strategies (kept explicit to match the style of the assignment screenshot)
finite_floats = st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False)
nonneg_floats = st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False)
small_ints = st.integers(min_value=-20, max_value=20)

list_floats = st.lists(finite_floats, min_size=0, max_size=20)
nonempty_list_floats = st.lists(finite_floats, min_size=1, max_size=20)
nonempty_list_nonneg = st.lists(nonneg_floats, min_size=1, max_size=20)



@given(finite_floats, finite_floats)
def test_gradient_clip_budget_raises_on_condition_1(gradients, max_norm):

    assume(eval('max_norm <= 0', {"__builtins__": {}}, {"len": len, "sum": sum, "any": any, "all": all, **locals()}))
    with pytest.raises(ValueError) as e:
        prog.gradient_clip_budget(gradients, max_norm=max_norm)
    _ = e



@given(finite_floats, finite_floats)
def test_gradient_clip_budget_length_preserving_2(gradients, max_norm):
    assume(not (eval('max_norm <= 0', {"__builtins__": {}}, {"len": len, "sum": sum, "any": any, "all": all, **locals()})))
    out = prog.gradient_clip_budget(gradients, max_norm=max_norm)
    assert hasattr(out, "__len__")
    assert len(out) == len(gradients)

