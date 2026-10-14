<!-- check:docs:allow DOC-90 R-SOLID-09 — quoted to report the false positives that made this rule unshippable. -->

# SA referrals — items outside Solution Architect accountability

| Field | Value |
|---|---|
| Document ID | REF-SA-CMS-001 |
| Version | 2.0.0 |
| Status | **Closed** |
| Date | 2026-10-14 · closed |
| From | Solution Architect (`RACI-CMS-001` §2) |
| Basis | Mechanical audit of `docs/` against itself |
| Command | `python3 tools/docs/run_all.py` |

**Status: closed 2026-10-14.** Every item in v1.0.0 was resolved and the file was rewritten rather
than annotated, so a reader arriving now sees one state instead of a change log. The items are
listed under "What this found" because the findings are the record; they are no longer open.

The two fixed counts are described, not reproduced: a number quoted in a document about the
defect it caused is a hand-maintained fact, which is the whole subject of ADR-0028.

Closure required the artefact owner's authority over artefacts the SA does not own. It was given
on 2026-10-14, which is what made items 1, 2 and 4 closable rather than merely referred.

---

## What this found, and what closed it

| # | Item | Owner | Closed by |
|---|---|---|---|
| 1 | `TIMP-CMS-001` used both spellings of two gates; described a fixed ADR count | TL | Spellings unified on `TDD` §13 per ADR-0028; counts replaced with "every record in `adr/`" so they cannot drift again |
| 2 | `IMP-CMS-001` used one superseded spelling; asserted a fixed ADR count | PM | Same |
| 3 | A durable fix, requested not defected | PM + TL | The counts were deleted rather than corrected. A number that changes whenever a record is added is a hand-maintained fact, which is the entire subject of ADR-0028 |
| 4 | `RACI-CMS-001` named no accountable — a deadlock, since the only artefact that could assign it one had none | PM | Assigned to **Project Manager**, with §2.1 added recording the reasoning taken from §5 and `IMPLEMENTATION-PLAN` §7 rather than invented |
| 5 | ADR-0012 and ADR-0017 cited a `REJECTED` reference | SA (with authority) | ADR-0029; both records retired |
| 5.1 | Seven rejected entries sat inside ranges in PRD §22 | SA | Ranges recomputed against the catalogue: `R-MFE-20`, `R-BE-21`, `R-BND-10` |
| 6 | The rejected-citation rule was unenforceable | SA | Closed — see below |

## 6. Closed: the largest blind spot

DOC-90 existed as a declared blind spot because `references.md` stored status as prose. It could
not be shipped sound: scanning for `REJECTED` gave twelve hits of which eleven were false
positives, including `R-SOLID-09`, which is named in the PRD and in ADR-0011 precisely in order to
forbid citing it.

The block was the catalogue's schema. All 416 reference rows now carry a `Status` field. Rows with
no explicit marker were recorded `VERIFIED` on the catalogue's own authority — its preamble already
asserts every reference was retrieved and read, and the arithmetic confirms it: 381 VERIFIED, 24
PARTIAL, 11 REJECTED, matching the totals the header already claimed.

Shipping the check immediately found items 5 and 5.1. That is the argument for closing a blind
spot rather than documenting it: the two blind spots declared at ADR-0028 were a statement of what
was missing, and filling one of them produced five findings the corpus did not know it had.

## 7. Closed: the last blind spot

`DOC-91` — detecting the same fact stated with two different values — was declared a blind spot
because nothing named which fact a sentence was *about*. The facts are keyed now: every artefact
declares its own `Document ID`, `Version`, `Status` and `Accountable` in a `| Field | Value |` block,
every ADR carries `Gate` and `Closes` as labelled fields, and every reference row carries `Status`.

`DOC-91` covers version cross-references. A reference to `X vN.N.N` is a claim about X's *current*
version — except inside a `Supersedes` row, where naming an older version is the entire point. That
distinction is made by the field name, not by reading the sentence, so the check stays sound under
ADR-0028 rule 1.

Shipping it found four stale cross-references that no other check could see, including the PRD
describing its own evidence base as 379 admissible references when the catalogue held 405. Adopting
it also required a rule change: a superseding record may now retire the file it supersedes, so a
retired artefact's header no longer has to be current.

**No blind spots remain declared.** That is not the same as having none — it means the ones we
could name are closed, and the ones we cannot name yet are the ones nobody has been bitten by.

## Re-run

```sh
python3 tools/docs/run_all.py
python3 tools/docs/test_check_docs.py
```

Baseline is empty. The gate is green because there is nothing left to carry, not because anything
is suppressed.
