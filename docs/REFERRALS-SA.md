# SA referrals — items outside Solution Architect accountability

| Field | Value |
|---|---|
| Document ID | REF-SA-CMS-001 |
| Version | 1.0.0 |
| Status | Open |
| Date | 2026-10-14 |
| From | Solution Architect (`RACI-CMS-001` §2) |
| To | Project Manager · Technical Lead |
| Basis | Mechanical audit of `docs/` against itself, run 2026-10-14 |
| Command | `python3 tools/docs/check_docs.py -C docs --fail-on warning` |

<!-- check:docs:allow DOC-04 This document quotes the stale counts and gate spellings it is asking other roles to fix. Removing the quotes would make the referrals unactionable; the underlying defects live in the files named below, not here. -->
<!-- check:docs:allow DOC-07 Same: the superseded gate spellings are reproduced verbatim so the TL can search for them. -->
<!-- check:docs:allow DOC-08 The accountable of a referral is its author, not a role that maintains it. Adding the field would imply this document is maintained; it is closed once the referrals are actioned. -->

Every item below was found by a command, not by reading. Each names the role that can
close it. **None of them may be closed by the SA** — under `RACI.md` §2 the artefacts
concerned belong to another role, and closing one here would leave a second document
claiming to own a fact it does not own, which is the defect class this whole pass existed
to remove.

---

## 1. To the Technical Lead — `TIMP-CMS-001` (3 items)

`TECHNICAL-IMPLEMENTATION-PLAN.md` uses the superseded gate spelling in two places and
still describes a 27-record ADR set.

| Line | Finding | Required change |
|---|---|---|
| 29, 283 | `pins:check` and `catalog:verify-ownership` — the two spellings superseded by ADR-0028 rule 3 | Use `check:pins` and `check:catalog`. §0.1 currently records this as a defect referred to the SA; it is now **resolved by ADR-0028**, so the note should point at the ADR rather than at an open question. |
| 203, 248 | "27 ADRs" / "the 27 records in `adr/`" — 28 now exist | Update to 28, or delete the literal and cite `adr/README.md` (see §3 below). |

**Note on line 29.** That paragraph is now partly obsolete in substance, not just in
spelling: it records the PRD/TDD naming split as *unresolved*. It was resolved on
2026-10-14.

## 2. To the Project Manager — `IMP-CMS-001` (1 item)

| Line | Finding | Required change |
|---|---|---|
| 54, 55 | `pins:check` (superseded spelling); "27 ADRs each cite ≥ 1 `R-xx`" | Use `check:pins`; update the count or make it relative. |

## 3. To the PM and TL jointly — a request, not a defect

**`check:docs` exists and will not be green until these are addressed.** Rather than have
each role hand-maintain a count that changes whenever a record is added, the durable fix
is to stop writing the literal: replace "27 ADRs" with a reference to `adr/README.md`,
which is the one place the number belongs.

This is not optional tidiness. It is the reason this pass happened. The amendment
originally proposed to fix a stale ADR range in `adr/README.md` was itself stale —
it named 27 when the set had reached 28. **A fix written by hand, unchecked, becomes stale
faster than the defect it repaired.** PRD v3.1.0 §21 item 13 now requires `check:docs` to
pass; under `IMPLEMENTATION-PLAN` §4 it falls to a phase exit, most naturally PH-10.

## 4. To the PM — `RACI-CMS-001` has no accountable (2 items)

| Finding | Why it matters |
|---|---|
| `RACI.md` §2 assigns no accountable to `RACI.md` itself | The artefact index carries "—" for it. Under the document's own rule, **a document with two owners has none** — but a document with *zero* owners has no one who can amend it. This is a deadlock: the only artefact that could assign RACI an owner is the artefact that has none. |
| `RACI.md:45` records the ADR set as 27 | 28 now exist. |

**SA proposal, requiring PM decision:** `RACI-CMS-001` is accountable to the **Project
Manager**, on the grounds that it governs coordination and decision rights rather than
architecture, and that `IMPLEMENTATION-PLAN` §7 already makes the PM the owner of the
governance cadence the RACI describes. SA is consulted, not deciding.

**Second proposal, same forum.** `README.md` §2 previously listed `TDD-CMS-001` as
`SA (§1–§23) / TL (§24)`, which contradicted `RACI.md` §3 — *"splitting the file is
optional; splitting the accountability is not."* A split accountability is exactly what
that rule forbids. Resolved unilaterally as SA by assigning **Technical Lead** (per
`RACI.md` §2, which already names TL accountable for Technical Design) and recording the
SA's directional ownership of §1–§23 as content ownership, not accountability. **Please
confirm.**

## 5. Deferred by the SA, with the reason on the record

**`DEC-10` has no ADR.** `DEC-10` ("Floating remote versions? Prohibited") is claimed by no
record, while `adr/README.md` asserted full DEC coverage. That assertion was false and
`check:docs` DOC-05 reports it.

The SA has **not** written an ADR for it, because `README.md` rule 3 says a decision gets an
ADR only if it is expensive to reverse, and dependency versions are reversible (RES-01).
`DEC-10` is enforced by `check:pins` and `D-11`. Manufacturing a record to satisfy a coverage
count would be the wrong fix, so `adr/README.md` now records `DEC-10` as deliberately
ADR-less. **If the TL or PM judges that pinning policy is expensive to reverse, the ADR is
theirs to demand and SA will write it.**

## 6. Not fixable with the data as it stands

`references.md` encodes reference status as prose inside a free-text column rather than as a
field, so the rule at `adr/README.md` rule 2 — *no record may cite a rejected reference* —
cannot be enforced mechanically. A substring scan for `REJECTED` produced 12 hits, **11 of
them false positives** (`R-SOLID-09` is named in `PRD.md` and `adr/0011` precisely to forbid
citing it; `R-SEC-01` is `VERIFIED` while its row mentions "REJECTED" in passing).

ADR-0028 rule 1 forbids shipping a check that cannot be made sound, so this is recorded as
a **declared blind spot** (`DOC-90`) rather than as a failing check. It is not in anyone's
queue today because **the schema change it needs is in `references.md`, an SA-owned
artefact**, and is scheduled as the next SA action after this referral is acknowledged.

---

## Re-run

```sh
python3 tools/docs/check_docs.py -C docs --fail-on warning
python3 tools/docs/test_check_docs.py
```

Expected once §1–§3 are closed: zero error findings. The RACI count (§4) will remain a
warning until the RACI's owner updates it.