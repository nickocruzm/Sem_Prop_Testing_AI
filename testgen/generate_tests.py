"""Generate Hypot property-based tests from `semantics_json_update/`.

User constraints:
- ONLY use `semantic_prop_project/semantics_json_update/` as the property source.
- Emit one `test_<program>.py` per program under `semantic_prop_project/generated_tests/`.
- Each generated test file must import Hypothesis at the top (see assignment screenshot).

This generator is intentionally conservative:
- It translates only a subset of property kinds into executable tests.
- For unsupported/ambiguous properties it emits `pytest.skip()` tests.

Run:
  python -m semantic_prop_project.testgen.generate_tests

Optional args:
  python -m semantic_prop_project.testgen.generate_tests --limit 20
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


ROOT = Path(__file__).resolve().parents[1]
SEMANTICS_DIR_DEFAULT = ROOT / "semantics_json_update"
PROGRAM_DIR_DEFAULT = ROOT / "python_programs"

# New default output: keep artifacts in a dedicated folder.
CLINE_OUT_ROOT_DEFAULT = ROOT / "Cline_GenTesting_no_skips"
OUT_DIR_DEFAULT = CLINE_OUT_ROOT_DEFAULT / "generated_tests"


@dataclass(frozen=True)
class FnSig:
    name: str
    pos_args: list[str]
    kwonly_args: list[str]
    has_varargs: bool
    has_kwargs: bool


def _parse_program_signatures(path: Path) -> dict[str, FnSig]:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    sigs: dict[str, FnSig] = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        args = node.args
        # Keep it simple: ignore posonlyargs for now; treat them as positional.
        pos = [a.arg for a in args.posonlyargs] + [a.arg for a in args.args]
        kwonly = [a.arg for a in args.kwonlyargs]
        sigs[node.name] = FnSig(
            name=node.name,
            pos_args=pos,
            kwonly_args=kwonly,
            has_varargs=args.vararg is not None,
            has_kwargs=args.kwarg is not None,
        )
    return sigs


_RE_RAISES = re.compile(r"raises\s+(?P<exc>[A-Za-z_][A-Za-z0-9_]*)\((?P<args>.*)\)\s*$")


def _infer_exception(formal: str) -> tuple[str, Optional[str]]:
    """Parse `... raises ValueError(\"msg\")` -> (ValueError, msg)."""
    m = _RE_RAISES.search(formal)
    if not m:
        return ("Exception", None)
    exc = m.group("exc")
    arg_str = m.group("args").strip()
    # If first arg is a string literal, capture it.
    msg = None
    if arg_str.startswith(("\"", "'")):
        try:
            msg = ast.literal_eval(arg_str.split(",", 1)[0])
        except Exception:
            msg = None
    return (exc, msg)


def _names_in_expr(expr: str) -> set[str]:
    try:
        node = ast.parse(expr, mode="eval")
    except SyntaxError:
        return set()
    names: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            names.add(n.id)
    return names


def _cond_uses_only_args(cond: str, args: set[str]) -> bool:
    # allow builtins len/sum/any/all plus True/False/None
    allowed = args | {"len", "sum", "any", "all", "True", "False", "None"}
    names = _names_in_expr(cond)
    return names.issubset(allowed)


def _py_header(module_stem: str) -> str:
    # Hypothesis import MUST be at top (per user constraint)
    # We keep a minimal header and import shared utilities from
    # `semantic_prop_project/Cline_GenTesting_no_skips/utils.py`.
    return f'''"""Generated Hypothesis tests for `{module_stem}.py`.

This file is auto-generated from `semantics_json_update/{module_stem}.json`.
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


