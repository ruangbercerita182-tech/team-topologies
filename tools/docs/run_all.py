#!/usr/bin/env python3
"""run_all — one command that runs every gate for the document set.

CI and the pre-commit hook both call this, so there is exactly one definition
of "the documentation gates pass". Exit codes:

  0  every gate passed
  1  a gate found something to act on
  2  a gate could not run (configuration error) -- never reported as success

Standard library only.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DOCS = REPO / "docs"
BASELINE = HERE / "baseline.json"

CHECKS = HERE.parent / "checks"

GATES = [
    ("doc fixtures", [sys.executable, str(HERE / "test_check_docs.py")]),
    ("pin fixtures", [sys.executable, str(CHECKS / "test_check_pins.py")]),
    ("pinned resolution (FR-21)",
     [sys.executable, str(CHECKS / "check_pins.py"), "-C", str(REPO)]),
    ("toolchain (FR-26/FR-27/RES-01)",
     [sys.executable, str(CHECKS / "check_toolchain.py"), "-C", str(REPO)]),
    ("generator up to date",
     [sys.executable, str(HERE / "gen_docs.py"), "-C", str(DOCS), "--check"]),
    ("document coherence",
     [sys.executable, str(HERE / "check_docs.py"), "-C", str(DOCS),
      "--fail-on", "warning", "--baseline", str(BASELINE)]),
]


def main() -> int:
    print(f"run_all: {REPO}\n")
    failed = 0
    config_error = 0
    for name, cmd in GATES:
        res = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        status = {0: "PASS", 1: "FAIL", 2: "ERROR"}.get(res.returncode, f"EXIT {res.returncode}")
        if res.returncode == 1:
            failed += 1
        elif res.returncode != 0:
            config_error += 1
        print(f"[{status:5}] {name}")
        out = (res.stdout + res.stderr).rstrip()
        if res.returncode != 0 and out:
            for line in out.splitlines():
                print(f"        {line}")
        print()

    if config_error:
        print(f"run_all: {config_error} gate(s) could not run. "
              "That is a configuration error and is not a pass.")
        return 2
    if failed:
        print(f"run_all: {failed} gate(s) found something to act on.")
        return 1
    print("run_all: all gates passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())