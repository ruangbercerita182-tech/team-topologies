#!/usr/bin/env python3
"""Prove every check in check_docs can actually fail.

R-3: "Every check has a seeded fixture in the same PR. A check whose
fixture is deleted fails review." A check that has only ever returned
clean is not known to work (TDD §13).

Run:  python3 tools/docs/test_check_docs.py
Exit: 0 all checks proven, 1 a check failed to fire or false-positived.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_docs import load, run  # noqa: E402

FIXTURES = HERE / "fixtures" / "drift"

# fixture directory -> (check id expected to fire, minimum severity)
CASES = [
    ("doc00-clean",         None,      None),
    ("doc01-ref-undefined", "DOC-01",  "error"),
    ("doc02-link-file",     "DOC-02",  "error"),
    ("doc03-link-anchor",   "DOC-03",  "warning"),
    ("doc04-adr-range",     "DOC-04",  "error"),
    ("doc04-adr-count",     "DOC-04",  "warning"),
    ("doc04-partial-range-valid", None,  None),
    ("doc04-partial-range-gap",   "DOC-04", "error"),
    ("doc05-dec-uncovered", "DOC-05",  "warning"),
    ("doc06-gap-unclosed",  "DOC-06",  "error"),
    ("doc07-gate-alias",    "DOC-07",  "error"),
    ("doc08-version-conflict", "DOC-08", "error"),
    ("doc08-owner-conflict",   "DOC-08", "error"),
    ("doc08-unregistered",     "DOC-08", "warning"),
    ("doc09-suppressed",       None,      None),
    ("doc05-range-authored",   None,      None),
    ("doc05-uncovered-both",   "DOC-05",  "warning"),
    ("doc10-duplicate-heading", "DOC-10", "error"),
    ("doc90-rejected-in-range", "DOC-90",  "error"),
    ("doc90-scoped-allow",     None,      None),
    ("doc90-scope-missed",     "DOC-90",  "error"),
]


def codes(findings) -> set[str]:
    return {f.check for f in findings}


def main() -> int:
    failures: list[str] = []

    for name, expect, severity in CASES:
        d = FIXTURES / name
        if not d.is_dir():
            failures.append(f"{name}: fixture directory missing")
            continue

        findings, _suppressed, corpus = run(d, "none")
        got = codes(findings)

        if expect is None:
            if findings:
                failures.append(
                    f"{name}: expected clean, got "
                    + "; ".join(f.check for f in findings)
                )
            else:
                print(f"  ok    {name:22} clean ({len(corpus.files)} docs)")
            continue

        if expect not in got:
            failures.append(f"{name}: expected {expect} to fire, got {sorted(got) or 'nothing'}")
            continue

        matched = [f for f in findings if f.check == expect]
        if severity and not any(f.severity == severity for f in matched):
            failures.append(
                f"{name}: {expect} fired but not at severity {severity}: "
                f"{[f.severity for f in matched]}"
            )
            continue

        print(f"  ok    {name:22} {expect} fired at {severity}")

    print()
    if failures:
        print(f"FAILED ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"all {len(CASES)} fixtures behaved as specified")
    return 0


if __name__ == "__main__":
    sys.exit(main())