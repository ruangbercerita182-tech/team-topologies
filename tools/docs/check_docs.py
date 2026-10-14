#!/usr/bin/env python3
"""check_docs — mechanical coherence gate for the CMS document set.

Scope (ADR-0028 candidate, Tier A only):
  Facts that are DERIVABLE from another file in the repo are checked here.
  Facts that are authored (rationale, intent, budgets-in-prose) are not.

Every check must be provable from files on disk. A check whose verdict
depends on parsing English prose is NOT implemented; see KNOWN_BLIND_SPOTS.

Exit codes:
  0  no findings above threshold
  1  findings above threshold
  2  configuration or usage error  (never a finding — a typo must not
     be able to mask real drift behind a green build)

Standard library only. No dependency may become a reason a build breaks.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}

# Checks that sound plausible but were rejected during design. Recorded so
# the absence is a decision on the record, not an oversight.
KNOWN_BLIND_SPOTS = [
    {
        "id": "DOC-90",
        "wanted": "flag an ADR that cites a REJECTED reference entry",
        "why_not": (
            "references.md encodes status as prose inside a free-text column, "
            "not as a field. A substring scan for 'REJECTED' produced 12 hits, "
            "of which 11 were false positives: R-SOLID-09 is cited in PRD.md:664 "
            "and adr/0011:21 precisely to say it must never be cited, and "
            "R-SEC-01 is VERIFIED while its row merely mentions the word "
            "'REJECTED' in prose ('already listed as REJECTED in R-23'). "
            "Until status becomes a machine-readable field this check cannot "
            "be made sound, and a noisy gate gets switched off."
        ),
        "unblocks": "make reference status a field (ADR-0028 / references.md schema)",
    },
    {
        "id": "DOC-91",
        "wanted": "detect the same fact stated with two different values",
        "why_not": (
            "requires that the fact be keyed. Nothing in the current document "
            "set names which literal owns which fact, so there is no sound way "
            "to tell a contradiction from two legitimately-scoped statements."
        ),
        "unblocks": "ADR-0028 — model owns the value, prose states the rule",
    },
]


@dataclass
class Finding:
    check: str
    severity: str
    path: str
    line: int
    message: str
    evidence: str = ""

    def render(self) -> str:
        loc = f"{self.path}:{self.line}" if self.line else self.path
        head = f"[{self.severity}] {self.check} {loc}"
        out = f"{head}\n    {self.message}"
        if self.evidence:
            out += f"\n    saw: {self.evidence}"
        return out


@dataclass
class Corpus:
    root: Path
    files: list[Path] = field(default_factory=list)
    text: dict[Path, str] = field(default_factory=dict)
    adrs: list[Path] = field(default_factory=list)


def slugify_heading(text: str) -> str:
    """GitHub heading-slug rules, reduced to what this corpus needs."""
    text = unicodedata.normalize("NFKD", text).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def anchors_of(markdown: str) -> set[str]:
    out: set[str] = set()
    in_fence = False
    for raw in markdown.splitlines():
        if re.match(r"^\s*(```|~~~)", raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", raw)
        if m:
            out.add(slugify_heading(m.group(2)))
    return out


def load(root: Path) -> Corpus:
    files = sorted(
        p for p in root.rglob("*.md")
        if ".git" not in p.parts and "node_modules" not in p.parts
    )
    c = Corpus(root=root, files=files)
    for p in files:
        try:
            c.text[p] = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            c.text[p] = p.read_text(encoding="utf-8", errors="replace")
    c.adrs = [p for p in files if p.parent.name == "adr" and re.match(r"^\d{4}-", p.name)]
    return c


def rel(c: Corpus, p: Path) -> str:
    try:
        return str(p.relative_to(c.root))
    except ValueError:
        return str(p)


# --------------------------------------------------------------------------
# DOC-01  every cited R-xx resolves in the catalogue
# --------------------------------------------------------------------------
def doc_01_references(c: Corpus) -> list[Finding]:
    cat = c.root / "references.md"
    if not cat.exists():
        return [Finding("DOC-01", "error", "references.md", 0,
                        "catalogue missing; cannot resolve any citation")]
    defined: set[str] = set()
    for line in c.text[cat].splitlines():
        m = re.match(r"\|\s*`?(R-[A-Z]+-\d+)`?\s*\|", line)
        if m:
            defined.add(m.group(1))

    out: list[Finding] = []
    for p in c.files:
        if p == cat:
            continue
        for i, line in enumerate(c.text[p].splitlines(), 1):
            for rid in re.findall(r"\bR-[A-Z]+-\d+\b", line):
                if rid not in defined:
                    out.append(Finding(
                        "DOC-01", "error", rel(c, p), i,
                        f"cited {rid} is not defined in references.md",
                        line.strip()[:160],
                    ))
    return out


# --------------------------------------------------------------------------
# DOC-02 / DOC-03  local markdown links resolve, including anchors
# --------------------------------------------------------------------------
LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def doc_02_03_links(c: Corpus) -> list[Finding]:
    out: list[Finding] = []
    for p in c.files:
        in_fence = False
        for i, line in enumerate(c.text[p].splitlines(), 1):
            if re.match(r"^\s*(```|~~~)", line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in LINK.findall(line):
                if re.match(r"^(https?:|mailto:|tel:)", target) or target.startswith("#"):
                    continue
                path_part, _, frag = target.partition("#")
                if not path_part:
                    continue
                dest = (p.parent / path_part).resolve()
                if not dest.exists():
                    out.append(Finding(
                        "DOC-02", "error", rel(c, p), i,
                        f"link target does not exist: {path_part}",
                        line.strip()[:160],
                    ))
                    continue
                if frag and dest.suffix.lower() == ".md" and dest.is_file():
                    try:
                        headings = anchors_of(dest.read_text(encoding="utf-8", errors="replace"))
                    except OSError:
                        continue
                    if slugify_heading(frag) not in headings:
                        out.append(Finding(
                            "DOC-03", "warning", rel(c, p), i,
                            f"anchor '#{frag}' has no heading in {path_part}",
                            line.strip()[:160],
                        ))
    return out


# --------------------------------------------------------------------------
# DOC-04  ADR count and range claims match the files actually present
# --------------------------------------------------------------------------
ADR_RANGE = re.compile(r"ADR-(\d{4})\s*(?:…|\.\.\.|–|-|to)\s*ADR-(\d{4})")

# Count claims only count in a line that is actually talking about the ADR set.
# Without that guard this fires on "R-BUILD-40 records that ..." and on
# "3 recorded data points", both of which were observed false positives.
ADR_COUNT = re.compile(
    r"(?<![\w-])(\d{1,3})\s+(?:accepted\s+)?(?:ADRs?|decision\s+records?|records?)(?![\w-])",
    re.I,
)
ADR_CONTEXT = re.compile(r"\bADR|adr/", re.I)


def doc_04_adr_claims(c: Corpus) -> list[Finding]:
    if not c.adrs:
        return [Finding("DOC-04", "error", "adr/", 0, "no ADR files found")]
    nums = sorted(int(p.name[:4]) for p in c.adrs)
    lo, hi = nums[0], nums[-1]
    count = len(c.adrs)

    out: list[Finding] = []
    for p in c.files:
        for i, line in enumerate(c.text[p].splitlines(), 1):
            for a, b in ADR_RANGE.findall(line):
                if int(a) != lo or int(b) != hi:
                    out.append(Finding(
                        "DOC-04", "error", rel(c, p), i,
                        f"claims the ADR set is {a}–{b}; on disk it is "
                        f"{lo:04d}–{hi:04d} ({count} records)",
                        line.strip()[:160],
                    ))
            if not ADR_CONTEXT.search(line):
                continue
            for n in ADR_COUNT.findall(line):
                if int(n) != count:
                    out.append(Finding(
                        "DOC-04", "warning", rel(c, p), i,
                        f"claims {n} records; {count} exist on disk",
                        line.strip()[:160],
                    ))
    return out


# --------------------------------------------------------------------------
# DOC-05  every PRD decision is addressed by at least one ADR
# --------------------------------------------------------------------------
def _expand_dec(text: str) -> set[str]:
    """Collect DEC-nn mentions, expanding the DEC-a...DEC-b range shorthand."""
    found: set[str] = set()
    for a, b in re.findall(r"\bDEC-(\d{2})\s*(?:…|\.\.\.|–|-)\s*DEC-(\d{2})\b", text):
        lo, hi = int(a), int(b)
        if lo <= hi and hi - lo <= 32:
            found |= {f"DEC-{n:02d}" for n in range(lo, hi + 1)}
    found |= set(re.findall(r"\bDEC-\d{2}\b", text))
    return found


def _traceability_cells(c: Corpus) -> str:
    """Return only the DEC -> ADR traceability table of adr/README.md.

    Parsing the whole index file is unsound: its header states
    "Basis | PRD DEC-01...DEC-24", which is background, not a claim that
    those decisions are covered. Reading that row as coverage made DEC-05
    pass with DEC-10 demonstrably uncovered.
    """
    index = c.root / "adr" / "README.md"
    if not index.exists():
        return ""
    lines = c.text[index].splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.lstrip("# ").lower().startswith("traceability"):
            start = i
            break
    if start is None:
        return ""
    cells: list[str] = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        m = re.match(r"^\|\s*([^|]+?)\s*\|", line)
        if m and "ADR" not in m.group(1):
            cells.append(m.group(1))
    return "\n".join(cells)


def _closes_decls(c: Corpus) -> set[str]:
    """DEC-nn asserted by an ADR's own 'Closes:' assertion line."""
    out: set[str] = set()
    for a in c.adrs:
        for line in c.text[a].splitlines():
            if "Closes:" in line:
                out |= set(re.findall(r"\bDEC-\d{2}\b", line))
    return out


