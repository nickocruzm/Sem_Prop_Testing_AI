"""AST-based *semantic property* extractor.

This script derives lightweight semantic properties aligned with the code's
structure for each Python file under an input directory.

It is intentionally heuristic (not a full verifier). It focuses on common
micro-program patterns found in `semantic_prop_project/python_programs`, such as:

- input validation (raise ValueError under a guard)
- early return behaviors (identity / constant return)
- list-comprehension map/filter properties (length preservation / subset)
- simple budget/allocation invariants (ratio normalization, sum preservation)
- token bucket / limiter style pre/post conditions

Output:
For each `<name>.py`, write `semantics_json/<name>.json` containing an array of
JSON objects, each describing one semantic property.
"""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


def _safe_unparse(node: Optional[ast.AST], source: str) -> Optional[str]:
    if node is None:
        return None
    seg = ast.get_source_segment(source, node)
    if seg is not None:
        return seg.strip()
    try:
        return ast.unparse(node).strip()  # type: ignore[attr-defined]
    except Exception:
        return node.__class__.__name__


def _attach_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "parent", parent)


def _is_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


def _is_call_to(node: ast.AST, func_name: str) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == func_name
    )


def _literal_bool(node: ast.AST) -> Optional[bool]:
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return bool(node.value)
    return None


def _iter_name_from_comp(comp: ast.ListComp) -> Optional[str]:
    if len(comp.generators) != 1:
        return None
    gen = comp.generators[0]
    if isinstance(gen.iter, ast.Name):
        return gen.iter.id
    return None


def _target_name_from_comp(comp: ast.ListComp) -> Optional[str]:
    if len(comp.generators) != 1:
        return None
    gen = comp.generators[0]
    if isinstance(gen.target, ast.Name):
        return gen.target.id
    return None


def _ifs_from_comp(comp: ast.ListComp, source: str) -> list[str]:
    if len(comp.generators) != 1:
        return []
    gen = comp.generators[0]
    return [(_safe_unparse(i, source) or "<cond>") for i in gen.ifs]


@dataclass
class FuncCtx:
    file: str
    function: str
    args: list[str]
    source: str


