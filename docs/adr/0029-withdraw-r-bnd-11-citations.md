<!-- check:docs:allow DOC-90 R-BND-11, R-SOLID-09 — quoted verbatim from ADR-0012 and ADR-0017 and from the audit, in order to record and withdraw the citations. -->

# ADR-0029 — Two records cited a rejected entry; the claims are true and the citations are withdrawn

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-7
- **Amends:** ADR-0012, ADR-0017 — **both retired.** Reference lists corrected; neither decision is reopened · **Closes:** `adr/README.md` rule-2 violation found by `DOC-90`

## Context

`adr/README.md` rule 2 states that a cited reference must never be one of the catalogue's rejected entries. Until 2026-10-14 that rule was unenforceable, because `references.md` stored status as prose inside a free-text column rather than as a field. A substring scan for `REJECTED` over the corpus returned twelve hits, eleven of which were false positives — including `R-SOLID-09`, which is named in the PRD and in ADR-0011 precisely in order to forbid citing it.

ADR-0028 rule 1 forbids shipping a check that cannot be made sound, so the rule was recorded as a declared blind spot rather than as a failing gate. The block was `references.md`'s schema, which is SA-owned. It was migrated: every reference row now carries a `Status` field, and `DOC-90` shipped the same day.

`DOC-90` immediately found two genuine violations. **ADR-0012** and **ADR-0017** each list `R-BND-11` in their `## References` section with no marker:

```
R-BND-01, R-BND-02, R-BND-04, R-BND-11, R-BND-12, R-BND-13, R-SOLID-10
R-BND-01, R-BND-04, R-BND-11, R-BND-12, R-BND-13
```

`R-BND-11` is *Turborepo has no boundaries* — a negative claim. The catalogue rejects it **as a citation target**, not as a claim: the substance is true, but no positive Turborepo source says so. Its own row gives the instruction: *"Assert without citation, or cite R-BND-07 by contrast."*

Both records are accepted. `README.md` rule 4 forbids editing them, so this is the amendment path.

**Both records are retired.** Their status reads `Superseded by ADR-0029`, their reference lists drop `R-BND-11`, and the corrected lists are restated here as normative. Retirement is the amendment path rule 4 already provides; what was missing before was a rule saying a superseding record may retire the file it supersedes, and this version of `RACI-CMS-001` §2.1 and `README.md` §5 now say so.

Until that was settled the two findings sat in the committed baseline and `DOC-90` reported them on every run, which is a report nobody reads after a week. A permanently-red check is worse than an absent one, because it is counted as coverage. The honest options were to retire the records or to declare the citations intentional; the catalogue forbids the latter, so the first was the only one available.

**What retirement does not do.** It does not reopen either decision. ADR-0012 still gates a critical constraint on two mechanisms because `turbo boundaries` is Experimental; ADR-0017 still states which mechanism covers which class of violation. A reader who needs the decision reads this record's Summary, not the files.

## Decision

**The `R-BND-11` citations in ADR-0012 and ADR-0017 are withdrawn. Neither decision changes.**

- ADR-0012's decision — two independent mechanisms police the dependency graph, because `turbo boundaries` is labelled Experimental — is unaffected. `R-BND-01`, `R-BND-02`, `R-BND-04`, `R-BND-12`, `R-BND-13` and `R-SOLID-10` remain and carry it.
- ADR-0017's gate matrix — which mechanism covers which class of violation — is unaffected. The matrix's Turborepo column asserts a **capability boundary**, not a performance or correctness claim, and capability boundaries are what the tool's own documentation states.

`R-BND-07` (`@nx/enforce-module-boundaries`) is added to ADR-0017 as the contrast the catalogue prescribes: it is the mature tag-based boundary mechanism ADR-0012 treats as the primary one, and citing it makes the "Turborepo cannot express this class" row legible without asserting it about Turborepo from nothing.

The corrected reference lists, which are now normative:

- **ADR-0012** — `R-BND-01, R-BND-02, R-BND-04, R-BND-12, R-BND-13, R-SOLID-10`
- **ADR-0017** — `R-BND-01, R-BND-04, R-BND-07, R-BND-12, R-BND-13` (R-BND-07 added, per the catalogue's own instruction to cite it by contrast)

## Consequences

- **Rule 2 is enforceable and currently satisfied.** `DOC-90` runs in CI against every document. The two findings were baselined while the decision was pending and are removed from the baseline now that it is made.
- **The correction is a citation change, not a decision change.** Anyone reading ADR-0012 or ADR-0017 for the *decision* is unaffected. Anyone reading them for the evidence sees a list that now resolves.
- **A negative claim remains asserted, uncited.** That is the catalogue's instruction and it is worth stating plainly: this document set asserts that Turborepo cannot express certain boundary classes, and that assertion rests on the tool's documented model rather than on a citable source. It is a limitation of the evidence base, recorded rather than papered over.
- **This is what a superseding record is for.** The tempting move was to edit two reference lists and note it in a remediation commit. That is precisely the failure ADR-0028 was written about: a fix made by hand, unchecked, that leaves the reader unable to tell it from the original.

## Alternatives rejected

- **Edit ADR-0012 and ADR-0017 in place** — rejected: rule 4. Accepted records are not edited, and a correction that lands without a record leaves the next reader unable to distinguish it from the original text.
- **Add a `check:docs:allow DOC-90` marker to both records instead** — rejected: it would mark an unintentional citation as intentional. Whether the citation was meant as support is the open question this record answers, and the answer is that it was not, because the catalogue forbids it.
- **Reconsider the underlying claims now that they are uncited** — rejected: out of scope. Both claims remain true; ADR-0012's experimental-label concern is documented by Turborepo itself, and ADR-0017's matrix describes scope rather than quality. Reopening them would be a different record.

## References

R-BND-01, R-BND-02, R-BND-04, R-BND-07, R-BND-12, R-BND-13, R-SOLID-10, R-META-26 (metadata validity is checked against a published schema, and the same reasoning applies to a decision's evidence list), R-DOC-02 (the check that found this)