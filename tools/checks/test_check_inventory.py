#!/usr/bin/env python3
"""Fixture suite for check_inventory.

check_inventory enforces R-03 -- a check whose fixture is deleted fails review --
so it cannot exempt itself. Each fixture below drives one rule to failure against
a miniature repository built in a temporary directory, and asserts the exit code.

The last fixture is the one that matters: it reproduces the exact manipulation
that left every gate green in the demonstration -- removing DOC-10 from the
registry, from the fixture suite, and from disk -- and asserts the tree is now
refused.

Standard library only. Exit 0 when every fixture behaved as specified.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECK = HERE / "check_inventory.py"

TDD_OK = """# TDD

## 13. Check inventory

| CHK | Command | Input | Fails on | Seeded fixture | Status |
|---|---|---|---|---|---|
| 01 | `check:alpha` DOC-98 | tracked text | FR-01 | a version stated twice | Built |
| 02 | `check:beta` DOC-99 | repository root | FR-02 | a nested `.git` | Built |
| 03 | `check:gamma` | build output | FR-03 | an oversized route | Planned |
"""

# Each check lives in the file section 13 resolves its command to, because that
# is the whole point: a check deleted from its registry must become invisible.
CHECK_ALPHA_OK = '''"""One check per gate file."""


def doc_98_duplicate_heading(ctx):
    return []


CHECKS = [
    ("DOC-98", doc_98_duplicate_heading),
]
'''

CHECK_BETA_OK = '''"""The gate section 13 names with an inline check id."""


def doc_99_nested_repo(ctx):
    return []


CHECKS = [
    ("DOC-99", doc_99_nested_repo),
]
'''

SUITE_OK = '''CASES = [
    ("alpha-duplicate-version", "DOC-98", "error"),
    ("beta-nested-git", "DOC-99", "error"),
]
'''

RUN_ALL_OK = '''GATES = [
    ("alpha", [sys.executable, str(CHECKS / "check_alpha.py")]),
    ("beta", [sys.executable, str(CHECKS / "check_beta.py")]),
]
'''


def build(root: Path, *, tdd: str = TDD_OK,
          alpha: str = CHECK_ALPHA_OK, beta: str = CHECK_BETA_OK,
          suite: str = SUITE_OK, run_all: str = RUN_ALL_OK,
          drop_fixture: bool = False, drop_check: bool = False,
          drop_suite_case: bool = False, drop_file: bool = False) -> Path:
    """Lay down a miniature repository that satisfies every rule."""
    docs = root / "docs"
    tools = root / "tools" / "docs"
    gate_dir = root / "tools" / "checks"
    fixtures = tools / "fixtures" / "drift"
    for d in (docs, tools, gate_dir, fixtures):
        d.mkdir(parents=True, exist_ok=True)

    beta_src = beta
    if drop_check:
        beta_src = beta.replace('    ("DOC-99", doc_99_nested_repo),\n', "")
    suite_src = suite
    if drop_suite_case:
        suite_src = suite.replace(
            '    ("beta-nested-git", "DOC-99", "error"),\n', "")
    run_src = run_all
    if drop_check:
        # A deleted check is also unregistered from the runner, so that nothing
        # in the tree still references it.
        run_src = run_all.replace(
            '    ("beta", [sys.executable, str(CHECKS / "check_beta.py")]),\n', "")

    (docs / "TDD.md").write_text(tdd, encoding="utf-8")
    (docs / "PRD.md").write_text("**FR-01 — single fact.**\n\n**FR-02 — no nesting.**\n",
                                 encoding="utf-8")
    (gate_dir / "check_alpha.py").write_text(alpha, encoding="utf-8")
    if drop_file:
        # Section 13 still declares `check:beta`, but the file is gone.
        stale = gate_dir / "check_beta.py"
        if stale.exists():
            stale.unlink()
    else:
        (gate_dir / "check_beta.py").write_text(beta_src, encoding="utf-8")
    (tools / "test_checks.py").write_text(suite_src, encoding="utf-8")
    (tools / "run_all.py").write_text(run_src, encoding="utf-8")

    for name in ("alpha-duplicate-version", "beta-nested-git"):
        if drop_fixture and name == "beta-nested-git":
            continue
        d = fixtures / name
        d.mkdir(exist_ok=True)
        (d / "notes.md").write_text(f"fixture {name}\n", encoding="utf-8")
    return root


def run(root: Path) -> tuple[int, str]:
    res = subprocess.run(
        [sys.executable, str(CHECK), "-C", str(root / "docs"), "--repo", str(root)],
        capture_output=True, text=True)
    return res.returncode, res.stdout + res.stderr


CASES: list[tuple[str, int, str]] = [
    # name, expected exit, substring that must appear
    ("clean", 0, "every executed gate is declared"),
    ("INV-01 gate not named in 13",
     1, "TDD section 13 does not name it"),
    ("INV-02 declared gate absent",
     1, "does not register it"),
    ("INV-02 check file missing",
     1, "but no check_beta.py exists"),
    ("INV-03 fixture with no assertion",
     1, "no suite asserts"),
    ("INV-04 gate cites no requirement",
     1, "names no requirement"),
    ("Planned gate with no file is not a finding", 0, "every executed gate is declared"),
    ("INV-04 gate cites unknown requirement",
     1, "which appears in no document"),
    ("R-03 check deleted with its fixture",
     1, "does not register it"),
]


def main() -> int:
    failures = 0
    for name, want_code, want_text in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            kw = {}
            if name.startswith("INV-01"):
                # check_gamma is declared (Planned), so an undeclared script needs
                # a name section 13 has never heard of.
                kw = {"run_all": RUN_ALL_OK.replace("check_beta.py", "check_omega.py")}
            elif name == "INV-02 declared gate absent":
                kw = {"drop_check": True, "drop_suite_case": True}
            elif name == "INV-02 check file missing":
                kw = {"drop_file": True}
            elif name == "INV-03 fixture with no assertion":
                kw = {"suite": SUITE_OK.replace(
                    '    ("beta-nested-git", "DOC-99", "error"),\n', "")}
            elif name == "INV-04 gate cites no requirement":
                kw = {"tdd": TDD_OK.replace("FR-01", "nothing in particular")}
            elif name.startswith("Planned"):
                kw = {"run_all": RUN_ALL_OK.replace(
                    '    ("beta", [sys.executable, str(CHECKS / "check_beta.py")]),\n', "")}
            elif name == "INV-04 gate cites unknown requirement":
                kw = {"tdd": TDD_OK.replace("FR-02", "FR-99")}
            elif name.startswith("R-03"):
                kw = {"drop_check": True, "drop_suite_case": True,
                      "drop_fixture": True}
            build(root, **kw)
            code, out = run(root)

        if code != want_code or want_text not in out:
            failures += 1
            print(f"[FAIL] {name}: expected exit {want_code} containing "
                  f"{want_text!r}, got {code}")
            print("       " + "\n       ".join(out.strip().splitlines()[:8]))
        else:
            print(f"[ok]   {name}: exit {code}")

    if failures:
        print(f"\n{failures} of {len(CASES)} inventory fixtures did not behave as specified")
        return 1
    print(f"all {len(CASES)} inventory fixtures behaved as specified")
    return 0


if __name__ == "__main__":
    sys.exit(main())