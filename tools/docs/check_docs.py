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
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}

# Checks that sound plausible but were rejected during design. Recorded so
# the absence is a decision on the record, not an oversight.
KNOWN_BLIND_SPOTS = [
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
    present = set(nums)
    for p in c.files:
        for i, line in enumerate(c.text[p].splitlines(), 1):
            for a, b in ADR_RANGE.findall(line):
                a, b = int(a), int(b)
                if a > b:
                    continue
                # A range whose lower bound is 0001 claims the whole set, so it
                # must end at the highest record. A range starting above 0001 is
                # a partial claim ("0013...0028 were written afterwards") and is
                # checked for existence only -- an earlier draft of this check
                # compared every range against the full set and reported correct
                # prose as a contradiction.
                if a == lo and b != hi:
                    out.append(Finding(
                        "DOC-04", "error", rel(c, p), i,
                        f"claims the ADR set is {a:04d}–{b:04d}; on disk it is "
                        f"{lo:04d}–{hi:04d} ({count} records)",
                        line.strip()[:160],
                    ))
                    continue
                missing = [n for n in range(a, b + 1) if n not in present]
                if missing:
                    out.append(Finding(
                        "DOC-04", "error", rel(c, p), i,
                        f"claims the range {a:04d}–{b:04d}, but "
                        + ", ".join(f"{n:04d}" for n in missing)
                        + " do not exist",
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
def _generated_block(c: Corpus, path: Path, name: str) -> str | None:
    """Body of a named generated block, or None if absent.

    A checker that validates generated output is the other half of generating
    it. Where a block exists, the generated text is the authority; falling back
    to hand-written prose would let the two disagree and only one be checked.
    """
    src = c.root / path
    if not src.is_file():
        return None
    m = re.search(
        rf"<!-- BEGIN GENERATED: {re.escape(name)}\b[^\n]*-->\n(.*?)<!-- END GENERATED: {re.escape(name)} -->",
        c.text[src], re.S,
    )
    return m.group(1) if m else None


def _claims_from_field(a_text: str) -> set[str]:
    """DEC ids in a cell, expanding the DEC-a...DEC-b range shorthand.

    Range expansion is not optional. Without it 'DEC-17...DEC-19' yields
    {DEC-17, DEC-19} and DEC-18 is reported uncovered, which is exactly the
    class of false positive this check already produced once before.
    """
    found: set[str] = set()
    for a, b in re.findall(r"\bDEC-(\d{2})\s*(?:…|\.\.\.|–|-)\s*DEC-(\d{2})\b", a_text):
        lo, hi = int(a), int(b)
        if lo <= hi and hi - lo <= 32:
            found |= {f"DEC-{n:02d}" for n in range(lo, hi + 1)}
    found |= set(re.findall(r"\bDEC-\d{2}\b", a_text))
    return found


def doc_05_dec_coverage(c: Corpus) -> list[Finding]:
    prd = c.root / "PRD.md"
    if not prd.exists():
        return []
    decs = set(re.findall(r"\bDEC-\d{2}\b", c.text[prd]))
    if not decs:
        return []

    index = "adr/README.md"

    # Authority: the generated traceability block, when present.
    generated = _generated_block(c, Path(index), "adr-traceability")
    if generated is not None:
        derived: set[str] = set()
        for line in generated.splitlines():
            if not line.startswith("|"):
                continue
            cells = [x.strip() for x in line.strip("|").split("|")]
            if len(cells) < 2 or cells[0] == "PRD decision":
                continue
            derived |= _claims_from_field(cells[0])
        # The authored section below the generated block is Tier B by ADR-0028.
        # It is a claim, not a derivation, so a decision covered only there is
        # reported as authored rather than counted as derived coverage.
        authored_only = _authored_claims(c, index)
        missing = sorted(decs - derived - authored_only)
        if not missing:
            return []
        return [Finding(
            "DOC-05", "warning", index, 0,
            f"{len(missing)} of {len(decs)} PRD decisions are claimed by neither the "
            f"generated traceability nor the authored table: {', '.join(missing)}",
            "adr/README.md asserts every PRD decision maps to at least one ADR",
        )]

    # Fallback for a corpus with no generated block yet.
    covered: set[str] = set()
    for a in c.adrs:
        for line in c.text[a].splitlines():
            if "Closes:" in line:
                covered |= set(re.findall(r"\bDEC-\d{2}\b", line))
    missing = sorted(decs - covered)
    if not missing:
        return []
    return [Finding(
        "DOC-05", "warning", index, 0,
        f"{len(missing)} of {len(decs)} PRD decisions have no ADR: {', '.join(missing)}",
        "adr/README.md asserts every PRD decision maps to at least one ADR",
    )]


def _authored_claims(c: Corpus, index: str) -> set[str]:
    """DEC ids covered only by the authored, non-derivable mappings."""
    src = c.root / index
    if not src.is_file():
        return set()
    text = c.text[src]
    heading = "### Editorial mappings not derivable from any record"
    if heading not in text:
        return set()
    seg = text.split(heading, 1)[1]
    seg = seg.split("\n## ", 1)[0]
    out: set[str] = set()
    for line in seg.splitlines():
        if not line.startswith("|"):
            continue
        cells = [x.strip() for x in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] == "PRD decision":
            continue
        out |= _claims_from_field(cells[0])
    return out


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


# --------------------------------------------------------------------------
# DOC-08  the artefact index agrees with the artefacts themselves
# --------------------------------------------------------------------------
# README.md §2 is a hand-maintained table of (artefact, id, version, status,
# accountable). Every one of those five values is already declared by the
# artefact in its own "| Field | Value |" header block, so the table is
# derivable and can be checked. This is the Tier A case ADR-0028 would fix
# by generating it; until then it is at least checked.

HEADER_FIELDS = ("Document ID", "Version", "Status", "Accountable", "Owner")


def _clean(v: str) -> str:
    v = v.replace("**", "").replace("`", "").strip()
    return re.sub(r"\s+", " ", v)


def _head_role(v: str) -> str:
    """First clause of an accountable value.

    '**DevOps lead**; Technical Lead co-signs application order' and
    'DevOps lead (TL co-signs app order)' both reduce to 'DevOps lead'.
    Comparing full strings produced a false positive on exactly that pair.
    """
    v = _clean(v)
    for sep in (";", "(", "—", "–"):
        v = v.split(sep)[0]
    return v.strip().rstrip(",").strip().lower()


def _artefact_header(p: Path, text: str) -> dict[str, tuple[int, str]]:
    """Parse the leading '| Field | Value |' block of a document.

    The block sits below the H1 title, so non-table lines are skipped until
    the table opens; only a non-blank line after it has opened ends the
    parse. Breaking on the first non-table line found the title instead.
    """
    out: dict[str, tuple[int, str]] = {}
    seen_table = False
    for i, line in enumerate(text.splitlines(), 1):
        if not line.startswith("|"):
            if seen_table and line.strip():
                break
            continue
        seen_table = True
        cells = [_clean(c) for c in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] == "Field" or set(cells[0]) <= set("-: "):
            continue
        for field in HEADER_FIELDS:
            if cells[0] == field and field not in out:
                out[field] = (i, cells[1])
    return out


def _index_rows(c: Corpus) -> list[tuple[int, list[str]]]:
    """Rows of the artefact index table in README.md section 2."""
    readme = c.root / "README.md"
    if not readme.exists():
        return []
    lines = c.text[readme].splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and "artefact index" in line.lower():
            start = i
            break
    if start is None:
        return []
    rows: list[tuple[int, list[str]]] = []
    # start at the line AFTER the matched heading: the heading itself matches
    # the "## " terminator below and would end the scan immediately.
    for i in range(start + 1, min(start + 40, len(lines))):
        line = lines[i]
        if line.startswith("## "):
            break
        if not line.startswith("|"):
            continue
        cells = [_clean(c) for c in line.strip("|").split("|")]
        if len(cells) < 5 or cells[1] == "ID":
            continue
        if all(set(x) <= set("-: ") for x in cells[:5]):
            continue
        rows.append((i + 1, cells))
    return rows


ID_RE = re.compile(r"\b([A-Z][A-Z-]+-CMS-\d{3})\b")


def _declares_owner(v: str) -> bool:
    """Is this accountable cell a real name, or an explicit 'none'?

    A leading em dash is how this corpus writes 'nobody owns this' -- the
    artefact index uses it for RACI-CMS-001. Treating the cell as a value made
    DOC-08 report '— unassigned; referred to PM' as an owner.
    """
    return _clean(v).strip() not in ("—", "-", "", "— unassigned; referred to PM") \
        and not _clean(v).lstrip().startswith(("—", "-"))


def doc_08_artefact_index(c: Corpus) -> list[Finding]:
    rows = _index_rows(c)
    if not rows:
        return [Finding("DOC-08", "error", "README.md", 0,
                        "artefact index table not found; rule README.md 5 is unverified")]

    artefacts: dict[str, tuple[Path, dict]] = {}
    for p in c.files:
        if p.parent.name == "adr":
            continue
        head = _artefact_header(p, c.text[p])
        if "Document ID" not in head:
            continue
        _, doc_id = head["Document ID"]
        m = ID_RE.search(doc_id)
        if not m:
            continue
        artefacts[m.group(1)] = (p, head)

    out: list[Finding] = []

    # duplicate ids
    seen: dict[str, Path] = {}
    for doc_id, (p, _h) in artefacts.items():
        if doc_id in seen:
            out.append(Finding(
                "DOC-08", "error", rel(c, p), 0,
                f"Document ID {doc_id} is also declared by {rel(c, seen[doc_id])}",
            ))
        seen[doc_id] = p

    indexed: set[str] = set()
    for line_no, cells in rows:
        name, id_cell, ver, status, owner = cells[0], cells[1], cells[2], cells[3], cells[4]
        ids = ID_RE.findall(id_cell)
        if not ids:
            continue  # range row (ADR-0001...ADR-0027) or prose; not a single artefact
        doc_id = ids[0]
        indexed.add(doc_id)
        if doc_id not in artefacts:
            out.append(Finding(
                "DOC-08", "error", "README.md", line_no,
                f"index registers {doc_id} ({name}) but no document declares it",
            ))
            continue

        p, head = artefacts[doc_id]

        for idx_cell, field in ((ver, "Version"), (status, "Status")):
            if field in head:
                declared = _clean(head[field][1])
                claimed = _clean(idx_cell)
                if claimed in ("—", "-", "") or declared in ("—", "-", ""):
                    continue
                if not (declared.lower().startswith(claimed.lower())
                        or claimed.lower().startswith(declared.lower())):
                    out.append(Finding(
                        "DOC-08", "error", rel(c, p), head[field][0],
                        f"index says {field} {claimed!r}; {rel(c, p)} declares {declared!r}",
                        f"README.md:{line_no}",
                    ))

        declared_owner = head.get("Accountable") or head.get("Owner")
        if declared_owner is None:
            if _declares_owner(owner):
                out.append(Finding(
                    "DOC-08", "warning", rel(c, p), 0,
                    f"index assigns accountable {owner!r} but {rel(c, p)} declares none",
                    f"README.md:{line_no}; RACI section 2 rule 1 "
                    f"(one accountable role per artefact) cannot be verified from the artefact",
                ))
        elif _declares_owner(owner):
            if _head_role(owner) != _head_role(declared_owner[1]):
                out.append(Finding(
                    "DOC-08", "error", rel(c, p), declared_owner[0],
                    f"index names accountable {owner!r}; {rel(c, p)} declares "
                    f"{declared_owner[1]!r}",
                    f"README.md:{line_no}",
                ))

    # artefacts that declare an id nobody registered
    for doc_id, (p, _h) in sorted(artefacts.items()):
        if doc_id not in indexed:
            out.append(Finding(
                "DOC-08", "warning", rel(c, p), 0,
                f"{doc_id} is not registered in the README.md artefact index",
                "README.md section 5 rule 5: register any new artefact and give it a <TYPE>-CMS-00n ID",
            ))
    return out


def doc_90_rejected_citation(c: Corpus) -> list[Finding]:
    """No document may cite a REJECTED reference entry.

    This is rule 2 of the ADR set and was unenforceable until
    references.md carried status as a field rather than as prose inside the
    "Establishes" column. The earlier substring scan produced 12 hits of which
    11 were false positives -- R-SOLID-09 is named in PRD.md and adr/0011
    precisely to forbid citing it, and R-SEC-01 is VERIFIED while its row
    mentions the word "REJECTED" in passing.

    Reading the Status column fixes the second case. The first case is a
    genuine, legitimate citation of a rejected entry, and is declared with the
    same in-document marker as any other suppression: a name and a reason.
    """
    cat = c.root / "references.md"
    if not cat.exists():
        return [Finding("DOC-90", "error", "references.md", 0,
                        "catalogue missing; rejected-citation rule cannot be checked")]

    status: dict[str, str] = {}
    for i, line in enumerate(c.text[cat].splitlines(), 1):
        if not line.startswith("|"):
            continue
        cells = [x.strip().replace("*", "").replace("`", "") for x in line.strip("|").split("|")]
        if len(cells) < 6 or not re.fullmatch(r"R-[A-Z]+-\d+", cells[0]):
            continue
        st = cells[4].upper()
        if st in ("VERIFIED", "PARTIAL", "REJECTED"):
            status[cells[0]] = st

    if not status:
        return [Finding("DOC-90", "error", "references.md", 0,
                        "no reference row carries a machine-readable Status; "
                        "the rejected-citation rule is unenforceable")]

    rejected = {r for r, s in status.items() if s == "REJECTED"}

    out: list[Finding] = []
    for p in c.files:
        if p == cat:
            continue
        allowed = allowances(c.text[p]).get("DOC-90")
        if allowed is not None and allowed.ids is None:
            continue  # unscoped: the whole file declares it reports rejected ids
        allowed_ids = allowed.ids if allowed else set()
        for i, line in enumerate(c.text[p].splitlines(), 1):
            for rid in (_refs_including_ranges(line) & rejected):
                if rid in allowed_ids:
                    continue
                out.append(Finding(
                    "DOC-90", "error", rel(c, p), i,
                    f"cites {rid}, which the catalogue marks REJECTED",
                    line.strip()[:160],
                ))
    return out


def _refs_including_ranges(line: str) -> set[str]:
    """R-ids a line cites, expanding 'R-BND-01 … R-BND-11' shorthand.

    Without expansion the check misses precisely the case that produced the
    original defect: PRD section 22 cited 'R-MFE-01 … R-MFE-23' with only the
    upper bound written out, so three rejected entries inside the range were
    never seen. Range handling has now been missed three times in this file --
    DOC-04, DOC-05 and now DOC-90 -- and is covered by fixtures each time.
    """
    found: set[str] = set()
    for m in re.finditer(r"\b(R-[A-Z]+-)(\d+)\s*(?:…|\.\.\.|–|-)\s*(R-[A-Z]+-)(\d+)\b", line):
        pre1, n1, pre2, n2 = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
        if pre1 != pre2 or not (0 <= n2 - n1 <= 256):
            continue
        found |= {f"{pre1}{n:02d}" for n in range(n1, n2 + 1)}
    found |= set(re.findall(r"\bR-[A-Z]+-\d+\b", line))
    return found


CHECKS = [
    ("DOC-01", doc_01_references),
    ("DOC-02/03", doc_02_03_links),
    ("DOC-04", doc_04_adr_claims),
    ("DOC-05", doc_05_dec_coverage),
    ("DOC-06", doc_06_gap_closure),
    ("DOC-07", doc_07_gate_names),
    ("DOC-08", doc_08_artefact_index),
    ("DOC-90", doc_90_rejected_citation),
]


ALLOW_MARKER = re.compile(
    r"<!--\s*check:docs:allow\s+(DOC-\d+(?:/\d+)?)\s+(.+?)\s*-->"
)


class Allowance:
    """A declared suppression: a reason, and optionally the ids it covers.

    Scoping matters. An unscoped marker silences every finding of that check in
    the file, which means the first legitimate non-citation in a large document
    disables the check for that document permanently -- including violations
    added later. Naming the ids keeps new ones failing.
    """

    __slots__ = ("check", "reason", "ids")

    def __init__(self, check: str, reason: str) -> None:
        self.check = check
        self.reason = reason
        ids = set(re.findall(r"\bR-[A-Z]+-\d+\b", reason))
        self.ids = ids or None


def allowances(text: str) -> dict[str, Allowance]:
    """Per-file suppressions declared by the document itself.

    A document that must report a defect has to reproduce the defect, and a
    string-scanning check cannot tell "this file asserts a stale value" from
    "this file explains a stale value". Telling them apart by parsing prose is
    forbidden by ADR-0028 rule 1, so the opt-out is explicit instead: a marker
    naming the check and a mandatory reason, in the file, visible in review.

    Suppressed findings are still reported, in their own section, so a
    suppression is never mistaken for a clean result.
    """
    out: dict[str, Allowance] = {}
    for m in ALLOW_MARKER.finditer(text):
        out[m.group(1)] = Allowance(m.group(1), m.group(2).strip())
    return out


def run(root: Path, fail_on: str) -> tuple[list[Finding], list[tuple[Finding, str]], Corpus]:
    c = load(root)
    findings: list[Finding] = []
    for _name, fn in CHECKS:
        findings.extend(fn(c))
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.check, f.path, f.line))

    suppressed: list[tuple[Finding, str]] = []
    kept: list[Finding] = []
    for f in findings:
        src = c.root / f.path
        marker = allowances(c.text[src]).get(f.check) if src.is_file() else None
        # An unscoped marker silences the check for the whole file and is
        # applied generically. A scoped marker names specific ids and belongs
        # to the check that understands those ids -- applying it generically
        # would suppress findings the check deliberately let through, which is
        # how a scoped marker silently became a whole-file opt-out.
        if marker is not None and marker.ids is None:
            suppressed.append((f, marker.reason))
        else:
            kept.append(f)

    # "none" means report everything unthresholded -- this is the mode used to
    # capture a baseline, so filtering it down to errors would hide exactly
    # the warnings being baselined.
    if fail_on != "none":
        threshold = SEVERITY_ORDER.get(fail_on)
        if threshold is not None:
            kept = [f for f in kept if SEVERITY_ORDER.get(f.severity, 9) <= threshold]
    return kept, suppressed, c


def finding_key(f: Finding) -> str:
    """Stable identity of a finding, so a baseline survives line-number churn."""
    return f"{f.check}|{f.path}|{f.message}"


def load_baseline(path: Path) -> tuple[set[str], str | None]:
    """Return (known finding keys, baseline of this run's source revision).

    The revision is recorded so a gate can tell "no new drift" from "nothing has
    ever been checked". A baseline with no revision is not a baseline.
    """
    if not path.exists():
        raise BaselineError(f"baseline file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BaselineError(str(exc)) from exc
    if "sourceRevision" not in data:
        raise BaselineError("baseline has no 'sourceRevision'; refusing to treat it as valid")
    return set(data.get("findings", [])), data.get("sourceRevision")


class BaselineError(Exception):
    """A malformed baseline is a configuration error, never a clean result."""


def git_revision(root: Path) -> str | None:
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return res.stdout.strip() or None


def write_baseline(path: Path, findings: list[Finding], revision: str | None) -> int:
    payload = {
        "note": "Known findings at adoption. check_docs fails only on NEW drift. "
                "Regenerate with --write-baseline once a finding is genuinely closed.",
        "sourceRevision": revision or "unknown",
        "findings": sorted(finding_key(f) for f in findings),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return len(payload["findings"])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="check_docs")
    ap.add_argument("-C", "--root", default="docs", help="document root (default: docs)")
    ap.add_argument("--fail-on", default="error",
                    choices=["error", "warning", "info", "none"],
                    help="lowest severity that fails the build (default: error)")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    ap.add_argument("--list-blind-spots", action="store_true")
    ap.add_argument("--baseline", metavar="PATH",
                    help="fail only on findings not already recorded in this baseline")
    ap.add_argument("--write-baseline", metavar="PATH",
                    help="record the current findings as the baseline, then exit 0")
    args = ap.parse_args(argv)

    if args.list_blind_spots:
        print(json.dumps(KNOWN_BLIND_SPOTS, indent=2))
        return 0

    root = Path(args.root)
    if not root.is_dir():
        print(f"check_docs: document root not found: {root}", file=sys.stderr)
        return 2

    try:
        findings, suppressed, corpus = run(root, args.fail_on)
    except OSError as exc:
        print(f"check_docs: cannot read corpus: {exc}", file=sys.stderr)
        return 2

    if args.write_baseline:
        n = write_baseline(Path(args.write_baseline), findings, git_revision(root.parent))
        print(f"check_docs: baseline written with {n} finding(s) -> {args.write_baseline}")
        return 0

    known: set[str] = set()
    baseline_rev = None
    if args.baseline:
        try:
            known, baseline_rev = load_baseline(Path(args.baseline))
        except BaselineError as exc:
            print(f"check_docs: unusable baseline {args.baseline}: {exc}", file=sys.stderr)
            print("check_docs: a broken baseline must not read as 'no drift'.", file=sys.stderr)
            return 2

    fresh = [f for f in findings if finding_key(f) not in known]
    pre_existing = [f for f in findings if finding_key(f) in known]

    blocking = [f for f in fresh if f.severity != "info"]

    if args.format == "json":
        print(json.dumps({
            "root": str(root),
            "documents": len(corpus.files),
            "adrs": len(corpus.adrs),
            "failOn": args.fail_on,
            "baseline": args.baseline,
            "baselineRevision": baseline_rev,
            "newFindings": [f.__dict__ for f in fresh],
            "knownFindings": [f.__dict__ for f in pre_existing],
            "suppressed": [
                {"finding": f.__dict__, "reason": r} for f, r in suppressed
            ],
            "blindSpots": KNOWN_BLIND_SPOTS,
        }, indent=2))
    else:
        print(f"check_docs: {len(corpus.files)} documents, {len(corpus.adrs)} ADR records, root={root}")
        if args.baseline:
            print(f"baseline: {len(pre_existing)} known, {len(fresh)} new")
        if not findings:
            print("clean")
        elif args.baseline and not fresh:
            print(f"no new drift ({len(pre_existing)} pre-existing finding(s) carried by baseline)")
        else:
            for f in (fresh if args.baseline else findings):
                print(f.render())
        if suppressed:
            print(f"\nsuppressed ({len(suppressed)}) — declared in-document, still visible:")
            for f, reason in suppressed:
                print(f"  [suppressed] {f.check} {f.path}:{f.line}")
                print(f"      reason: {reason}")
        print(f"\n{len(fresh)} finding(s) to act on; {len(pre_existing)} carried by baseline; "
              f"{len(suppressed)} suppressed; {len(KNOWN_BLIND_SPOTS)} declared blind spot(s)")

    if args.fail_on == "none":
        return 0
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())