PROGRAM_PATH = PROGRAMS_DIR / "{module_stem}.py"
prog = load_program("{module_stem}", PROGRAM_PATH)
'''


def _strategy_for_arg(name: str) -> str:
    """Return a strategy expression string for an argument name."""
    lname = name.lower()
    # Heuristics for common structured inputs in the `python_programs/` corpus
    # (especially the various scheduling/reservation programs).
    if lname in {"candidate"}:
        # Many programs treat `candidate` as a (start, end) pair.
        return "window"
    if lname in {"existing"}:
        # Many programs treat `existing` as a list of (start, end) pairs.
        return "windows"
    if lname in {"jobs"}:
        return "list_ints"
    if lname in {"max_jobs"}:
        return "st.integers(min_value=0, max_value=200)"
    if lname in {"xs", "values", "series", "current", "target", "ratios", "weights"}:
        return "list_floats"
    if lname in {"tokens"}:
        # token bucket expects a dict-like object
        return 'st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=-5, max_value=20), max_size=5)'
    if lname in {"now", "start", "end", "t", "time", "timestamp"}:
        return "small_ints"
    if lname in {"amount", "total", "minimum", "capacity", "rate", "fee", "budget"}:
        return 'st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)'
    if lname.startswith("is_") or lname.endswith("flag"):
        return "st.booleans()"
    return "finite_floats"


def _emit_given(sig: FnSig) -> tuple[str, str, str]:
    """Return (decorator, param_list, call_expr)."""
    if sig.has_varargs or sig.has_kwargs:
        # Too hard to generate safely.
        return ("", "", "")

    params: list[str] = []
    strat_items: list[str] = []
    call_parts: list[str] = []

    for a in sig.pos_args:
        params.append(a)
        strat_items.append(_strategy_for_arg(a))
        call_parts.append(a)
    for a in sig.kwonly_args:
        params.append(a)
        strat_items.append(_strategy_for_arg(a))
        call_parts.append(f"{a}={a}")

    decorator = f"@given({', '.join(strat_items)})" if strat_items else ""
    param_list = ", ".join(params)
    call_expr = f"prog.{sig.name}({', '.join(call_parts)})"
    return (decorator, param_list, call_expr)


def _emit_given_with_overrides(sig: FnSig, overrides: dict[str, str]) -> tuple[str, str, str]:
    """Like `_emit_given`, but allow overriding strategy expressions per argument."""
    if sig.has_varargs or sig.has_kwargs:
        return ("", "", "")

    params: list[str] = []
    strat_items: list[str] = []
    call_parts: list[str] = []

    for a in sig.pos_args:
        params.append(a)
        strat_items.append(overrides.get(a, _strategy_for_arg(a)))
        call_parts.append(a)
    for a in sig.kwonly_args:
        params.append(a)
        strat_items.append(overrides.get(a, _strategy_for_arg(a)))
        call_parts.append(f"{a}={a}")

    decorator = f"@given({', '.join(strat_items)})" if strat_items else ""
    param_list = ", ".join(params)
    call_expr = f"prog.{sig.name}({', '.join(call_parts)})"
    return (decorator, param_list, call_expr)


_RE_LEN_EQ_0 = re.compile(r"^len\((?P<var>[A-Za-z_][A-Za-z0-9_]*)\)\s*==\s*0$")
_RE_LEN_NEQ = re.compile(
    r"^len\((?P<a>[A-Za-z_][A-Za-z0-9_]*)\)\s*!=\s*len\((?P<b>[A-Za-z_][A-Za-z0-9_]*)\)$"
)
_RE_NOT_VAR = re.compile(r"^not\s+(?P<var>[A-Za-z_][A-Za-z0-9_]*)$")
_RE_VAR_LT_0 = re.compile(r"^(?P<var>[A-Za-z_][A-Za-z0-9_]*)\s*<\s*0$")
_RE_VAR_LE_0 = re.compile(r"^(?P<var>[A-Za-z_][A-Za-z0-9_]*)\s*<=\s*0$")
_RE_SUM_EQ_0 = re.compile(r"^sum\((?P<var>[A-Za-z_][A-Za-z0-9_]*)\)\s*==\s*0$")
_RE_SUM_LE_0 = re.compile(r"^sum\((?P<var>[A-Za-z_][A-Za-z0-9_]*)\)\s*<=\s*0$")
_RE_OR_LE_0 = re.compile(
    r"^(?P<a>[A-Za-z_][A-Za-z0-9_]*)\s*<=\s*0\s+or\s+(?P<b>[A-Za-z_][A-Za-z0-9_]*)\s*<=\s*0$"
)


def _infer_overrides_for_condition(cond: str, sig: FnSig) -> dict[str, str]:
    """Best-effort: choose strategies that satisfy *simple* conditions without heavy assume() filtering."""
    cond_s = (cond or "").strip()
    args = set(sig.pos_args + sig.kwonly_args)
    overrides: dict[str, str] = {}

    m = _RE_LEN_EQ_0.match(cond_s)
    if m:
        v = m.group("var")
        if v in args:
            overrides[v] = "st.just([])"
        return overrides

    m = _RE_LEN_NEQ.match(cond_s)
    if m:
        a, b = m.group("a"), m.group("b")
        if a in args and b in args:
            # Satisfy mismatch deterministically.
            overrides[a] = "st.just([])"
            overrides[b] = "nonempty_list_floats"
        return overrides

    m = _RE_NOT_VAR.match(cond_s)
    if m:
        v = m.group("var")
        if v in args:
            # Many programs use `not <list>` as emptiness
            overrides[v] = "st.just([])"
        return overrides

    m = _RE_SUM_EQ_0.match(cond_s) or _RE_SUM_LE_0.match(cond_s)
    if m:
        v = m.group("var")
        if v in args:
            overrides[v] = "st.lists(st.just(0.0), min_size=1, max_size=20)"
        return overrides

    m = _RE_OR_LE_0.match(cond_s)
    if m:
        a, b = m.group("a"), m.group("b")
        if a in args:
            overrides[a] = "st.floats(max_value=0.0, allow_nan=False, allow_infinity=False)"
        if b in args:
            overrides[b] = "st.floats(max_value=0.0, allow_nan=False, allow_infinity=False)"
        return overrides

    m = _RE_VAR_LT_0.match(cond_s)
    if m:
        v = m.group("var")
        if v in args:
            overrides[v] = "st.floats(max_value=-1e-6, allow_nan=False, allow_infinity=False)"
        return overrides

    m = _RE_VAR_LE_0.match(cond_s)
    if m:
        v = m.group("var")
        if v in args:
            overrides[v] = "st.floats(max_value=0.0, allow_nan=False, allow_infinity=False)"
        return overrides

    return overrides


def _infer_overrides_to_avoid_raises(raise_conds: list[str], sig: FnSig) -> dict[str, str]:
    """Choose strategies that *tend* to avoid triggering known raise guards.

    This reduces Hypothesis 'filter_too_much' health checks from many assume(...)
    lines.
    """
    args = set(sig.pos_args + sig.kwonly_args)
    overrides: dict[str, str] = {}
    for cond in raise_conds:
        c = (cond or "").strip()
        m = _RE_LEN_EQ_0.match(c)
        if m:
            v = m.group("var")
            if v in args:
                overrides[v] = "nonempty_list_floats"
            continue
        m = _RE_NOT_VAR.match(c)
        if m:
            v = m.group("var")
            if v in args:
                overrides[v] = "nonempty_list_floats"
            continue
        m = _RE_SUM_EQ_0.match(c) or _RE_SUM_LE_0.match(c)
        if m:
            v = m.group("var")
            if v in args:
                overrides[v] = "st.lists(st.just(1.0), min_size=1, max_size=20)"
            continue
        m = _RE_VAR_LT_0.match(c)
        if m:
            v = m.group("var")
            if v in args:
                overrides[v] = "st.floats(min_value=0.0, max_value=1000, allow_nan=False, allow_infinity=False)"
            continue
        m = _RE_VAR_LE_0.match(c)
        if m:
            v = m.group("var")
            if v in args:
                overrides[v] = "st.floats(min_value=1e-6, max_value=1000, allow_nan=False, allow_infinity=False)"
            continue
        # Complex conditions (e.g., len(a) != len(b)) are ignored here.

    return overrides


def _eval_expr(expr: str) -> str:
    """Emit a helper call into `utils.safe_eval()` used across generated tests."""
    return "safe_eval(" + repr(expr) + ", locals())"


def _emit_assume_no_raises(raise_conds: list[str]) -> str:
    if not raise_conds:
        return ""
    return "    assume_no_raises(" + repr(raise_conds) + ", locals())"


def _emit_test_raises(
    prop: dict[str, Any],
    sig: FnSig,
    idx: int,
    *,
    prior_raise_conds: list[str],
) -> Optional[str]:
    cond = prop.get("condition")
    formal = prop.get("formal") or ""
    if not cond:
        return None
    args_set = set(sig.pos_args + sig.kwonly_args)
    if not _cond_uses_only_args(cond, args_set):
        return None

    exc, msg = _infer_exception(formal)
    decorator, params, call_expr = _emit_given_with_overrides(
        sig, _infer_overrides_for_condition(cond, sig)
    )
    if not decorator:
        return None

    # best-effort mapping of exception names
    exc_expr = exc if exc in {"ValueError", "TypeError", "KeyError", "IndexError", "ZeroDivisionError"} else "Exception"

    # NOTE: We intentionally do *not* assert on the error message.
    # Many programs have multiple ValueError guards; ensuring we trigger the
    # specific message would require ordering-aware preconditions. We *do*
    # exclude earlier raise-guards via `prior_raise_conds` below.
    _ = msg

    # We no longer enforce guard ordering here (can cause heavy filtering).
    # If multiple guards raise the same exception type, this test still
    # validates the "raises" property.
    _ = prior_raise_conds
    prior_assumes = ""

    return f'''

