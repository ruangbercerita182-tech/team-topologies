#!/usr/bin/env python3
"""Prove check_pins can fail, and cannot fail on correct input.

FR-21 states the acceptance directly: "check:pins fails on a fixture
containing @latest and passes on the pinned form." TDD §13: a gate never
observed red is not known to work. R-3: a check whose fixture is deleted
fails review.

Run:  python3 tools/checks/test_check_pins.py
Exit: 0 all cases behaved as specified, 1 a case did not.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_pins import is_floating, main  # noqa: E402

FIX = HERE / "fixtures"

# (fixture dir, expected exit, what the case proves)
CASES = [
    ("clean", 0, "a fully pinned tree passes"),
    ("floating", 1, "@latest, ^range and a Nix pin-defeating flag are rejected"),
    ("dev-floating", 0, "a floating devDependency is tolerated by default"),
]

# (spec, expected floating) -- is_floating decides, not the file format
UNIT = [
    ("1.2.3", False), ("0.0.1-exact", False), ("==2.32.3", False),
    ("./local", False), ("../up", False), ("workspace:*", False),
    ("workspace:^1.2.3", False),
    ("github:o/r#abc1234", False), ("git+ssh://g/o/r.git#deadbeef1234", False),
    ("https://x/archive/refs/tags/v1.2.3", False),
    ("^1.2.3", True), ("~1.2.3", True), (">=1.2.3", True), ("1.x", True),
    ("*", True), ("latest", True), ("next", True), ("canary", True),
    ("https://x/y.git", True), ("==2.32.3,<3", True), ("~=2.32", True),
    ("", True),
]


def main_test() -> int:
    failures: list[str] = []

    for name, expect, why in CASES:
        d = FIX / name
        if not d.is_dir():
            failures.append(f"{name}: fixture missing")
            continue
        rc = main(["-C", str(d)])
        if rc != expect:
            failures.append(f"{name}: exit {rc}, expected {expect} ({why})")
        else:
            print(f"  ok    {name:16} exit {rc}  — {why}")

    for spec, expect in UNIT:
        got = is_floating(spec) is not None
        if got != expect:
            failures.append(f"is_floating({spec!r}) = {got}, expected {expect}")

    # --strict-deps must flip the devDependency case, or the flag is decorative
    rc = main(["-C", str(FIX / "dev-floating"), "--strict-deps"])
    if rc != 1:
        failures.append(f"--strict-deps did not change the outcome (exit {rc})")
    else:
        print("  ok    --strict-deps    exit 1  — the flag is not decorative")

    # a missing root is a configuration error, never a clean result
    rc = main(["-C", str(FIX / "does-not-exist")])
    if rc != 2:
        failures.append(f"missing root returned {rc}, expected 2")
    else:
        print("  ok    missing root     exit 2  — a typo cannot read as 'clean'")

    print()
    if failures:
        print(f"FAILED ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"all {len(CASES)} fixtures and {len(UNIT)} unit cases behaved as specified")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())