class SemanticExtractor(ast.NodeVisitor):
    def __init__(self, *, filename: str, source: str):
        self.filename = filename
        self.source = source
        self.items: list[dict[str, Any]] = []
        self._function_stack: list[FuncCtx] = []

        # Per-function scratch (rebuilt on entry)
        self._assignments: dict[str, ast.AST] = {}

    def _add(self, obj: dict[str, Any]) -> None:
        obj.setdefault("file", self.filename)
        self.items.append(obj)

    def _ctx(self) -> FuncCtx:
        return self._function_stack[-1]

    # ---- Function entry/exit ----

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        args = [a.arg for a in node.args.args]
        ctx = FuncCtx(
            file=self.filename,
            function=node.name,
            args=args,
            source=self.source,
        )
        self._function_stack.append(ctx)
        self._assignments = {}

        # basic totality/definition property
        self._add(
            {
                "scope": "function",
                "function": node.name,
                "property": "defines_function",
                "element": node.name,
                "formal": f"{node.name}({', '.join(args)}) is defined",
            }
        )

        # pre-scan assignments at top-level of function body (simple)
        for st in node.body:
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
                self._assignments[st.targets[0].id] = st.value

        # Continue into body
        for st in node.body:
            self.visit(st)

        # Post-pass: infer properties from final returns
        self._infer_from_returns(node)
        self._function_stack.pop()

    # ---- Guard / validation properties ----

    def visit_If(self, node: ast.If) -> Any:
        ctx = self._ctx()
        cond = _safe_unparse(node.test, ctx.source) or "<cond>"

        # input validation pattern: if <cond>: raise <Exc>(...)
        if node.body and isinstance(node.body[0], ast.Raise):
            exc = node.body[0].exc
            exc_name = _safe_unparse(exc, ctx.source) or "<exception>"
            self._add(
                {
                    "scope": "branch",
                    "function": ctx.function,
                    "element": ctx.function,
                    "condition": cond,
                    "property": "raises_on_condition",
                    "formal": f"if {cond} then raises {exc_name}",
                }
            )

        # constant/identity return under guard
        for st in node.body:
            if isinstance(st, ast.Return) and st.value is not None:
                b = _literal_bool(st.value)
                if b is not None:
                    self._add(
                        {
                            "scope": "branch",
                            "function": ctx.function,
                            "element": ctx.function,
                            "condition": cond,
                            "property": "returns_constant",
                            "formal": f"if {cond} then {ctx.function}(...) == {b}",
                        }
                    )
                elif isinstance(st.value, ast.Name) and st.value.id in ctx.args:
                    self._add(
                        {
                            "scope": "branch",
                            "function": ctx.function,
                            "element": ctx.function,
                            "condition": cond,
                            "property": "identity_on_condition",
                            "formal": f"if {cond} then {ctx.function}(...) == {st.value.id}",
                        }
                    )

        # recurse
        for st in node.body:
            self.visit(st)
        for st in node.orelse:
            self.visit(st)

    # ---- Track assignments (for later inference) ----

    def visit_Assign(self, node: ast.Assign) -> Any:
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            self._assignments[node.targets[0].id] = node.value
        self.generic_visit(node)

    # ---- Return-based inference ----

    def _infer_from_returns(self, fn: ast.FunctionDef) -> None:
        """Infer higher-level semantics from return expressions."""
        ctx = self._ctx()

        returns: list[ast.Return] = [n for n in ast.walk(fn) if isinstance(n, ast.Return)]
        for ret in returns:
            if ret.value is None:
                continue

            # list-comprehension map/filter properties
            if isinstance(ret.value, ast.ListComp):
                comp = ret.value
                it = _iter_name_from_comp(comp)
                if it is not None:
                    ifs = _ifs_from_comp(comp, ctx.source)

                    if not ifs:
                        self._add(
                            {
                                "scope": "function",
                                "function": ctx.function,
                                "element": ctx.function,
                                "property": "length_preserving_listcomp",
                                "precondition": None,
                                "formal": f"len({ctx.function}(...)) == len({it})",
                            }
                        )
                    else:
                        joined = " and ".join(ifs)
                        self._add(
                            {
                                "scope": "function",
                                "function": ctx.function,
                                "element": ctx.function,
                                "property": "filtered_subset_listcomp",
                                "precondition": None,
                                "formal": (
                                    f"forall y in {ctx.function}(...): y in {it} and ({joined})"
                                ),
                            }
                        )
                        self._add(
                            {
                                "scope": "function",
                                "function": ctx.function,
                                "element": ctx.function,
                                "property": "filtered_length_upper_bound",
                                "precondition": None,
                                "formal": f"len({ctx.function}(...)) <= len({it})",
                            }
                        )

                # Detect normalization: s = sum(xs), return [x/s for x in xs]
                self._infer_normalization(comp)

            # tuple return often encodes (allowed, remaining)
            if isinstance(ret.value, ast.Tuple) and len(ret.value.elts) == 2:
                a, b = ret.value.elts
                a_bool = _literal_bool(a)
                if a_bool is not None:
                    self._add(
                        {
                            "scope": "branch" if self._is_guarded_return(ret) else "function",
                            "function": ctx.function,
                            "element": ctx.function,
                            "property": "returns_status_tuple",
                            "precondition": None,
                            "formal": f"{ctx.function}(...) returns ({a_bool}, {_safe_unparse(b, ctx.source)})",
                        }
                    )

        # Detect ratio allocation patterns (shares built from ratios)
        self._infer_ratio_allocation(fn)

        # Detect token bucket style state update (tokens dict)
        self._infer_token_bucket(fn)

    def _is_guarded_return(self, ret: ast.Return) -> bool:
        parent = getattr(ret, "parent", None)
        # If return is inside If/For/While/Try etc treat as branch-level
        return isinstance(parent, (ast.If, ast.For, ast.While, ast.Try, ast.With))

    def _infer_normalization(self, comp: ast.ListComp) -> None:
        ctx = self._ctx()
        it = _iter_name_from_comp(comp)
        if it is None:
            return
        target = _target_name_from_comp(comp)
        if target is None:
            return

        # elt looks like: x / s
        elt = comp.elt
        if not (
            isinstance(elt, ast.BinOp)
            and isinstance(elt.op, ast.Div)
            and _is_name(elt.left, target)
            and isinstance(elt.right, ast.Name)
        ):
            return

        denom = elt.right.id
        denom_src = denom

        # denom assigned from sum(it)? (s = sum(xs))
        rhs = self._assignments.get(denom)
        if rhs is None or not _is_call_to(rhs, "sum"):
            return
        if len(rhs.args) != 1 or not _is_name(rhs.args[0], it):
            return

        self._add(
            {
                "scope": "function",
                "function": ctx.function,
                "element": ctx.function,
                "property": "unit_sum_normalization",
                "precondition": f"sum({it}) != 0",
                "formal": f"sum({ctx.function}({it})) == 1",
            }
        )

        # non-negativity preservation is common if xs nonnegative
        self._add(
            {
                "scope": "function",
                "function": ctx.function,
                "element": ctx.function,
                "property": "sign_preservation_under_positive_sum",
                "precondition": f"forall x in {it}: x >= 0 and sum({it}) > 0",
                "formal": f"forall y in {ctx.function}({it}): y >= 0",
            }
        )

    def _infer_ratio_allocation(self, fn: ast.FunctionDef) -> None:
        ctx = self._ctx()
        # Look for total_ratio = sum(ratios)
        total_ratio_name: Optional[str] = None
        ratios_name: Optional[str] = None
        for name, rhs in self._assignments.items():
            if _is_call_to(rhs, "sum") and len(rhs.args) == 1 and isinstance(rhs.args[0], ast.Name):
                total_ratio_name = name
                ratios_name = rhs.args[0].id
                break
        if total_ratio_name is None or ratios_name is None:
            return

        # Find `shares = []` and `for r in ratios: shares.append((r/total_ratio)*amount)`
        shares_name: Optional[str] = None
        for st in fn.body:
            if (
                isinstance(st, ast.Assign)
                and len(st.targets) == 1
                and isinstance(st.targets[0], ast.Name)
                and isinstance(st.value, ast.List)
                and len(st.value.elts) == 0
            ):
                shares_name = st.targets[0].id
                break
        if shares_name is None:
            return

        # Try to identify loop appending per ratio
        loop_ok = False
        amount_name: Optional[str] = None
        for st in fn.body:
            if not isinstance(st, ast.For):
                continue
            if not _is_name(st.iter, ratios_name):
                continue
            if not isinstance(st.target, ast.Name):
                continue
            rname = st.target.id
            # find shares.append(<expr>)
            for bst in st.body:
                if not (
                    isinstance(bst, ast.Expr)
                    and isinstance(bst.value, ast.Call)
                    and isinstance(bst.value.func, ast.Attribute)
                    and isinstance(bst.value.func.value, ast.Name)
                    and bst.value.func.value.id == shares_name
                    and bst.value.func.attr == "append"
                    and len(bst.value.args) == 1
                ):
                    continue
                expr = bst.value.args[0]
                # match (r / total_ratio) * amount (some parenthesization)
                if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Mult):
                    # (r/total_ratio) * amount
                    left, right = expr.left, expr.right
                    if isinstance(left, ast.BinOp) and isinstance(left.op, ast.Div):
                        if _is_name(left.left, rname) and _is_name(left.right, total_ratio_name) and isinstance(right, ast.Name):
                            amount_name = right.id
                            loop_ok = True
                if loop_ok:
                    break
            if loop_ok:
                break
        if not loop_ok or amount_name is None:
            return

        self._add(
            {
                "scope": "function",
                "function": ctx.function,
                "element": ctx.function,
                "property": "allocation_length_matches_ratios",
                "precondition": None,
                "formal": f"len({shares_name}) == len({ratios_name})",
            }
        )

        self._add(
            {
                "scope": "function",
                "function": ctx.function,
                "element": ctx.function,
                "property": "ratio_allocation_sum_preserved_pre_fee",
                "precondition": f"sum({ratios_name}) != 0",
                "formal": f"sum({shares_name}) == {amount_name}",
            }
        )

        # If final return is `[s - fee for s in shares]`, infer sum shift by fee
        fee_name: Optional[str] = None
        for st in fn.body:
            if isinstance(st, ast.Return) and isinstance(st.value, ast.ListComp):
                comp = st.value
                it = _iter_name_from_comp(comp)
                tgt = _target_name_from_comp(comp)
                if it == shares_name and tgt is not None:
                    elt = comp.elt
                    if (
                        isinstance(elt, ast.BinOp)
                        and isinstance(elt.op, ast.Sub)
                        and _is_name(elt.left, tgt)
                        and isinstance(elt.right, ast.Name)
                    ):
                        fee_name = elt.right.id
                        break
        if fee_name is not None:
            self._add(
                {
                    "scope": "function",
                    "function": ctx.function,
                    "element": ctx.function,
                    "property": "fee_shifts_total_by_n_times_fee",
                    "precondition": None,
                    "formal": (
                        f"sum({ctx.function}(...)) == {amount_name} - {fee_name} * len({ratios_name})"
                    ),
                }
            )

    def _infer_token_bucket(self, fn: ast.FunctionDef) -> None:
        ctx = self._ctx()
        # Heuristic: function has arg named 'tokens' and assigns tokens['available']
        if "tokens" not in ctx.args:
            return
        has_subscript_assign = any(
            isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Subscript) for t in n.targets)
            for n in ast.walk(fn)
        )
        if not has_subscript_assign:
            return

        # Property: on True return, tokens keys updated (available, last)
        for ret in [n for n in ast.walk(fn) if isinstance(n, ast.Return) and n.value is not None]:
            b = _literal_bool(ret.value)
            if b is True:
                self._add(
                    {
                        "scope": "branch" if self._is_guarded_return(ret) else "function",
                        "function": ctx.function,
                        "element": ctx.function,
                        "property": "state_update_on_success",
                        "precondition": None,
                        "formal": (
                            "if return True then tokens['available'] decreases by 1 and tokens['last'] set to now"
                        ),
                    }
                )
            if b is False:
                self._add(
                    {
                        "scope": "branch" if self._is_guarded_return(ret) else "function",
                        "function": ctx.function,
                        "element": ctx.function,
                        "property": "failure_no_consumption",
                        "precondition": None,
                        "formal": "if return False then no token is consumed (available <= 0)",
                    }
                )

        # Property: available is capped at capacity (if both names appear)
        if "capacity" in ctx.args:
            self._add(
                {
                    "scope": "function",
                    "function": ctx.function,
                    "element": ctx.function,
                    "property": "available_capped_by_capacity",
                    "precondition": None,
                    "formal": "available <= capacity",
                }
            )


def extract_semantics_from_file(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
        _attach_parents(tree)
        ex = SemanticExtractor(filename=path.name, source=source)
        ex.visit(tree)
        return {"file": path.name, "properties": ex.items, "error": None}
    except SyntaxError as e:
        return {
            "file": path.name,
            "properties": [],
            "error": {
                "type": "SyntaxError",
                "message": str(e),
                "lineno": getattr(e, "lineno", None),
                "offset": getattr(e, "offset", None),
            },
        }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Directory containing .py files")
    ap.add_argument("--output", required=True, help="Directory to write <name>.json")
    ap.add_argument("--glob", default="*.py", help="Glob of files (default: *.py)")
    args = ap.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(in_dir.glob(args.glob)):
        if not path.is_file():
            continue
        result = extract_semantics_from_file(path)
        out_path = out_dir / f"{path.stem}.json"
        out_path.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
