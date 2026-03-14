"""Group pytest nodeids in test_report.json by the python_programs/*.py file they test.

Reads:
  semantic_prop_project/test_report.json

Writes:
  semantic_prop_project/test_report_by_group.json

Grouping logic:
- Each nodeid key looks like: generated_tests/test_x.py::test_name
- Each generated test file contains a PROGRAM_PATH pointing at:
    ... / "python_programs" / "<program>.py"
  We extract <program>.py with a regex.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def _extract_program_filename(test_file_text: str) -> str | None:
    # Example line:
    # PROGRAM_PATH = Path(__file__).resolve().parents[1] / "python_programs" / "ad_mix.py"
    prog_re = re.compile(r"python_programs.*?\"(?P<prog>[^\"]+\.py)\"")

    # Prefer lines that mention PROGRAM_PATH (more precise).
    for line in test_file_text.splitlines():
        if "PROGRAM_PATH" in line and "python_programs" in line:
            m = prog_re.search(line)
            if m:
                return m.group("prog")

    # Fallback: scan whole file.
    m = prog_re.search(test_file_text)
    if m:
        return m.group("prog")
    return None


def main() -> None:
    root = Path(__file__).resolve().parent
    report_path = root / "test_report.json"
    out_path = root / "test_report_by_group.json"

    report = json.loads(report_path.read_text(encoding="utf-8"))
    tests: dict[str, str] = report.get("tests", {})

    # nodeid -> status, where nodeid includes the test file path prefix.
    unique_test_files = {nodeid.split("::", 1)[0] for nodeid in tests.keys()}

    # Map: generated test file path -> program filename (e.g., ad_mix.py)
    program_by_testfile: dict[str, str | None] = {}
    for test_file in sorted(unique_test_files):
        path = Path(test_file)
        if not path.exists():
            # If nodeids were emitted with paths relative to repo root, try that.
            alt = (root.parent / test_file).resolve()
            path = alt
        if not path.exists():
            program_by_testfile[test_file] = None
            continue
        program_by_testfile[test_file] = _extract_program_filename(
            path.read_text(encoding="utf-8")
        )

    unknown_key = "__unknown__"
    groups: dict[str, dict[str, object]] = defaultdict(
        lambda: {"tests": {}, "summary": Counter()}
    )

    for nodeid, status in tests.items():
        test_file = nodeid.split("::", 1)[0]
        prog = program_by_testfile.get(test_file)
        group_key = prog if prog else unknown_key

        group_tests: dict[str, str] = groups[group_key]["tests"]  # type: ignore[assignment]
        group_tests[nodeid] = status

        group_summary: Counter[str] = groups[group_key]["summary"]  # type: ignore[assignment]
        group_summary[status] += 1

    # Ensure every group summary has the same keys as the global report summary.
    all_statuses = list(report.get("summary", {}).keys())
    for g in groups.values():
        summary: Counter[str] = g["summary"]  # type: ignore[assignment]
        for s in all_statuses:
            summary.setdefault(s, 0)
        g["summary"] = dict(summary)

    out = {
        "summary": report.get("summary", {}),
        "total-generated-tests": len(tests),
        "groups": dict(sorted(groups.items(), key=lambda kv: kv[0])),
    }

    # Validate counts.
    computed = Counter()
    for g in out["groups"].values():
        computed.update(g["summary"])
    reported = Counter(out["summary"])
    if computed != reported:
        raise SystemExit(
            "Computed summary from groups does not match report summary. "
            f"delta(computed-reported)={dict(computed - reported)} "
            f"delta(reported-computed)={dict(reported - computed)}"
        )

    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
