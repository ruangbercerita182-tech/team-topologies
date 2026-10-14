# CMS Platform Architecture — Documentation Index

| Field | Value |
|---|---|
| Document ID | DOC-INDEX-CMS-001 |
| Status | Active |
| Date | 2026-10-14 |
| Purpose | Entry point and document index. **Not a source of truth for any topic** — see the reading rules below. |

This file holds no decisions, no requirements and no plan. It exists so a newcomer can find the
authoritative document for a question without guessing, and so that adding an artefact has an
obvious place to be registered.

---

## 1. Reading rules

Ask *what kind of question* you have, then open the one document that owns it.

| Your question | Authoritative document |
|---|---|
| What must be true, and why was it decided that way? | [`adr/`](adr/README.md) — one record per expensive-to-reverse decision |
| What is the normative architecture standard? | [`PRD.md`](PRD.md) — the only *Approved* document here; the root of the dependency chain |
| How is it designed in detail? | [`TDD.md`](TDD.md) — normative detail *under* the PRD |
| What is the schedule, phase order and dependency register? | [`IMPLEMENTATION-PLAN.md`](IMPLEMENTATION-PLAN.md) |
| What do I build, task by task? | [`TECHNICAL-IMPLEMENTATION-PLAN.md`](TECHNICAL-IMPLEMENTATION-PLAN.md) |
| How is it verified? | [`TEST-PLAN.md`](TEST-PLAN.md) |
| How is it shipped and cut over? | [`DEPLOYMENT-PLAN.md`](DEPLOYMENT-PLAN.md) |
| Who owns what, and who decides what? | [`RACI.md`](RACI.md) |
| What is the evidence base? | [`references.md`](references.md) |

**Conflict rule.** These documents are not merged. If two disagree, that is a defect, not a
choice: identify which document owns the topic using the table above, raise it with that
document's accountable role, and let the fix propagate as an ADR or a version bump. Never
silently copy one version into another.

---

## 2. Artefact index

Accountable roles are canonical in [`RACI.md`](RACI.md) §2; decision rights are in §5. Summarised
here for navigation only.

| Artefact | ID | Version | Status | Accountable |
|---|---|---|---|---|
| Architecture standard | `PRD-CMS-001` | 3.0.0 | **Approved for implementation** | Solution Architect |
| Technical design | `TDD-CMS-001` | 1.0.0 | Proposed | SA (§1–§23) / TL (§24) — see RACI §3 |
| Overall implementation plan | `IMP-CMS-001` | 1.0.0 | Proposed | Project Manager |
| Technical implementation plan | `TIMP-CMS-001` | 1.0.0 | Proposed | Technical Lead |
| Test plan | `TEST-CMS-001` | 1.0.0 | Proposed | QA / Test Lead |
| Deployment & cutover plan | `DEP-CMS-001` | 1.0.0 | Proposed | DevOps lead (TL co-signs app order) |
| RACI | `RACI-CMS-001` | 1.0.0 | Proposed | — |
| Reference catalogue | `REF-CMS-001` | 3.0.0 | Active | Solution Architect |
| Architecture decision records | `ADR-0001`…`ADR-0027` | — | 27 accepted, none superseded | Solution Architect |

Only `PRD-CMS-001` is approved. Everything downstream is `Proposed` and inherits its authority
from the PRD rather than carrying its own.

---

## 3. Reading traps

Three places where the names will mislead you. These are deliberate, not oversights.

**`PRD.md` is not a product requirements document.** It is the *architecture standard* for a CMS
product organisation — repository topology, boundary rules, performance budgets. Product
functionality is explicitly a non-goal (`NG-07`): the business/functional specification is
**out of scope for this repository** and is not written yet. Do not look here for feature scope.

**`IMPLEMENTATION-PLAN.md` and `TECHNICAL-IMPLEMENTATION-PLAN.md` differ by one word.** The first
is the PM-owned schedule and dependency register; the second is the TL-owned task breakdown. The
filenames are not renamed because ADR-0027 cites the former by name and accepted records are not
edited. Check the `Accountable` field, not the filename, when you are unsure.

**There are two ADR scopes, and both are correct.** `PRD.md` names `ADR-0001 … ADR-0012`, which
matches its own Definition of Done §21.7 — that was the scope fixed at PRD v3.0.0. ADR-0013…
ADR-0027 were written afterwards to close `TDD.md` §14 `GAP-01…GAP-14`. The live set is 27; see
[`adr/README.md`](adr/README.md). They are not duplicates, and neither range is wrong:

- Most of the later records **add mechanism** the PRD left unspecified.
- **GAP-01/02/03 are configuration corrections** to PRD §11.3 (MF-4 `disableShared`, the
  unreachable `PERF-03` budget, `externalRuntime` host requirements).
- **GAP-08 is a staleness correction** to `DEC-07` and §9's unpinned `.envrc` form.

Where a later ADR conflicts with PRD text, the ADR wins — it is the newer accepted record.

---

## 4. Known gap in this document set

**`PRD-CMS-001` §21 (Definition of Done) does not mention ADRs 0013–0027.** It was written
against the 12-record scope and its ten completion criteria contain no clause for the
`GAP-01…GAP-14` closures. An implementer working the PRD's own acceptance gate has no signal that
fourteen accepted corrections exist, three of which change shipped configuration defaults
(`MF-4`, `PERF-03`, `externalRuntime`) and one of which invalidates an unpinned snippet in §9.

This is a real gap, and it is in an `Approved for implementation` document, so it is the
Solution Architect's to close — not a documentation fix anyone else should make unilaterally.
Suggested amendment: extend §21 with a clause requiring every `TDD.md` §14 GAP to be closed by an
accepted ADR or an explicitly unresolved entry, and a clause that a `GAP` superseded by ADR wins
over the corresponding PRD text.

Tracked here rather than in the PRD so the gap stays visible without an unapproved edit.

---

## 5. Rules for this directory

1. One accountable role per artefact and per decision. A document with two owners has none
   (`RACI.md`).
2. Every ADR cites at least one `R-xx` from the catalogue, and never cites a rejected entry
   (`adr/README.md`).
3. A decision gets an ADR only if it is expensive to reverse. Otherwise it belongs in the
   catalogue (`adr/README.md`).
4. An accepted ADR is not edited. Corrections land as a superseding ADR.
5. Register any new artefact in §2 above and give it a `<TYPE>-CMS-00n` ID.