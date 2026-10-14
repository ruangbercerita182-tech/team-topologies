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
from check_toolchain import main as tc_main  # noqa: E402
from check_lsc import evaluate, load_teams  # noqa: E402

FIX = HERE / "fixtures"
TC_FIX = HERE / "fixtures" / "toolchain"

# (fixture dir, expected exit, what the case proves)
CASES = [
    ("clean", 0, "a fully pinned tree passes"),
    ("floating", 1, "@latest, ^range and a Nix pin-defeating flag are rejected"),
    ("dev-floating", 0, "a floating devDependency is tolerated by default"),
]

# T-105: FR-26, FR-27, RES-01
TC_CASES = [
    ("clean", 0, "one manager, one root lockfile, no nested .git"),
    ("nested", 1, "a nested lockfile, a nested .git and a second manager are all reported"),
    ("two-root-locks", 1, "two lockfiles at the root resolve differently"),
]

# T-107 / FR-01 / AC-11. The PRD states two of these verbatim:
#   "a PR touching two teams' directories with no Owners-Override trailer is
#    rejected"; "a PR carrying the trailer with only one approval is rejected."
SLUGS = {"banner", "web", "platform"}
TWO_TEAMS = ["teams/banner/api/a.ts", "teams/web/client/b.tsx"]
TRAILER_BOTH = "subject: x\n\nOwners-Override: banner, web"

LSC_CASES = [
    # (label, paths, approvers, author, author_team, message, team_approvals, expect_rejected)
    ("one owner, no trailer", ["teams/banner/api/a.ts"], ["ana"], None, None, "", [], False),
    ("two owners, no trailer", TWO_TEAMS, ["ana"], None, None, "", [], True),
    ("trailer, one approval", TWO_TEAMS, ["ana"], None, None, TRAILER_BOTH, [], True),
    ("trailer, two approvals", TWO_TEAMS, ["ana", "bob"], None, None, TRAILER_BOTH, [], False),
    ("trailer names only one team", TWO_TEAMS, ["ana", "bob"], None, None,
     "Owners-Override: banner", [], True),
    ("proposer owns one, other approved", TWO_TEAMS, ["ana"], None, "banner", "", ["web"], False),
    ("proposer owns one, other silent", TWO_TEAMS, ["ana"], None, "banner", "", [], True),
    ("proposer owns all touched", ["teams/banner/a.ts", "teams/banner/api/b.ts"],
     ["ana"], None, "banner", "", [], False),
    ("undeclared directory", ["teams/ghost/a.ts", "teams/banner/b.ts"],
     ["ana"], None, None, "", [], True),
    ("malformed trailer entry", TWO_TEAMS, ["ana", "bob"], None, None,
     "Owners-Override: !!!!", [], True),
    # The trailer is asserted once, on the merge commit (PRD 1.4). Nothing here
    # inspects the branch's individual commits, so an author is never required to
    # carry it per commit -- which would demand knowing the finished change's
    # owner set at every step.
    ("trailer on the merge commit only", TWO_TEAMS, ["ana", "bob"], None, None,
     "subject: x\n\nOwners-Override: banner, web\n", [], False),
    # git does not read a trailer that is followed by prose, so neither do we:
    # accepting one would grant an override no post-merge audit could find.
    ("trailer followed by prose", TWO_TEAMS, ["ana", "bob"], None, None,
     "Owners-Override: banner, web\n\nA paragraph after it.\n", [], True),
    ("trailer mentioned only in prose", TWO_TEAMS, ["ana", "bob"], None, None,
     "Subject: x\n\nWe agreed Owners-Override: banner, web is needed.\n", [], True),
    # a typo grants nothing and must not pass silently
    ("typo in an override team name", TWO_TEAMS, ["ana", "bob"], None, None,
     "Subject: x\n\nOwners-Override: banner, wek\n", [], True),
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

    for name, expect, why in TC_CASES:
        d = TC_FIX / name
        if not d.is_dir():
            failures.append(f"toolchain/{name}: fixture missing")
            continue
        rc = tc_main(["-C", str(d)])
        if rc != expect:
            failures.append(f"toolchain/{name}: exit {rc}, expected {expect} ({why})")
        else:
            print(f"  ok    toolchain/{name:12} exit {rc}  — {why}")

    from check_lsc import rejected as lsc_rejected
    for label, paths, appr, author, ateam, msg, tapprovals, expect in LSC_CASES:
        d = evaluate(paths, appr, author, ateam, msg, tapprovals, SLUGS)
        got = lsc_rejected(d)
        if got != expect:
            failures.append(f"lsc[{label}]: rejected={got}, expected {expect}; reasons={d.reasons}")
        else:
            print(f"  ok    lsc/{label:32} {'reject' if got else 'allow '}  — FR-01/AC-11")

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
    print(f"all {len(CASES) + len(TC_CASES)} fixtures, {len(LSC_CASES)} LSC cases "
          f"and {len(UNIT)} unit cases behaved as specified")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())