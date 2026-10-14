#!/usr/bin/env python3
"""gen_docs — generate the derived parts of the document set.

One owner per derived fact (ADR-0028). This generator is the "generate" half;
check_docs.py is the "checked" half, and it also verifies that the output of
this script has not been hand-edited afterwards.

Sources of truth, read from existing prose:

  adr/NNNN-*.md      the ADR itself. Its H1, its `Closes:` / `Gate:` header
                     fields, and its `## References` section are the owner.
  <artefact>.md      each document's own `| Field | Value |` header block.

Generated outputs:

  docs/adr/README.md    ADR index tables and the record count
  docs/README.md        section 2 artefact index

Nothing under adr/ is edited to make generation work. ADR files are accepted
records and README.md rule 4 forbids editing them; the generator therefore
reads the prose that is already there. `Closes:` and `Gate:` are already
labelled fields inside that prose, and every one of the 28 records carries a
`## References` section, so the index can be derived without a schema change.

Standard library only. No dependency may become a reason a build breaks.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

BEGIN = "<!-- BEGIN GENERATED: {name} — owner: {owner}. Edit the owner, not this block. -->"
END = "<!-- END GENERATED: {name} -->"

ADR_NUM = re.compile(r"^# ADR-(\d{4}) — (.+)$", re.M)
# Header fields are '**Key:** value' separated by a middle dot. The key names
# vary across the set -- Closes, Refines, Amends, Supports all appear -- so the
# parser captures them generically instead of assuming one name.
HEADER_FIELD = re.compile(r"\*\*([A-Z][A-Za-z]*):\*\*\s*([^*]+?)\s*(?=\*\*|$)")
R_REF = re.compile(r"\b(R-[A-Z]+-\d+)\b")
R_RANGE = re.compile(r"\b(R-[A-Z]+-\d+)\s*(?:…|\.\.\.|–|-)\s*(R-[A-Z]+-\d+)\b")

# The header keys whose value names what the record is about. Used to derive the
# DEC -> ADR map; a record that names none is a decision, not a gap in coverage.
CLAIM_KEYS = ("Closes", "Refines", "Amends", "Supports", "Supersedes")


@dataclass
class Adr:
    num: int
    path: Path
    title: str
    fields: dict[str, str] = field(default_factory=dict)
    references: list[str] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return self.path.name

    @property
    def gate(self) -> str:
        return self.fields.get("Gate", "—").split("(")[0].strip() or "—"

    @property
    def claim(self) -> str:
        """Everything this record says it addresses, in the record's own words."""
        parts = [
            f"{k}: {self.fields[k]}" for k in CLAIM_KEYS if k in self.fields
        ]
        return "; ".join(parts) if parts else "—"

    @property
    def decs(self) -> list[str]:
        blob = " ".join(self.fields.get(k, "") for k in CLAIM_KEYS)
        return sorted(set(re.findall(r"\bDEC-\d{2}\b", blob)))

    @property
    def gaps(self) -> list[str]:
        blob = " ".join(self.fields.get(k, "") for k in CLAIM_KEYS)
        return sorted(set(re.findall(r"\bGAP-\d{2}\b", blob)))

    @property
    def evidence(self) -> str:
        return ", ".join(self.references) if self.references else "—"

    @property
    def family(self) -> str:
        """Derived, not curated.

        An earlier draft grouped records by hand into 'foundations' and
        'corrections'. That grouping is editorial -- ADR-0003 and ADR-0008
        address PRD identifiers but close no DEC, so no rule reproduces the
        hand-made split -- and a curated group is a hand-maintained fact, which
        is what this generator exists to remove. The claim column says what
        each record addresses; the reader does not need a category.
        """
        if self.gaps:
            return "correction"
        if self.decs:
            return "foundation"
        return "decision"


def expand_refs(text: str) -> list[str]:
    """Expand 'R-MONO-01 … R-MONO-08' into the ids it stands for."""
    out: list[str] = []
    claimed: set[str] = set()
    for rm in R_RANGE.finditer(text):
        a, b = rm.group(1), rm.group(2)
        m1 = R_REF.fullmatch(a)
        m2 = R_REF.fullmatch(b)
        if not m1 or not m2:
            continue
        pre1, n1 = m1.group(1).rsplit("-", 1)
        pre2, n2 = m2.group(1).rsplit("-", 1)
        if pre1 != pre2:
            continue
        lo, hi = int(n1), int(n2)
        if not (0 < hi - lo <= 64):
            continue
        for n in range(lo, hi + 1):
            rid = f"{pre1}-{n:02d}"
            claimed.add(rid)
            out.append(rid)
    for rid in R_REF.findall(text):
        if rid not in claimed:
            out.append(rid)
    seen: set[str] = set()
    return [r for r in out if not (r in seen or seen.add(r))]


