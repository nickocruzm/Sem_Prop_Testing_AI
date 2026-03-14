"""AST-based structural element extractor.

For each Python file, this script emits a JSON file named `<filename>.json`
(e.g. `normalize.py` -> `normalize.py.json`) containing a list of structural
elements found:

- functions
- control-flow branches (if/elif/else, match/case, try/except)
- loops (for/while)
- API call boundaries (heuristic: network/io/subprocess/etc)
- early returns

The output is intentionally *structural* (syntax-derived) rather than attempting
to infer deep semantic properties.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


API_ROOT_NAMES = {
    # network
    "requests",
    "httpx",
    "urllib",
    "socket",
    # subprocess / shell
    "subprocess",
    # filesystem / io
    "pathlib",
    "os",
    "shutil",
    "io",
    # db-ish (common)
    "sqlite3",
}

API_FUNC_NAMES = {
    # builtins / common IO
    "open",
}


def _safe_unparse(node: ast.AST, source: str) -> str:
    seg = ast.get_source_segment(source, node)
    if seg is not None:
        return seg.strip()
    # Fallback: ast.unparse (py>=3.9)
    try:
        return ast.unparse(node).strip()  # type: ignore[attr-defined]
    except Exception:
        return node.__class__.__name__


def _callee_chain(call: ast.Call) -> str:
    """Return a dotted callee string like `requests.get` or `client.fetch`."""
    f = call.func
    parts: list[str] = []
    while isinstance(f, ast.Attribute):
        parts.append(f.attr)
        f = f.value
    if isinstance(f, ast.Name):
        parts.append(f.id)
    parts.reverse()
    return ".".join(parts) if parts else "<call>"


def _api_category(callee: str) -> Optional[str]:
    root = callee.split(".")[0]
    if root in {"requests", "httpx", "urllib", "socket"}:
        return "network"
    if root in {"subprocess"}:
        return "subprocess"
    if root in {"os", "pathlib", "shutil", "io"}:
        return "io"
    if root in {"sqlite3"}:
        return "db"
    if root in API_ROOT_NAMES:
        return "api"
    if callee in API_FUNC_NAMES:
        return "io"
    return None


def _is_api_call(call: ast.Call) -> bool:
    callee = _callee_chain(call)
    if callee in API_FUNC_NAMES:
        return True
    root = callee.split(".")[0]
    return root in API_ROOT_NAMES


def _get_assigned_to(node: ast.AST) -> Optional[str]:
    """If node is on RHS of `x = <call>`, return `x` when it is a simple name."""
    if not hasattr(node, "parent"):
        return None
    p = getattr(node, "parent")
    if isinstance(p, ast.Assign) and p.value is node:
        if len(p.targets) == 1 and isinstance(p.targets[0], ast.Name):
            return p.targets[0].id
    if isinstance(p, ast.AnnAssign) and p.value is node:
        if isinstance(p.target, ast.Name):
            return p.target.id
    return None


def _attach_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "parent", parent)


@dataclass
class Ctx:
    filename: str
    source: str
    function: str  # "<module>" or function name
    guard_stack: list[str]


class Extractor(ast.NodeVisitor):
    def __init__(self, *, filename: str, source: str):
        self._filename = filename
        self._source = source
        self._function_stack: list[str] = ["<module>"]
        self._guard_stack: list[str] = []
        self.items: list[dict[str, Any]] = []

    def _ctx(self) -> Ctx:
        return Ctx(
            filename=self._filename,
            source=self._source,
            function=self._function_stack[-1],
            guard_stack=list(self._guard_stack),
        )

    def _add(self, obj: dict[str, Any]) -> None:
        obj.setdefault("file", self._filename)
        self.items.append(obj)

    def _line_span(self, node: ast.AST) -> tuple[Optional[int], Optional[int]]:
        return (
            getattr(node, "lineno", None),
            getattr(node, "end_lineno", None),
        )

    # ---- Structural elements ----

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        start, end = self._line_span(node)
        self._add(
            {
                "scope": "function",
                "function": node.name,
                "property": "defines_function",
                "args": [a.arg for a in node.args.args],
                "start_line": start,
                "end_line": end,
            }
        )

        self._function_stack.append(node.name)
        self.generic_visit(node)
        self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        # Treat same as FunctionDef.
        start, end = self._line_span(node)
        self._add(
            {
                "scope": "function",
                "function": node.name,
                "property": "defines_async_function",
                "args": [a.arg for a in node.args.args],
                "start_line": start,
                "end_line": end,
            }
        )
        self._function_stack.append(node.name)
        self.generic_visit(node)
        self._function_stack.pop()

    def visit_If(self, node: ast.If) -> Any:
        ctx = self._ctx()
        cond = _safe_unparse(node.test, ctx.source)
        start, end = self._line_span(node)
        self._add(
            {
                "scope": "branch",
                "function": ctx.function,
                "property": "conditional_branch",
                "branch_type": "if",
                "condition": cond,
                "guards": list(ctx.guard_stack),
                "start_line": start,
                "end_line": end,
            }
        )

        # Body guarded by `cond`
        self._guard_stack.append(cond)
        for st in node.body:
            self.visit(st)
        self._guard_stack.pop()

        # Else guarded by `not (cond)` if it exists
        if node.orelse:
            neg = f"not ({cond})"
            self._add(
                {
                    "scope": "branch",
                    "function": ctx.function,
                    "property": "conditional_branch",
                    "branch_type": "else",
                    "condition": neg,
                    "guards": list(ctx.guard_stack),
                    "start_line": getattr(node.orelse[0], "lineno", start),
                    "end_line": getattr(node.orelse[-1], "end_lineno", end),
                }
            )
            self._guard_stack.append(neg)
            for st in node.orelse:
                self.visit(st)
            self._guard_stack.pop()

    def visit_Match(self, node: ast.Match) -> Any:
        ctx = self._ctx()
        start, end = self._line_span(node)
        subj = _safe_unparse(node.subject, ctx.source)
        self._add(
            {
                "scope": "branch",
                "function": ctx.function,
                "property": "match_branch",
                "branch_type": "match",
                "condition": subj,
                "guards": list(ctx.guard_stack),
                "start_line": start,
                "end_line": end,
            }
        )
        for case in node.cases:
            pat = _safe_unparse(case.pattern, ctx.source)
            guard = _safe_unparse(case.guard, ctx.source) if case.guard else None
            case_cond = f"case {pat}" + (f" if {guard}" if guard else "")
            cstart, cend = self._line_span(case)
            self._add(
                {
                    "scope": "branch",
                    "function": ctx.function,
                    "property": "match_case",
                    "branch_type": "case",
                    "condition": case_cond,
                    "guards": list(ctx.guard_stack),
                    "start_line": cstart,
                    "end_line": cend,
                }
            )
            self._guard_stack.append(case_cond)
            for st in case.body:
                self.visit(st)
            self._guard_stack.pop()

    def visit_Try(self, node: ast.Try) -> Any:
        ctx = self._ctx()
        start, end = self._line_span(node)
        self._add(
            {
                "scope": "branch",
                "function": ctx.function,
                "property": "try_block",
                "branch_type": "try",
                "condition": "try",
                "guards": list(ctx.guard_stack),
                "start_line": start,
                "end_line": end,
            }
        )
        for st in node.body:
            self.visit(st)
        for h in node.handlers:
            hstart, hend = self._line_span(h)
            exc = _safe_unparse(h.type, ctx.source) if h.type else "Exception"
            name = h.name
            cond = f"except {exc}" + (f" as {name}" if name else "")
            self._add(
                {
                    "scope": "branch",
                    "function": ctx.function,
                    "property": "exception_handler",
                    "branch_type": "except",
                    "condition": cond,
                    "guards": list(ctx.guard_stack),
                    "start_line": hstart,
                    "end_line": hend,
                }
            )
            self._guard_stack.append(cond)
            for st in h.body:
                self.visit(st)
            self._guard_stack.pop()
        for st in node.orelse:
            self.visit(st)
        for st in node.finalbody:
            self.visit(st)

    def visit_For(self, node: ast.For) -> Any:
        ctx = self._ctx()
        start, end = self._line_span(node)
        target = _safe_unparse(node.target, ctx.source)
        it = _safe_unparse(node.iter, ctx.source)
        descr = f"for {target} in {it}"
        self._add(
            {
                "scope": "loop",
                "function": ctx.function,
                "property": "loop_iteration",
                "loop_type": "for",
                "target": target,
                "iter": it,
                "guards": list(ctx.guard_stack),
                "start_line": start,
                "end_line": end,
            }
        )
        self._guard_stack.append(descr)
        for st in node.body:
            self.visit(st)
        self._guard_stack.pop()
        for st in node.orelse:
            self.visit(st)

    def visit_While(self, node: ast.While) -> Any:
        ctx = self._ctx()
        start, end = self._line_span(node)
        cond = _safe_unparse(node.test, ctx.source)
        descr = f"while {cond}"
        self._add(
            {
                "scope": "loop",
                "function": ctx.function,
                "property": "loop_iteration",
                "loop_type": "while",
                "condition": cond,
                "guards": list(ctx.guard_stack),
                "start_line": start,
                "end_line": end,
            }
        )
        self._guard_stack.append(descr)
        for st in node.body:
            self.visit(st)
        self._guard_stack.pop()
        for st in node.orelse:
            self.visit(st)

    def visit_Return(self, node: ast.Return) -> Any:
        ctx = self._ctx()
        line = getattr(node, "lineno", None)
        value = _safe_unparse(node.value, ctx.source) if node.value else None

        # We call it an early return if it is not the last statement of the
        # enclosing function body.
        early = False
        parent = getattr(node, "parent", None)
        if parent is not None and isinstance(parent, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
            early = True
        elif parent is not None and isinstance(parent, ast.FunctionDef):
            # last statement check
            if parent.body and parent.body[-1] is not node:
                early = True

        self._add(
            {
                "scope": "early_return" if early else "return",
                "function": ctx.function,
                "property": "early_exit" if early else "return_exit",
                "value": value,
                "guards": list(ctx.guard_stack),
                "line": line,
            }
        )

    def visit_Call(self, node: ast.Call) -> Any:
        ctx = self._ctx()
        if _is_api_call(node):
            callee = _callee_chain(node)
            cat = _api_category(callee) or "api"
            call_src = _safe_unparse(node, ctx.source)
            start, end = self._line_span(node)
            self._add(
                {
                    "scope": "api_call",
                    "function": ctx.function,
                    "property": "api_call_boundary",
                    "callee": callee,
                    "category": cat,
                    "call": call_src,
                    "assigned_to": _get_assigned_to(node),
                    "preconditions": list(ctx.guard_stack),
                    "postconditions": [],
                    "start_line": start,
                    "end_line": end,
                }
            )
        self.generic_visit(node)


def extract_from_source(*, filename: str, source: str) -> list[dict[str, Any]]:
    tree = ast.parse(source)
    _attach_parents(tree)
    ex = Extractor(filename=filename, source=source)
    ex.visit(tree)
    return ex.items


def process_file(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    try:
        items = extract_from_source(filename=path.name, source=source)
        return {"file": path.name, "elements": items, "error": None}
    except SyntaxError as e:
        return {
            "file": path.name,
            "elements": [],
            "error": {
                "type": "SyntaxError",
                "message": str(e),
                "lineno": getattr(e, "lineno", None),
                "offset": getattr(e, "offset", None),
            },
        }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        required=True,
        help="Directory containing .py files to analyze",
    )
    ap.add_argument(
        "--output",
        required=True,
        help="Directory to write <filename>.json outputs",
    )
    ap.add_argument(
        "--glob",
        default="*.py",
        help="Glob to select input files (default: *.py)",
    )
    args = ap.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    py_files = sorted(in_dir.glob(args.glob))
    for path in py_files:
        if not path.is_file():
            continue
        result = process_file(path)
        out_path = out_dir / f"{path.name}.json"
        out_path.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