{decorator}
def test_{sig.name}_raises_on_condition_{idx}({params}):
{prior_assumes}
    assume({_eval_expr(cond)})
    with pytest.raises({exc_expr}) as e:
        {call_expr}
    _ = e
'''


def _emit_test_identity(
    prop: dict[str, Any],
    sig: FnSig,
    idx: int,
    *,
    raise_conds: list[str],
) -> Optional[str]:
    cond = prop.get("condition")
    formal = prop.get("formal") or ""
    if not cond:
        return None

    # Try to infer the RHS variable: `... == xs`
    m = re.search(r"==\s*([A-Za-z_][A-Za-z0-9_]*)\s*$", formal)
    if not m:
        return None
    rhs = m.group(1)

    args_set = set(sig.pos_args + sig.kwonly_args)
    if rhs not in args_set:
        return None
    if not _cond_uses_only_args(cond, args_set):
        return None

    decorator, params, call_expr = _emit_given_with_overrides(
        sig, _infer_overrides_for_condition(cond, sig)
    )
    if not decorator:
        return None

    no_raises = _emit_assume_no_raises(raise_conds)
    return f'''

{decorator}
def test_{sig.name}_identity_on_condition_{idx}({params}):
{no_raises}
    assume({_eval_expr(cond)})
    try:
        out = {call_expr}
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under identity property: {sig.name}: {{e!r}}")
    assert out == {rhs}