def parse_header(head: str) -> dict[str, str]:
    """'**Key:** value' pairs across the header lines, split on the middle dot."""
    fields: dict[str, str] = {}
    for line in head.splitlines():
        if not line.lstrip().startswith("-"):
            continue
        for key, value in HEADER_FIELD.findall(line):
            v = value.strip().rstrip("·").strip()
            if key not in fields and v:
                fields[key] = v
    return fields


def load_adrs(adr_dir: Path) -> list[Adr]:
    out: list[Adr] = []
    for path in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
        text = path.read_text(encoding="utf-8")
        m = ADR_NUM.search(text)
        if not m:
            raise SystemExit(
                f"gen_docs: {path.name} has no '# ADR-NNNN — Title' heading; "
                "the generator cannot derive a title and refuses to guess one"
            )
        head = text[: text.find("## Context")] if "## Context" in text else text[:1500]
        refs = text.split("## References", 1)[1] if "## References" in text else ""
        out.append(Adr(
            num=int(m.group(1)),
            path=path,
            title=m.group(2).strip(),
            fields=parse_header(head),
            references=expand_refs(refs),
        ))
    return out


def render_adr_index(adrs: list[Adr]) -> str:
    # Derived, not asserted. The phrase "none superseded" was hardcoded and
    # became false the moment ADR-0029 retired two records -- a generated block
    # claiming something the generator had not looked at.
    live = [a for a in adrs if not a.fields.get("Status", "").lower().startswith("superseded")]
    retired = len(adrs) - len(live)
    if retired:
        state = (f"{len(live)} accepted; {retired} superseded by a later record")
    else:
        state = f"{len(live)} accepted records; none superseded"
    lines = [
        f"| Status of the set | {state} |",
        "",
        "| ADR | Title | Gate | Addresses | Evidence |",
        "|---|---|---|---|---|",
    ]
    for a in adrs:
        lines.append(
            f"| [{a.num:04d}]({a.slug}) | {a.title} | {a.gate} | {a.claim} | {a.evidence} |"
        )
    return "\n".join(lines)


def render_traceability(adrs: list[Adr]) -> str:
    """DEC -> ADR, derived from each record's own `Closes:` assertion."""
    m: dict[str, list[int]] = {}
    for a in adrs:
        for d in a.decs:
            m.setdefault(d, []).append(a.num)
    lines = ["| PRD decision | ADR |", "|---|---|"]
    for d in sorted(m):
        lines.append(f"| {d} | {', '.join(f'{n:04d}' for n in sorted(set(m[d])))} |")
    return "\n".join(lines)


GEN_MARKER = re.compile(
    r"<!-- BEGIN GENERATED:.*?-->\n.*?<!-- END GENERATED:.*?-->\n?",
    re.S,
)


def strip_generated(text: str) -> str:
    """Remove generated blocks before parsing.

    Without this the generator reads its own output: a generated table has a
    header row containing the literal cells 'Version', 'Status' and
    'Accountable', so the header-block parser matched the generated table
    instead of the document's real header and produced a shifted row.
    """
    return GEN_MARKER.sub("", text)


def _clean(v: str) -> str:
    v = v.replace("**", "").replace("`", "").strip()
    return re.sub(r"\s+", " ", v)


def _header_block(text: str) -> dict[str, str]:
    """The leading '| Field | Value |' block: id, version, status, owner."""
    out: dict[str, str] = {}
    seen = False
    for line in text.splitlines():
        if not line.startswith("|"):
            if seen and line.strip():
                break
            continue
        seen = True
        cells = [_clean(c) for c in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] == "Field" or set(cells[0]) <= set("-: "):
            continue
        out.setdefault(cells[0], cells[1])
    return out


def render_artefact_index(docs: Path, ids: list[str]) -> str:
    lines = ["| Artefact | ID | Version | Status | Accountable |", "|---|---|---|---|---|"]
    for want in ids:
        found = None
        for p in sorted(docs.glob("*.md")):
            text = strip_generated(p.read_text(encoding="utf-8"))
            if re.search(rf"\|\s*Document ID\s*\|\s*`?{re.escape(want)}`?\s*\|", text):
                found = (p, text)
                break
        if not found:
            lines.append(f"| — | `{want}` | — | not found | — |")
            continue
        p, text = found

        # Fields come from the leading "| Field | Value |" block only.
        # Scanning the whole document made any table with an "Owner" column look
        # like an owner declaration: a referrals table headed
        # "# | Item | Owner | Closed by" was rendered with an accountable role
        # of "Closed by".
        head = _header_block(text)

        def fieldval(name: str) -> str:
            v = head.get(name, "—")
            # Drop the trailing citation, e.g. "(RACI-CMS-001 section 2)", so
            # the column reads as a role rather than as a sentence.
            return v.split("(")[0].strip().rstrip("*").strip() or "—"

        # The display label is the file stem: derived and unambiguous. The
        # previous hand-written table used prose labels ("Architecture
        # standard", "Technical design") which were a hand-maintained mapping
        # from file to meaning; the stem needs no upkeep.
        label = p.stem
        owner = fieldval("Accountable")
        if owner == "—":
            owner = fieldval("Owner")
        lines.append(
            f"| {label} | `{want}` | {fieldval('Version')} | "
            f"{fieldval('Status')} | {owner} |"
        )
    return "\n".join(lines)


