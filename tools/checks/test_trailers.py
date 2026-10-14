#!/usr/bin/env python3
"""Differential test: our trailer parser against `git interpret-trailers`.

The trailer is only worth anything if the tooling can find it afterwards. A
parser that reads "Owners-Override: web" out of the middle of a paragraph grants
an override that `git log --format='%(trailers:key=Owners-Override)'` will never
report, which is precisely the property FR-01 exists to provide.

So the parser is not written from git's documentation; it is written to agree
with git, and this test is how that agreement is kept. It shells out to git and
compares. If git is unavailable the test fails rather than skipping: a
differential test that quietly stops testing is worse than none.

Run:  python3 tools/checks/test_trailers.py
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_lsc import parse_trailers  # noqa: E402

CASES = {
    "trailer at end": "Subject: x\n\nbody text\n\nOwners-Override: web, banner\n",
    "trailer then prose": "Subject: x\n\nOwners-Override: web\n\nThis paragraph follows it.\n",
    "inline in prose": "Subject: x\n\nWe agreed Owners-Override: web is needed.\n",
    "multi-trailer block": "Subject: x\n\nbody\n\nOwners-Override: web\nSigned-off-by: ana\n",
    "key with spaces": "Subject: x\n\nWe agreed Owners Override: web\n",
    "no trailer": "Subject: x\n\njust a body\n",
    "lowercase key": "Subject: x\n\nowners-override: web\n",
    "continuation": "Subject: x\n\nbody\n\nOwners-Override: web,\n  banner\n",
    "deep continuation": "Subject: x\n\nbody\n\nOwners-Override: web,\n\t\tbanner\n",
    "only trailer": "Owners-Override: web\n",
    "prose colon line": "Subject: x\n\nNote: this is prose\nthat continues here\n",
    "trailer then blank then prose": "Subject: x\n\nOwners-Override: web\n\nmore prose\n",
    "trailing blank lines": "Subject: x\n\nbody\n\nOwners-Override: web\n\n\n",
    "url in value": "Subject: x\n\nbody\n\nOwners-Override: web https://x/y\n",
    "empty value": "Subject: x\n\nbody\n\nOwners-Override:\n",
    "trailer in middle of block": "Subject: x\n\nbody\n\nSigned-off-by: ana\nOwners-Override: web\n",
}


def git_trailers(msg: str) -> str:
    res = subprocess.run(["git", "interpret-trailers", "--parse"], input=msg,
                         capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"git interpret-trailers failed: {res.stderr.strip()}")
    return res.stdout.strip()


def main() -> int:
    try:
        git_trailers("Subject: x\n\nbody\n\nOwners-Override: web\n")
    except (RuntimeError, FileNotFoundError) as exc:
        print(f"test_trailers: git unavailable ({exc}); this test cannot be skipped",
              file=sys.stderr)
        return 1

    failures = []
    for label, msg in CASES.items():
        try:
            ref = git_trailers(msg)
        except RuntimeError as exc:
            failures.append(f"{label}: {exc}")
            continue
        mine = "\n".join(f"{k}: {' '.join(v)}" for k, v in parse_trailers(msg).items()).strip()
        if mine != ref:
            failures.append(f"{label}: git={ref!r} ours={mine!r}")
        else:
            print(f"  ok    {label:32} {ref!r}")

    print()
    if failures:
        print(f"FAILED ({len(failures)} of {len(CASES)}):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"all {len(CASES)} cases agree with git interpret-trailers --parse")
    return 0


if __name__ == "__main__":
    sys.exit(main())
