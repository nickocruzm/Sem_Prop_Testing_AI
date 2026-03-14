"""Run generated tests repeatedly and summarize pass/fail/exception/flaky.

This is optional but useful for the project goal of classifying outcomes.

Run:
  python -m semantic_prop_project.testgen.run_tests --tests semantic_prop_project/generated_tests -n 3
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunOutcome:
    nodeid: str
    outcome: str  # passed/failed/error/skipped


def _run_pytest_once(test_dir: Path) -> list[RunOutcome]:
    """Run pytest once and return per-test outcomes."""
    import pytest  # local import so generation does not require pytest at import time

    results: list[RunOutcome] = []

    class Plugin:
        def pytest_runtest_logreport(self, report):
            # only final call stage matters for pass/fail; setup stage can hold errors
            if report.when == "call":
                results.append(RunOutcome(report.nodeid, report.outcome))
            elif report.when == "setup" and report.failed:
                results.append(RunOutcome(report.nodeid, "error"))

    # -q for quiet, --disable-warnings for stable output
    rc = pytest.main(["-q", str(test_dir), "--disable-warnings"], plugins=[Plugin()])
    # In case collection failed catastrophically, results may be empty.
    _ = rc
    return results


def _format_summary_line(summary: dict[str, int], *, i: int, runs: int, test_dir: Path) -> str:
    # Stable, greppable one-line summary for each iteration.
    parts = [
        f"run={i}/{runs}",
        f"tests_dir={test_dir}",
        f"pass={summary.get('pass', 0)}",
        f"fail={summary.get('fail', 0)}",
        f"exception={summary.get('exception', 0)}",
        f"flaky={summary.get('flaky', 0)}",
        f"skip={summary.get('skip', 0)}",
    ]
    return " ".join(parts)


def _classify_across_runs(runs: list[list[RunOutcome]]) -> dict[str, str]:
    by_test: dict[str, set[str]] = {}
    for run in runs:
        for r in run:
            by_test.setdefault(r.nodeid, set()).add(r.outcome)

    final: dict[str, str] = {}
    for nodeid, outs in by_test.items():
        # normalize pytest terms to requested buckets
        mapped: set[str] = set()
        for o in outs:
            if o == "passed":
                mapped.add("pass")
            elif o == "failed":
                mapped.add("fail")
            elif o == "error":
                mapped.add("exception")
            elif o == "skipped":
                mapped.add("skip")
            else:
                mapped.add(o)

        if len(mapped - {"skip"}) > 1:
            final[nodeid] = "flaky"
        elif "exception" in mapped:
            final[nodeid] = "exception"
        elif "fail" in mapped:
            final[nodeid] = "fail"
        elif "pass" in mapped:
            final[nodeid] = "pass"
        else:
            final[nodeid] = "skip"
    return final


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", default="semantic_prop_project/generated_tests", help="Directory of tests")
    ap.add_argument("-n", "--runs", type=int, default=3, help="How many times to repeat")
    ap.add_argument("--out", default=None, help="Optional output JSON path")
    args = ap.parse_args()

    test_dir = Path(args.tests)
    runs: list[list[RunOutcome]] = []
    per_run_summaries: list[dict[str, int]] = []
    for i in range(1, args.runs + 1):
        one = _run_pytest_once(test_dir)
        runs.append(one)
        # Summarize this run so we can append it to a .txt file.
        s = {"pass": 0, "fail": 0, "exception": 0, "flaky": 0, "skip": 0}
        for r in one:
            if r.outcome == "passed":
                s["pass"] += 1
            elif r.outcome == "failed":
                s["fail"] += 1
            elif r.outcome == "error":
                s["exception"] += 1
            elif r.outcome == "skipped":
                s["skip"] += 1
        per_run_summaries.append(s)

    final = _classify_across_runs(runs)

    summary = {"pass": 0, "fail": 0, "exception": 0, "flaky": 0, "skip": 0}
    for outcome in final.values():
        summary[outcome] = summary.get(outcome, 0) + 1

    report = {
        "summary": summary,
        "tests": final,
        "per_run_summaries": per_run_summaries,
    }
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        # Also write a human-readable per-run summary to a companion .txt file.
        txt_path = out_path.with_suffix(".txt")
        lines = [
            _format_summary_line(s, i=i + 1, runs=args.runs, test_dir=test_dir)
            for i, s in enumerate(per_run_summaries)
        ]
        # Append mode so repeated invocations preserve history.
        with txt_path.open("a", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
    else:
        print(json.dumps(report["summary"], indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