def inside_section(text: str, name: str, heading: str) -> bool:
    """Is the block for `name` under the heading it belongs to?

    A block that drifts into the wrong section still has correct content, so a
    content check passes and the artefact ends up rendered in a place nobody
    reads. That is what happened: the artefact index sat under "Rules for this
    directory" for several commits while gen_docs --check reported green.
    """
    hi = text.find(heading)
    if hi == -1:
        return False
    rest = text[hi:]
    nxt = re.search(r"^#{2,6} ", rest[1:], re.M)
    section = rest[: nxt.start() + 1] if nxt else rest
    # re.escape: the block name is a regex fragment, and a plain substring
    # test with a trailing \b never matches, because \b is a word-boundary
    # assertion and not a character that appears in the marker text.
    return re.search(rf"<!-- BEGIN GENERATED: {re.escape(name)}\b", section) is not None


def splice(text: str, name: str, owner: str, body: str) -> str:
    """Replace the block called `name`, wherever it is, or append it.

    Matching is by block NAME, not by the owner string inside the marker. An
    earlier version required the owner text to match exactly, so renaming an
    owner in one place left the generator appending a second block on every
    run -- three duplicate traceability tables in one file before it was caught.
    """
    begin_re = re.compile(rf"<!-- BEGIN GENERATED: {re.escape(name)}\b[^\n]*-->\n?")
    end_re = re.compile(rf"[ \t]*<!-- END GENERATED: {re.escape(name)} -->\n?")
    mb, me = begin_re.search(text), end_re.search(text)
    block = (
        f"<!-- BEGIN GENERATED: {name} — owner: {owner}. "
        f"Edit the owner, not this block. -->\n{body}\n"
        f"<!-- END GENERATED: {name} -->\n"
    )
    if mb and me and mb.start() < me.start():
        return text[: mb.start()] + block + text[me.end():]
    return text + "\n" + block


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="gen_docs")
    ap.add_argument("-C", "--root", default="docs")
    ap.add_argument("--check", action="store_true",
                    help="fail if any generated block is missing or stale")
    args = ap.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"gen_docs: document root not found: {root}", file=sys.stderr)
        return 2

    adr_dir = root / "adr"
    try:
        adrs = load_adrs(adr_dir)
    except OSError as exc:
        print(f"gen_docs: cannot read ADR set: {exc}", file=sys.stderr)
        return 2
    if not adrs:
        print("gen_docs: no ADR records found", file=sys.stderr)
        return 2

    # (path, block name, owner, body, heading the block must sit under)
    targets: list[tuple[Path, str, str, str, str]] = []

    idx = root / "adr" / "README.md"
    targets.append((idx, "adr-index", "adr/[0-9][0-9][0-9][0-9]-*.md",
                    render_adr_index(adrs), "## Index"))
    targets.append((idx, "adr-traceability", "the header field of each ADR",
                    render_traceability(adrs), "## Traceability"))

    readme = root / "README.md"
    ids = ["DOC-INDEX-CMS-001", "PRD-CMS-001", "TDD-CMS-001", "IMP-CMS-001",
           "TIMP-CMS-001", "TEST-CMS-001", "DEP-CMS-001", "RACI-CMS-001",
           "REF-CMS-001", "REF-SA-CMS-001"]
    targets.append((readme, "artefact-index", "the | Field | Value | header of each artefact",
                    render_artefact_index(root, ids), "## 2. Artefact index"))

    stale: list[str] = []
    misplaced: list[str] = []
    for path, name, owner, body, heading in targets:
        if not path.exists():
            stale.append(f"{path}: target missing")
            continue
        current = path.read_text(encoding="utf-8")
        if not inside_section(current, name, heading):
            misplaced.append(
                f"{path}: block '{name}' is not under '{heading}' "
                "(--check verifies content, not position)"
            )
        updated = splice(current, name, owner, body)
        if updated == current:
            continue
        stale.append(f"{path}: generated block '{name}' is absent or stale")
        if not args.check:
            path.write_text(updated, encoding="utf-8")

    if misplaced:
        for m in misplaced:
            print(f"gen_docs: misplaced: {m}", file=sys.stderr)
    if args.check:
        if stale or misplaced:
            print("gen_docs: generated blocks are not up to date:", file=sys.stderr)
            for s in stale + misplaced:
                print(f"  {s}", file=sys.stderr)
            print("\nRun: python3 tools/docs/gen_docs.py", file=sys.stderr)
            return 1
        print(f"gen_docs: {len(adrs)} ADR records, all generated blocks up to date")
        return 0

    for s in stale:
        print(f"  updated {s}")
    if not stale:
        print(f"gen_docs: {len(adrs)} ADR records, nothing to update")
    return 0


if __name__ == "__main__":
    sys.exit(main())