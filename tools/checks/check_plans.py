#!/usr/bin/env python3
"""check_plans — make phase entry criteria verifiable.

TIMP-CMS-001 §14 records the defect this checks: PH-1's entry criterion is the
phrase "plan accepted", which has no command and therefore no exit code. The
programme's own standard (IMPLEMENTATION-PLAN.md §4, risk R-4) is that "every
exit criterion is a command with an exit code; a verbal exit is not an exit" —
and the entry criterion of the first phase did not meet the standard the plan
sets for everything after it.

Two things are checked:

1. **Verifiability.** Every phase entry and exit criterion must contain a command
   or a measurable condition. A phrase like "plan accepted" or "ready" is
   reported, because the next person cannot tell a satisfied criterion from an
   assumed one.

2. **Acceptance state.** Every artefact declares a status, and this reports which
   are approved and which are still proposed. It does not decide acceptance: an
   artefact is accepted by its accountable role signing for it, and a check that
   marks a plan accepted would forge that. It reports the state so the blocker
   is visible, including when a phase depends on a plan that is not yet approved.

Exit codes: 0 clean, 1 findings, 2 configuration or usage error.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "docs"))
from check_docs import _artefact_header  # noqa: E402

# A criterion is verifiable if it names a command or a measurable condition.
COMMAND_HINT = re.compile(r"`[^`]+`|\b(?:exit|exits|returns|nothing|exactly|zero|contains|passes|fails|exists|declared)\b", re.I)

# Phrases that assert a state without a way to observe it. Matched case-insensitively
# against the whole criterion cell.
UNVERIFIABLE = re.compile(
    r"\b(plan accepted|accepted|approved|agreed|signed off|ready|when ready|"
    r"as appropriate|if needed|reviewed|validated)\b",
    re.I,
)
# ...unless the sentence also carries a command, in which case the command is
# what makes it verifiable and the word is describing the command's outcome.
HAS_COMMAND = re.compile(r"`[^`]+`|\$\s|\bexit code\b|\bexits?\b|\breturns?\b", re.I)

APPROVED = ("approved for implementation", "approved", "accepted", "active")


@dataclass
class Finding:
    rule: str
    where: str
    message: str
    detail: str = ""


def artefact_states(docs: Path) -> dict[str, tuple[str, str, str]]:
    out: dict[str, tuple[str, str, str]] = {}
    for p in sorted(docs.glob("*.md")):
        h = _artefact_header(p, p.read_text(encoding="utf-8"))
        if "Document ID" not in h:
            continue
        out[_clean(h["Document ID"][1])] = (
            _clean(h.get("Status", ("", "—"))[1]),
            _clean(h.get("Accountable", ("", ""))[1]),
            str(p.relative_to(docs)),
        )
    return out


def _clean(v: str) -> str:
    return re.sub(r"\s+", " ", v.replace("**", "").replace("`", "")).strip()


def check_criteria(plan: Path) -> list[Finding]:
    """Every phase entry/exit criterion must be observable."""
    out: list[Finding] = []
    lines = plan.read_text(encoding="utf-8").splitlines()
    header_idx = None
    for i, l in enumerate(lines):
        if l.startswith("| Phase |") or (l.startswith("|") and "Entry criterion" in l):
            header_idx = i
            break
    if header_idx is None:
        return [Finding("PLANS-01", str(plan.name), "phase table not found; entry criteria unverified")]

    cols = [c.strip() for c in lines[header_idx].strip("|").split("|")]
    try:
        phase_i = cols.index("Phase")
        entry_i = next(i for i, c in enumerate(cols) if "Entry" in c)
        exit_i = next(i for i, c in enumerate(cols) if "Exit" in c)
    except (ValueError, StopIteration):
        return [Finding("PLANS-01", str(plan.name), f"cannot locate Phase/Entry/Exit columns in {cols}")]

    for n, line in enumerate(lines[header_idx + 1:], start=header_idx + 2):
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) <= exit_i or set(cells[0]) <= set("-: "):
            continue
        phase = cells[phase_i].replace("*", "")
        for label, cell in (("entry", cells[entry_i]), ("exit", cells[exit_i])):
            text = re.sub(r"\*\*|`", "", cell).strip()
            if not text:
                continue
            if UNVERIFIABLE.search(text) and not HAS_COMMAND.search(cell):
                out.append(Finding(
                    "PLANS-01", f"{plan.name}:{n}",
                    f"{phase} {label} criterion is not observable: {text!r}",
                    "an entry criterion with no command cannot be distinguished from an assumed one",
                ))
            elif not COMMAND_HINT.search(cell):
                out.append(Finding(
                    "PLANS-02", f"{plan.name}:{n}",
                    f"{phase} {label} criterion names no command or measurable condition",
                    text[:120],
                ))
    return out


def check_acceptance(docs: Path, states: dict) -> list[Finding]:
    """Report plans that are not yet approved, so the blocker is visible."""
    out: list[Finding] = []
    for doc_id, (status, owner, path) in sorted(states.items()):
        if any(a in status.lower() for a in APPROVED):
            continue
        out.append(Finding(
            "PLANS-03", f"{path} ({doc_id})",
            f"status is {status!r}; phases whose entry criterion requires an accepted plan are blocked",
            f"accountable: {owner or '—'}",
        ))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="check_plans")
    ap.add_argument("-C", "--root", default="docs")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    # PLANS-03 is a governance state, not a defect. An unapproved plan does not
    # become correct by failing CI every day -- and a gate that is permanently
    # red gets switched off. So it is reported, and PLANS-01/02 (criteria that
    # cannot be observed at all) are what gate. --strict makes acceptance gate too.
    ap.add_argument("--strict", action="store_true",
                    help="also fail when a plan is still Proposed (PLANS-03)")
    ap.add_argument("--report-only", action="store_true",
                    help="alias for the default: report acceptance without failing")
    args = ap.parse_args(argv)

    docs = Path(args.root)
    if not docs.is_dir():
        print(f"check_plans: document root not found: {docs}", file=sys.stderr)
        return 2

    plan = docs / "IMPLEMENTATION-PLAN.md"
    if not plan.is_file():
        print(f"check_plans: {plan} not found", file=sys.stderr)
        return 2

    try:
        states = artefact_states(docs)
    except OSError as exc:
        print(f"check_plans: cannot read document set: {exc}", file=sys.stderr)
        return 2

    findings = check_criteria(plan)
    acceptance = check_acceptance(docs, states)
    if args.strict and not args.report_only:
        findings += acceptance

    if args.format == "json":
        print(json.dumps({
            "findings": [f.__dict__ for f in findings],
            "acceptanceState": {k: {"status": v[0], "accountable": v[1], "path": v[2]}
                               for k, v in states.items()},
        }, indent=2))
    else:
        print(f"check_plans: {plan}")
        if args.report_only:
            print("acceptance state (report only):")
            for doc_id, (status, owner, _) in sorted(states.items()):
                mark = "ok " if any(a in status.lower() for a in APPROVED) else "   "
                print(f"  {mark}{doc_id:22} {status[:44]:46} {owner[:28]}")
            print()
        pending = [f for f in acceptance]
        if not findings:
            print("every phase criterion is observable")
        if pending and not findings:
            print(f"{len(pending)} plan(s) still Proposed -- reported, not a failure unless --strict")
        for f in findings:
            print(f"[error] {f.rule} {f.where}\n    {f.message}")
            if f.detail:
                print(f"    {f.detail}")
        if findings:
            print(f"\n{len(findings)} finding(s)")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())