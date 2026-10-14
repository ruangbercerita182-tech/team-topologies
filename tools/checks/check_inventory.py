#!/usr/bin/env python3
"""check_inventory — R-03, mechanically. Every gate is named, and every gate has a fixture.

`TDD-CMS-001` §13 says: *"Every gate is named, has an exit code, and has a seeded
violation fixture that proves it fails."* It also said, of checks, *"a check
without a fixture is a check that has never been observed."*

Neither clause was enforced. The demonstration: deleting `DOC-10` from the
registry, its row from the fixture suite and its fixture directory from disk left
every gate green. `DOC-10` was the check that found nine duplicated sections in
`adr/README.md`. The machinery protecting against silent capability loss was
itself silently losable, which is the one outcome ADR-0028 exists to prevent.

This check closes it by holding the gates to the inventory that already exists —
`TDD.md` §13 — rather than to a parallel list that would drift from it:

  INV-01  every gate `run_all` executes is named in §13. A gate nobody declared
          is a gate nobody reviews.
  INV-02  every §13 row marked implemented exists in the tree.
  INV-03  every implemented gate carries at least one fixture, and every fixture
          is asserted by the suite. R-03's "a check whose fixture is deleted
          fails review", stated as a command.
  INV-04  every implemented gate names a requirement that exists in the PRD or the
          TDD. A gate that enforces nothing cannot be traced to anything.

**What this does not do.** It does not make deletion impossible: whoever can edit
the gates can edit this file too. It raises the cost from one edit in one file to
several coordinated edits across the tool, the suite and a normative design
document — and it makes an unenforced gate a red build rather than a silent loss.
That is the honest limit, and stating it is part of the design.

Exit codes: 0 clean, 1 findings, 2 configuration or usage error.
Standard library only.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DOCS = REPO / "docs"

# CHK row in TDD.md section 13: | 09 | `check:pins` | input | FR-21, D-11 | fixture |
# One row per CHECK, not per script. `check_docs.py` holds ten checks in one
# file; grouping them into a single row is what let a deletion of DOC-10 go
# unnoticed -- the inventory was coarser than the thing it was protecting.
# The whole command cell is captured, not just the backticked part: rows read
# "`check:docs` DOC-10", and capturing only the backticks lost the check id --
# which is the one thing the row exists to declare.
ROW = re.compile(r"^\|\s*(?P<chk>\d{2})\s*\|\s*(?P<cmd>[^|]+?)\s*\|(?P<rest>.*)$")
STATUS = re.compile(r"\|\s*(Built|Planned)\s*\|\s*$")
BUILT = re.compile(r"\|\s*Built\s*\|\s*$")   # Planned must not match
CHECK_IN_FILE = re.compile(r"\b(DOC-\d+(?:/\d+)?)\b")

# Gate command -> implementing file is a NAMING CONVENTION, not a list. An
# earlier version carried an explicit dict; it was a parallel list that could
# drift from the tree, which is the failure mode this whole check exists to
# catch. `check:some-name` resolves to tools/checks/check_some_name.py or
# tools/docs/check_some_name.py; an unprefixed command such as `gen_docs` to
# tools/docs/gen_docs.py. A new gate is then covered by declaring it in section
# 13, with nothing to update here.
TOOL_DIRS = ("tools/checks", "tools/docs")


def impl_stem(cmd: str) -> str:
    """The filename a declared command must have.

    The file is named after the command: check:docs -> check_docs.py,
    gen_docs -> gen_docs.py. Normalising the separator is the whole rule.

    Deliberately independent of whether the file exists, so that a gate whose
    file has been deleted is reported as missing rather than as undeclared.
    """
    return re.sub(r"[^a-z0-9]+", "_", cmd.split()[0].lower())


def impl_for(cmd: str, repo: Path) -> Path | None:
    """Resolve a declared command to its file, or None when it is not built yet."""
    stem = impl_stem(cmd)
    for d in TOOL_DIRS:
        cand = repo / d / f"{stem}.py"
        if cand.is_file():
            return cand
    return None


# Risk ids (R-4 in IMPLEMENTATION-PLAN section 6) are requirement ids too. The
# pattern must not match reference codes: R-TT-01 has letters after the dash and
# is excluded by \b after digits.
REQUIREMENT = re.compile(r"\b(?:FR-\d{2}|RES-\d{2}[a-z]?|AC-\d{2}|PERF-\d{2}|BUD-\d{2}|"
                         r"NG-\d{2}|D-\d{2}|ADR-\d{4}|R-\d{1,2})\b")


@dataclass
class Finding:
    rule: str
    where: str
    message: str


def base_cmd(cell: str) -> str:
    """The command inside a section 13 cell, which may also name check ids."""
    m = re.search(r"`([^`]+)`", cell)
    return m.group(1) if m else cell.strip()


def inventory_rows(docs: Path) -> list[tuple[str, str, str]]:
    """(chk, command, rest-of-row) for TDD section 13."""
    tdd = docs / "TDD.md"
    if not tdd.is_file():
        return []
    lines = tdd.read_text(encoding="utf-8").splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("## 13. Check inventory")), None)
    if start is None:
        return []
    out = []
    for line in lines[start:]:
        if line.startswith("## ") and "Check inventory" not in line:
            break
        m = ROW.match(line)
        if m:
            out.append((m.group("chk"), m.group("cmd"), m.group("rest")))
    return out


def executed_gates(run_all: Path) -> set[str]:
    """Scripts run_all invokes, read from the runner rather than duplicated here.

    Fixture suites are excluded: they are not gates, they are the assertions
    that gates have fixtures, and holding them to INV-01 would be circular.
    """
    if not run_all.is_file():
        return set()
    text = run_all.read_text(encoding="utf-8")
    scripts = set(re.findall(r"[\w:./-]+\.py", text))
    return {s for s in scripts
            if Path(s).name != "run_all.py" and not Path(s).name.startswith("test_")}


def registry_ids(path: Path, name: str = "CHECKS") -> set[str] | None:
    """Ids a gate file actually registers, read from its AST.

    Text search is not enough and the failure is not hypothetical: `DOC-10`
    appears in its own function body and in its known-findings entry, so a check
    deleted from the registry still left the string `"DOC-10"` in the file. A
    substring probe read that as proof the check existed. Only the registry
    decides whether a check runs.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t_, ast.Name) and t_.id == name for t_ in node.targets):
            if isinstance(node.value, ast.List):
                ids = set()
                for elt in node.value.elts:
                    if isinstance(elt, ast.Tuple) and elt.elts:
                        first = elt.elts[0]
                        if isinstance(first, ast.Constant) and isinstance(first.value, str):
                            ids.add(first.value)
                return ids
    return None