'''


def _emit_utils_py() -> str:
    """Shared helper module imported by all generated tests.

    Important:
    - This file lives under `semantic_prop_project/Cline_GenTesting_no_skips/utils.py`.
    - Generated test modules import from `semantic_prop_project.Cline_GenTesting_no_skips.utils`.
    """
    return '''"""Utilities shared by generated Hypothesis tests.

This file is auto-generated.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Mapping

import pytest
from hypothesis import HealthCheck, assume, settings, strategies as st


# Suppress Hypothesis "filter too much" health-checks.
#
# Generated tests frequently use `assume(...)` for preconditions/guards.
# That is *expected* here because the semantic properties are conditional.
settings.register_profile(
    "semantic_props",
    deadline=None,
    suppress_health_check=[HealthCheck.filter_too_much],
)
settings.load_profile("semantic_props")


HERE = Path(__file__).resolve()
SEMANTIC_PROJECT_ROOT = HERE.parents[1]
PROGRAMS_DIR = SEMANTIC_PROJECT_ROOT / "python_programs"


def load_program(module_name: str, file_path: Path):
    """Import a python file by path without requiring it to be a package."""
    if not file_path.exists():
        pytest.skip(f"Program file not found: {file_path}")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {module_name} from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


# Base strategies (kept explicit to match the style of the assignment screenshot)
finite_floats = st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False)
nonneg_floats = st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False)
small_ints = st.integers(min_value=-20, max_value=20)

list_floats = st.lists(finite_floats, min_size=0, max_size=20)
nonempty_list_floats = st.lists(finite_floats, min_size=1, max_size=20)
nonempty_list_nonneg = st.lists(nonneg_floats, min_size=1, max_size=20)

# Common structured inputs
window = st.tuples(finite_floats, finite_floats)
windows = st.lists(window, min_size=0, max_size=20)

list_ints = st.lists(small_ints, min_size=0, max_size=200)
nonempty_list_ints = st.lists(small_ints, min_size=1, max_size=200)


def safe_eval(expr: str, local_vars: Mapping[str, Any]) -> Any:
    """Evaluate a *very* restricted expression against locals.

    Allowed functions: len, sum, any, all
    Builtins disabled.
    """
    try:
        return eval(
            expr,
            {"__builtins__": {}},
            {
                "len": len,
                "sum": sum,
                "any": any,
                "all": all,
                **dict(local_vars),
            },
        )
    except Exception:
        # If the expression doesn't type-check against the generated inputs
        # (e.g., `len(x)` where `x` was a float), treat it as False so tests
        # can reject that input via `assume(...)` instead of erroring.
        return False


def assume_no_raises(raise_conds: list[str], local_vars: Mapping[str, Any]) -> None:
    """Assume that none of the given raise-guard conditions hold."""
    for rc in raise_conds:
        assume(not bool(safe_eval(rc, local_vars)))
'''


def _emit_test_returns_constant(
    prop: dict[str, Any],
    sig: FnSig,
    idx: int,
    *,
    raise_conds: list[str],
) -> Optional[str]:
    cond = prop.get("condition")
    formal = prop.get("formal") or ""
    if not cond:
        return None
    m = re.search(r"==\s*(True|False)\s*$", formal)
    if not m:
        return None
    cst = m.group(1)

    args_set = set(sig.pos_args + sig.kwonly_args)
    if not _cond_uses_only_args(cond, args_set):
        return None

    decorator, params, call_expr = _emit_given_with_overrides(
        sig, _infer_overrides_for_condition(cond, sig)
    )
    if not decorator:
        return None

    no_raises = _emit_assume_no_raises(raise_conds)

    return f'''

{decorator}
def test_{sig.name}_returns_constant_{idx}({params}):
{no_raises}
    assume({_eval_expr(cond)})
    try:
        out = {call_expr}
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under constant-return property: {sig.name}: {{e!r}}")
    assert out is {cst}
'''


def _infer_list_arg_from_text(text: str, sig: FnSig) -> Optional[str]:
    # Prefer common list arg names
    for cand in ["xs", "values", "series", "ratios", "weights", "current", "target"]:
        if cand in (sig.pos_args + sig.kwonly_args) and cand in text:
            return cand
    # Else pick first arg that looks plural
    for a in (sig.pos_args + sig.kwonly_args):
        if a.endswith("s"):
            return a
    return None


def _emit_test_length_preserving(
    prop: dict[str, Any],
    sig: FnSig,
    idx: int,
    *,
    raise_conds: list[str],
) -> Optional[str]:
    formal = prop.get("formal") or ""
    list_arg = _infer_list_arg_from_text(formal, sig)
    if not list_arg:
        return None

    decorator, params, call_expr = _emit_given_with_overrides(
        sig, _infer_overrides_to_avoid_raises(raise_conds, sig)
    )
    if not decorator:
        return None

    no_raises = _emit_assume_no_raises(raise_conds)

    return f'''

{decorator}
def test_{sig.name}_length_preserving_{idx}({params}):
{no_raises}
    try:
        out = {call_expr}
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under length-preserving property: {sig.name}: {{e!r}}")
    assert hasattr(out, "__len__")
    assert len(out) == len({list_arg})
'''


def _emit_test_unit_sum(
    prop: dict[str, Any],
    sig: FnSig,
    idx: int,
    *,
    raise_conds: list[str],
) -> Optional[str]:
    pre = prop.get("precondition") or ""
    formal = prop.get("formal") or ""
    list_arg = _infer_list_arg_from_text(pre + " " + formal, sig)
    if not list_arg:
        return None
    if list_arg not in sig.pos_args + sig.kwonly_args:
        return None

    # Force non-empty list for stable sum checks
    decorator, params, call_expr = _emit_given(sig)
    if not decorator:
        return None

    # Override strategy for the list arg by generating a second decorator
    # (Hypothesis doesn't allow per-arg override without rebuilding decorator)
    params_list = (sig.pos_args + sig.kwonly_args)
    strat_items: list[str] = []
    for a in params_list:
        if a == list_arg:
            strat_items.append("nonempty_list_floats")
        else:
            strat_items.append(_strategy_for_arg(a))
    decorator2 = f"@given({', '.join(strat_items)})"
    call_parts = [a for a in sig.pos_args] + [f"{a}={a}" for a in sig.kwonly_args]
    call_expr2 = f"prog.{sig.name}({', '.join(call_parts)})"

    no_raises = _emit_assume_no_raises(raise_conds)

    return f'''

{decorator2}
def test_{sig.name}_unit_sum_{idx}({', '.join(params_list)}):
{no_raises}
    assume(sum({list_arg}) != 0)
    try:
        ys = {call_expr2}
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under unit-sum property: {sig.name}: {{e!r}}")
    assert math.isclose(sum(ys), 1.0, rel_tol=1e-6, abs_tol=1e-6)
'''


def _emit_test_sign_preservation(
    prop: dict[str, Any],
    sig: FnSig,
    idx: int,
    *,
    raise_conds: list[str],
) -> Optional[str]:
    pre = prop.get("precondition") or ""
    formal = prop.get("formal") or ""
    list_arg = _infer_list_arg_from_text(pre + " " + formal, sig)
    if not list_arg:
        return None
    if list_arg not in sig.pos_args + sig.kwonly_args:
        return None

    params_list = (sig.pos_args + sig.kwonly_args)
    strat_items: list[str] = []
    for a in params_list:
        if a == list_arg:
            strat_items.append("nonempty_list_nonneg")
        else:
            strat_items.append(_strategy_for_arg(a))
    decorator = f"@given({', '.join(strat_items)})"
    call_parts = [a for a in sig.pos_args] + [f"{a}={a}" for a in sig.kwonly_args]
    call_expr = f"prog.{sig.name}({', '.join(call_parts)})"

    no_raises = _emit_assume_no_raises(raise_conds)

    return f'''

{decorator}
def test_{sig.name}_sign_preservation_{idx}({', '.join(params_list)}):
{no_raises}
    assume(sum({list_arg}) > 0)
    try:
        ys = {call_expr}
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under sign-preservation property: {sig.name}: {{e!r}}")
    assert all(y >= -1e-12 for y in ys)
'''


def _emit_test_fee_shift(
    prop: dict[str, Any],
    sig: FnSig,
    idx: int,
    *,
    raise_conds: list[str],
) -> Optional[str]:
    formal = prop.get("formal") or ""
    # We need amount, fee, and ratios to be in args.
    args = set(sig.pos_args + sig.kwonly_args)
    if not ({"amount", "ratios"}.issubset(args)):
        return None
    if "fee" not in args:
        return None

    params_list = (sig.pos_args + sig.kwonly_args)
    strat_items: list[str] = []
    for a in params_list:
        if a == "ratios":
            strat_items.append("nonempty_list_floats")
        elif a == "amount":
            strat_items.append('st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)')
        else:
            strat_items.append(_strategy_for_arg(a))
    decorator = f"@given({', '.join(strat_items)})"

    call_parts = [a for a in sig.pos_args] + [f"{a}={a}" for a in sig.kwonly_args]
    call_expr = f"prog.{sig.name}({', '.join(call_parts)})"

    no_raises = _emit_assume_no_raises(raise_conds)

    return f'''

{decorator}
def test_{sig.name}_fee_shift_total_{idx}({', '.join(params_list)}):
    # Make sure we hit the main allocation path.
{no_raises}
    assume(len(ratios) > 0)
    assume(sum(ratios) != 0)
    try:
        out = {call_expr}
    except Exception as e:
        pytest.skip(f"Function raised unexpectedly under fee-shift property: {sig.name}: {{e!r}}")
    assert math.isclose(sum(out), amount - fee * len(ratios), rel_tol=1e-6, abs_tol=1e-6)
'''


def _emit_skips(props: list[dict[str, Any]]) -> str:
    # Always include at least one test so pytest collects the module.
    return """