def doc_05_dec_coverage(c: Corpus) -> list[Finding]:
    prd = c.root / "PRD.md"
    if not prd.exists():
        return []
    decs = set(re.findall(r"\bDEC-\d{2}\b", c.text[prd]))
    if not decs:
        return []

    covered = _closes_decls(c) | _expand_dec(_traceability_cells(c))

    missing = sorted(decs - covered)
    if not missing:
        return []
    return [Finding(
        "DOC-05", "warning", "adr/", 0,
        f"{len(missing)} of {len(decs)} PRD decisions have no ADR: "
        f"{', '.join(missing)}",
        "adr/README.md:77 states every PRD decision maps to at least one ADR",
    )]


# --------------------------------------------------------------------------
# DOC-06  every TDD GAP is closed by an ADR
# --------------------------------------------------------------------------
def doc_06_gap_closure(c: Corpus) -> list[Finding]:
    tdd = c.root / "TDD.md"
    if not tdd.exists():
        return []
    gaps = set(re.findall(r"\bGAP-\d{2}\b", c.text[tdd]))
    if not gaps:
        return []
    closed: set[str] = set()
    for a in c.adrs:
        closed |= set(re.findall(r"\bGAP-\d{2}\b", c.text[a]))
    missing = sorted(gaps - closed)
    if not missing:
        return []
    return [Finding(
        "DOC-06", "error", "TDD.md", 0,
        f"{len(missing)} GAP(s) have no closing ADR: {', '.join(missing)}",
    )]