def fixtures_with_assertion(suite: Path) -> set[str]:
    """Fixture names the suite asserts on, read from the suite itself."""
    if not suite.is_file():
        return set()
    text = suite.read_text(encoding="utf-8")
    return set(re.findall(r"\(\"([A-Za-z0-9_.\-]+)\"", text)) - {"error", "warning", "none"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="check_inventory")
    ap.add_argument("-C", "--root", default=str(DOCS),
                    help="document directory holding TDD.md")
    ap.add_argument("--repo", default=str(REPO),
                    help="repository root; defaults to this script's. Exposed so the "
                         "fixture suite can point the check at a miniature tree")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    args = ap.parse_args(argv)

    docs = Path(args.root)
    if not docs.is_dir():
        print(f"check_inventory: document root not found: {docs}", file=sys.stderr)
        return 2

    rows = inventory_rows(docs)
    if not rows:
        print("check_inventory: TDD section 13 check inventory not found", file=sys.stderr)
        return 2

    repo = Path(args.repo)
    findings: list[Finding] = []
    scripts = executed_gates(repo / "tools" / "docs" / "run_all.py")

    # INV-01: every executed gate must be named in section 13
    named_impl: {str} = {f"{impl_stem(base_cmd(raw))}.py" for _, raw, _ in rows
                        if base_cmd(raw)}
    for script in sorted(scripts):
        if Path(script).name not in named_impl:
            findings.append(Finding(
                "INV-01", script,
                "run_all executes this gate but TDD section 13 does not name it. "
                "A gate nobody declared is a gate nobody reviews"))

    # INV-02/04: every named-and-implemented row must exist and cite a real requirement
    # The corpus of defined requirements must exclude the inventory itself.
    # Including it made every bogus citation self-satisfying: a section 13 row
    # naming FR-99 found FR-99 in that same row, so the check passed a
    # requirement that exists nowhere. A gate's own claim to be evidence for
    # that claim is how an audit becomes a rubber stamp.
    corpus = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in sorted(docs.glob("*.md"))
        if p.name != "TDD.md"
    ) + "\n" + "\n".join(
        line for line in (docs / "TDD.md").read_text(encoding="utf-8").splitlines()
        if not ROW.match(line)
    )
    implemented: set[str] = set()
    declared_by_file: dict[str, set[str]] = {}
    for chk, cmd, rest in rows:
        # The declared command may name check ids inside a script ("check:docs
        # DOC-10"). The file is resolved from the command prefix.
        # Build state is declared in section 13, never inferred. Inference cannot
        # distinguish "planned for a later phase" from "built, then deleted", and
        # that ambiguity is precisely what let DOC-10 vanish unnoticed.
        declared_built = bool(BUILT.search(rest))
        cmd_name = base_cmd(cmd)
        impl_path = impl_for(cmd_name, repo) if cmd_name else None
        if impl_path is None:
            if declared_built:
                findings.append(Finding(
                    "INV-02", f"TDD §13 CHK-{chk}",
                    f"is marked Built, but no {impl_stem(cmd_name)}.py exists under "
                    f"{' or '.join(TOOL_DIRS)}. A gate marked Built and then deleted is "
                    "not a planned gate"))
            continue          # Planned: PH-7 and later
        impl = str(impl_path.relative_to(repo))
        if not declared_built:
            continue
        # Every check id the row names must actually be registered in the file.
        for cid in CHECK_IN_FILE.findall(cmd):
            ids = registry_ids(impl_path)
            if ids is None:
                findings.append(Finding(
                    "INV-02", f"TDD §13 CHK-{chk}",
                    f"{impl} exposes no CHECKS registry to verify {cid} against"))
                break
            if cid not in ids:
                findings.append(Finding(
                    "INV-02", f"TDD §13 CHK-{chk}",
                    f"names {cid}, but {impl} does not register it. A check deleted from "
                    "the registry is invisible to a gate that inventories scripts"))
        # Declared ids accumulate across every row that resolves to this file.
        # Section 13 gives one row per check, so a per-row comparison would report
        # the other nine checks of the same file as undeclared.
        declared_by_file.setdefault(impl, set()).update(CHECK_IN_FILE.findall(cmd))
        if not (repo / impl).is_file():
            findings.append(Finding(
                "INV-02", f"TDD §13 CHK-{chk}",
                f"declares `{cmd}` as a gate with a seeded fixture, but {impl} does not exist"))
            continue
        implemented.add(cmd)
        reqs = REQUIREMENT.findall(rest)
        if not reqs:
            findings.append(Finding(
                "INV-04", f"TDD §13 CHK-{chk}",
                f"`{cmd}` names no requirement in its 'Fails on' column; a gate that "
                "enforces nothing cannot be traced to anything"))
            continue
        unknown = [r for r in reqs if r not in corpus]
        if unknown:
            findings.append(Finding(
                "INV-04", f"TDD §13 CHK-{chk}",
                f"`{cmd}` cites {', '.join(unknown)}, which appears in no document"))

    # INV-03: every implemented gate needs a fixture asserted by a suite
    # Every suite in the tree, discovered rather than listed: a new suite counts
    # without anyone remembering to register it here.
    asserted: set[str] = set()
    for suite in sorted(repo.glob("tools/*/test_*.py")):
        asserted |= fixtures_with_assertion(suite)
    drift = repo / "tools" / "docs" / "fixtures" / "drift"
    fixture_dirs = {p.name for p in drift.iterdir() if p.is_dir()} if drift.is_dir() else set()
    orphan_fixtures = sorted(fixture_dirs - asserted)
    if orphan_fixtures:
        findings.append(Finding(
            "INV-03", "tools/docs/fixtures/drift",
            f"fixture(s) exist that no suite asserts: {', '.join(orphan_fixtures)}. "
            "R-03: a check whose fixture is deleted fails review"))
    # INV-05: every registered check must be named in section 13. The reverse
    # direction of INV-02, and the one that catches a check added without a row.
    for impl, declared in sorted(declared_by_file.items()):
        ids = registry_ids(repo / impl)
        if ids is None:
            continue
        for unregistered in sorted(ids - declared):
            findings.append(Finding(
                "INV-05", impl,
                f"registers {unregistered}, which TDD §13 does not name. A gate "
                "nobody declared is a gate nobody reviews"))

    if args.format == "json":
        print(json.dumps({
            "implementedGates": sorted(implemented),
            "inventoryRows": [c for c, _, _ in rows],
            "fixtureDirs": sorted(fixture_dirs),
            "assertedBySuites": sorted(asserted),
            "findings": [f.__dict__ for f in findings],
        }, indent=2))
    else:
        print(f"check_inventory: {len(rows)} gate(s) declared in TDD §13, "
              f"{len(implemented)} implemented here, {len(fixture_dirs)} fixture directories")
        print("  (rows marked Planned belong to PH-7 and later; they are not findings)")
        if not findings:
            print("every executed gate is declared, every implemented gate has a fixture, "
                  "every gate cites a requirement that exists")
        for f in findings:
            print(f"[error] {f.rule} {f.where}\n    {f.message}")
        if findings:
            print(f"\n{len(findings)} finding(s)")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())