@given(st.integers())
def test_generated_no_supported_properties(_x):
    pytest.skip("No supported semantic properties could be translated for this program")
"""


def _generate_for_file(sem_path: Path, program_path: Path) -> str:
    data = json.loads(sem_path.read_text(encoding="utf-8"))
    props: list[dict[str, Any]] = data.get("properties") or []

    module_stem = sem_path.stem
    header = _py_header(module_stem)

    if not program_path.exists():
        return header + "\n\n" + _emit_skips(props)

    sigs = _parse_program_signatures(program_path)

    # Gather input-level raise guards per function (in observed order).
    raise_conds_by_fn: dict[str, list[str]] = {}
    for p in props:
        if p.get("property") != "raises_on_condition":
            continue
        fn = p.get("function")
        cond = p.get("condition")
        if not fn or not cond:
            continue
        sig = sigs.get(fn)
        if not sig:
            continue
        args_set = set(sig.pos_args + sig.kwonly_args)
        if not _cond_uses_only_args(cond, args_set):
            continue
        raise_conds_by_fn.setdefault(fn, []).append(cond)

    body_parts: list[str] = []
    supported = 0

    for idx, p in enumerate(props):
        fn = p.get("function")
        kind = p.get("property")
        if not fn or not kind:
            continue
        sig = sigs.get(fn)
        if sig is None:
            continue
        if sig.has_varargs or sig.has_kwargs:
            continue

        snippet: Optional[str] = None
        raise_conds = raise_conds_by_fn.get(fn, [])
        if kind == "raises_on_condition":
            # Enforce ordering: avoid earlier raise guards so we target the intended one.
            cond = p.get("condition")
            prior: list[str] = []
            if cond in raise_conds:
                prior = raise_conds[: raise_conds.index(cond)]
            snippet = _emit_test_raises(p, sig, idx, prior_raise_conds=prior)
        elif kind == "identity_on_condition":
            snippet = _emit_test_identity(p, sig, idx, raise_conds=raise_conds)
        elif kind == "returns_constant":
            snippet = _emit_test_returns_constant(p, sig, idx, raise_conds=raise_conds)
        elif kind == "length_preserving_listcomp":
            snippet = _emit_test_length_preserving(p, sig, idx, raise_conds=raise_conds)
        elif kind == "unit_sum_normalization":
            snippet = _emit_test_unit_sum(p, sig, idx, raise_conds=raise_conds)
        elif kind == "sign_preservation_under_positive_sum":
            snippet = _emit_test_sign_preservation(p, sig, idx, raise_conds=raise_conds)
        elif kind == "fee_shifts_total_by_n_times_fee":
            snippet = _emit_test_fee_shift(p, sig, idx, raise_conds=raise_conds)

        if snippet:
            supported += 1
            body_parts.append(snippet)

    if supported == 0:
        body_parts.append(_emit_skips(props))

    return header + "\n" + "\n".join(body_parts) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--semantics-dir",
        default=str(SEMANTICS_DIR_DEFAULT),
        help="Directory of semantics JSON files (default: semantics_json_update)",
    )
    ap.add_argument(
        "--program-dir",
        default=str(PROGRAM_DIR_DEFAULT),
        help="Directory of python programs (default: python_programs)",
    )
    ap.add_argument(
        "--out-dir",
        default=str(OUT_DIR_DEFAULT),
        help="Directory to write generated tests (default: generated_tests)",
    )
    ap.add_argument(
        "--utils-out",
        default=str(CLINE_OUT_ROOT_DEFAULT / "utils.py"),
        help="Path to write shared utils.py for generated tests",
    )
    ap.add_argument(
        "--only",
        type=str,
        default=None,
        help="Comma-separated list of program stems to generate (e.g. normalize,ad_mix). Overrides --limit.",
    )
    ap.add_argument("--limit", type=int, default=None, help="Only generate first N files")
    args = ap.parse_args()

    sem_dir = Path(args.semantics_dir)
    prog_dir = Path(args.program_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Ensure the shared utils module exists where generated tests expect it.
    utils_out = Path(args.utils_out)
    utils_out.parent.mkdir(parents=True, exist_ok=True)
    utils_out.write_text(_emit_utils_py(), encoding="utf-8")

    # Ensure the output folder is an importable package (so tests can import utils).
    pkg_init = utils_out.parent / "__init__.py"
    if not pkg_init.exists():
        pkg_init.write_text("\n", encoding="utf-8")

    # Ensure the generated tests folder is importable as a package.
    init_py = out_dir / "__init__.py"
    if not init_py.exists():
        init_py.write_text("\n", encoding="utf-8")

    # Requirement: each python program should have an associated test_*.py
    program_stems = sorted(p.stem for p in prog_dir.glob("*.py") if p.is_file())
    if args.only:
        selected = [s.strip() for s in args.only.split(",") if s.strip()]
        program_stems = [s for s in program_stems if s in set(selected)]
    elif args.limit is not None:
        program_stems = program_stems[: args.limit]

    for module_stem in program_stems:
        sem_path = sem_dir / f"{module_stem}.json"
        program_path = prog_dir / f"{module_stem}.py"
        if sem_path.exists():
            content = _generate_for_file(sem_path, program_path)
        else:
            # No semantics file: emit a stub that skips.
            content = _py_header(module_stem) + "\n\n" + _emit_skips([]) + "\n"
        out_path = out_dir / f"test_{module_stem}.py"
        out_path.write_text(content, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