# --------------------------------------------------------------------------
# DOC-07  a gate has exactly one name across the document set
# --------------------------------------------------------------------------
KNOWN_ALIASES = {
    "check:pins": "pins:check",
    "check:catalog": "catalog:verify-ownership",
}


def doc_07_gate_names(c: Corpus) -> list[Finding]:
    out: list[Finding] = []
    for canonical, alias in KNOWN_ALIASES.items():
        hits: list[Finding] = []
        for p in c.files:
            for i, line in enumerate(c.text[p].splitlines(), 1):
                if re.search(rf"\b{re.escape(alias)}\b", line):
                    hits.append(Finding(
                        "DOC-07", "error", rel(c, p), i,
                        f"gate named '{alias}'; TDD §13 names this gate "
                        f"'{canonical}'. One gate, one name.",
                        line.strip()[:160],
                    ))
        if hits:
            out.append(Finding(
                "DOC-07", "error", "docs/", 0,
                f"'{alias}' and '{canonical}' both name the same gate",
                f"{len(hits)} occurrence(s) of '{alias}'; "
                f"see TECHNICAL-IMPLEMENTATION-PLAN.md §0.1",
            ))
    return out


CHECKS = [
    ("DOC-01", doc_01_references),
    ("DOC-02/03", doc_02_03_links),
    ("DOC-04", doc_04_adr_claims),
    ("DOC-05", doc_05_dec_coverage),
    ("DOC-06", doc_06_gap_closure),
    ("DOC-07", doc_07_gate_names),
]


def run(root: Path, fail_on: str) -> tuple[list[Finding], Corpus]:
    c = load(root)
    findings: list[Finding] = []
    for _name, fn in CHECKS:
        findings.extend(fn(c))
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.check, f.path, f.line))
    # "none" means report everything unthresholded -- this is the mode used to
    # capture a baseline, so filtering it down to errors would hide exactly
    # the warnings being baselined.
    if fail_on == "none":
        return findings, c
    threshold = SEVERITY_ORDER.get(fail_on)
    if threshold is None:
        return findings, c
    return [f for f in findings if SEVERITY_ORDER.get(f.severity, 9) <= threshold], c


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="check_docs")
    ap.add_argument("-C", "--root", default="docs", help="document root (default: docs)")
    ap.add_argument("--fail-on", default="error",
                    choices=["error", "warning", "info", "none"],
                    help="lowest severity that fails the build (default: error)")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    ap.add_argument("--list-blind-spots", action="store_true")
    args = ap.parse_args(argv)

    if args.list_blind_spots:
        print(json.dumps(KNOWN_BLIND_SPOTS, indent=2))
        return 0

    root = Path(args.root)
    if not root.is_dir():
        print(f"check_docs: document root not found: {root}", file=sys.stderr)
        return 2

    try:
        findings, corpus = run(root, args.fail_on)
    except OSError as exc:
        print(f"check_docs: cannot read corpus: {exc}", file=sys.stderr)
        return 2

    blocking = [f for f in findings if f.severity != "info"]

    if args.format == "json":
        print(json.dumps({
            "root": str(root),
            "documents": len(corpus.files),
            "adrs": len(corpus.adrs),
            "failOn": args.fail_on,
            "findings": [f.__dict__ for f in findings],
            "blindSpots": KNOWN_BLIND_SPOTS,
        }, indent=2))
    else:
        print(f"check_docs: {len(corpus.files)} documents, {len(corpus.adrs)} ADR records, root={root}")
        if not findings:
            print("clean")
        else:
            for f in findings:
                print(f.render())
            print(f"\n{len(findings)} finding(s); "
                  f"{len(KNOWN_BLIND_SPOTS)} declared blind spot(s)")

    if args.fail_on == "none":
        return 0
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())