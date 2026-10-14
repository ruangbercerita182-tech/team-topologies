<!-- check:docs:allow DOC-90 R-BND-11, R-SOLID-09 — derived from each record's References section, so a record may carry a rejected entry. R-BND-11 in ADR-0012 and ADR-0017 is withdrawn by ADR-0029; the records are frozen as written. -->

# Architecture Decision Records

| Field | Value |
|---|---|
| Owner | **Solution Architect** (RACI-CMS-001 §2, §5) |
| Basis | PRD DEC-01…DEC-24, TDD §14 (GAP-01…GAP-14), `docs/references.md` |
| Rules | (1) Every ADR cites ≥ 1 `R-xx` from the reference catalogue. (2) A cited URL must never be one of the **rejected** entries. (3) A decision is not reopenable without a superseding ADR. (4) An ADR is a decision about something **expensive to reverse**; if it is not, it belongs in the catalogue, not here. |

**Template:** Context (what forced a decision) → Decision → Consequences (including the costs we chose to pay) → Alternatives rejected → References.

---

## Index

Generated from the records themselves. The owner is each ADR's own H1,
header fields and `## References` section — edit the record, never this table.

<!-- BEGIN GENERATED: adr-index — owner: adr/[0-9][0-9][0-9][0-9]-*.md. Edit the owner, not this block. -->
| Status of the set | 27 accepted; 2 superseded by a later record |

| ADR | Title | Gate | Addresses | Evidence |
|---|---|---|---|---|
| [0001](0001-repository-topology-is-an-output.md) | Repository topology is a derived output, not an architectural input | PH-1 | Closes: PRD DEC-01, DEC-02; Amends: none | R-MONO-01, R-MONO-02, R-MONO-03, R-MONO-04, R-MONO-05, R-MONO-06, R-MONO-07, R-MONO-08, R-MONO-38, R-MONO-39, R-MONO-40, R-MONO-10, R-MONO-13, R-MONO-16, R-MONO-20, R-MONO-23, R-MONO-26, R-MONO-34 |
| [0002](0002-team-scoped-top-level-directories.md) | Top-level directories are team-scoped, not layer-scoped | PH-1 | Closes: PRD DEC-03, D-12 | R-MONO-13, R-MONO-38, R-MONO-39, R-TT-03 |
| [0003](0003-three-plane-model.md) | Three planes: presentation composition, business domain, response composition | PH-2 | Refines: PRD D-02, D-03, D-04 | R-DDD-01, R-DDD-03, R-TT-03, R-BFF-01, R-BFF-04, R-CA-02 |
| [0004](0004-aggregator-is-not-a-bounded-context.md) | The aggregator is composition only, with mechanical disqualification tests | PH-6 | Closes: PRD DEC-09, D-02, §6.2 | R-BFF-01, R-BFF-03, R-BFF-04, R-BFF-05, R-BFF-13, R-BFF-19, R-AGGR-09, R-AGGR-10 |
| [0005](0005-application-composition-layer.md) | Composition layer and UI business domain are separated by vocabulary and state | PH-7 | Closes: PRD DEC-08, D-04, §5 | R-DDD-01, R-MFE-04, R-MFE-15, R-MFE-16 |
| [0006](0006-declarative-composition.md) | Composition is declarative and generated, never imperatively registered | PH-3 | Closes: PRD DEC-15, D-07, D-09, G-04 | R-META-01, R-META-03, R-META-04, R-META-09, R-META-17, R-META-19, R-META-20, R-META-30, R-META-31, R-CFG-03 |
| [0007](0007-interfaces-are-the-unit-of-ownership.md) | Provider/consumer roles attach to interfaces, and interfaces are first-class metadata | PH-2 | Closes: PRD D-05, §7.1 | R-META-09, R-META-26, R-META-27, R-META-28, R-CDC-01, R-CDC-03, R-TT-03 |
| [0008](0008-ownership-resolution-is-total.md) | Ownership resolution is total and safe under self-declaration | PH-2 | Closes: PRD FR-06, FR-09, D-12 | R-OWN-01, R-OWN-02, R-OWN-03, R-OWN-04, R-OWN-05, R-OWN-06, R-MONO-38, R-MONO-39, R-META-26 |
| [0009](0009-authorisation-in-every-context-per-request.md) | Authorisation is enforced in the bounded context, on every request | PH-6 | Closes: PRD DEC-12, D-06, AC-12 | R-MFE-15, R-MFE-16, R-MFE-17, R-SEC-01, R-BFF-01, R-TT-03 |
| [0010](0010-micro-frontends-for-deployment-independence-only.md) | Micro-frontends are adopted for deployment independence, never for isolation | PH-6 | Closes: PRD DEC-06, NG-03, §11.1 | R-MFE-01, R-MFE-02, R-MFE-03, R-MFE-04, R-MFE-06, R-MFE-12, R-MFE-15 |
| [0011](0011-solid-at-layer-boundaries-only.md) | SOLID is applied at layer boundaries only | PH-7 | Closes: PRD DEC-16, §10.1 | R-SOLID-01, R-SOLID-02, R-SOLID-03, R-SOLID-04, R-SOLID-05, R-SOLID-06, R-SOLID-07, R-SOLID-08, R-SOLID-09, R-SOLID-10, R-CA-01, R-CA-02, R-CA-06 |
| [0012](0012-two-boundary-mechanisms-not-one.md) | Critical constraints are not gated on a single experimental mechanism | PH-7 | Closes: PRD DEC-14, AC-01, FR-14, RISK-05 | R-BND-01, R-BND-02, R-BND-04, R-BND-12, R-BND-13, R-SOLID-10 |
| [0013](0013-module-federation-optimisation-flags.md) | Federation size is bought with `externalRuntime` + `disableSnapshot`, never with `disableShared` | PH-6 | Closes: TDD GAP-01, GAP-02, GAP-03 | R-MF-21, R-MF-22, R-MF-23, R-MF-24, R-MF-03, R-MF-08 |
| [0014](0014-route-data-strategy.md) | Every route declares a data strategy; the aggregator participates only where it is needed | PH-2 | Closes: TDD GAP-04 | R-BFF-01, R-BFF-02, R-BFF-05, R-BFF-13, R-RES-09, R-AGGR-06 |
| [0015](0015-aggregator-forwards-the-user-subject.md) | The aggregator forwards the end-user subject and never substitutes a service identity | PH-6 | Closes: TDD GAP-05 | R-BFF-01, R-BFF-04, R-SEC-01, R-INT-02, R-MFE-25, R-META-27 |
| [0016](0016-self-declared-ownership-invariants.md) | Self-declared ownership is safe only because of two invariants | PH-2 | Closes: TDD GAP-06 | R-OWN-01, R-OWN-02, R-OWN-03, R-OWN-04, R-OWN-05, R-OWN-06, R-MONO-38, R-META-26 |
| [0017](0017-boundary-enforcement-scope.md) | The boundary gate matrix: what each mechanism actually covers | PH-7 | Closes: TDD GAP-07; Refines: ADR-0012 | R-BND-01, R-BND-04, R-BND-12, R-BND-13 |
| [0018](0018-direnv-activation-with-pinned-script.md) | direnv stays for reviewability, with the activation script pinned by hash | PH-5 | Closes: TDD GAP-08; Amends: PRD DEC-07 and §9's `.envrc` snippet | R-DIR-01, R-DIR-02, R-DIR-03, R-DV-10, R-DV-15, R-DV-16, R-DV-17, R-DV-08 |
| [0019](0019-artefact-duplication-budgets.md) | Budget what the artefact costs, not only what one navigation downloads | PH-8 | Closes: TDD GAP-09 | R-MFE-06, R-MFE-24, R-MFE-26, R-PERF-11, R-PERF-15, R-PERF-19 |
| [0020](0020-contract-verification-against-the-published-schema.md) | Consumer verification runs against the provider's published contract | PH-6 | Closes: TDD GAP-10; Refines: PRD FR-23 | R-CDC-01, R-CDC-03, R-CDC-04, R-META-12, R-META-13, R-SEC-01 |
| [0021](0021-deny-by-default-authorisation-coverage.md) | Every inbound route must reference an authorisation port or declare itself public | PH-6 | Closes: TDD GAP-11; Refines: ADR-0009, PRD AC-12 | R-SEC-01, R-MFE-15, R-BFF-01 |
| [0022](0022-generated-artefacts-are-tamper-evident-not-exempt.md) | Generated files inside another team's directory are tamper-evident, not exempt | PH-3 | Closes: TDD GAP-12 | R-OWN-02, R-OWN-06, R-META-03, R-MONO-38 |
| [0023](0023-shell-attested-sessions.md) | "External consumers prohibited" gets a runtime control | PH-6 | Closes: TDD GAP-13 | R-BFF-01, R-BFF-03, R-SEC-01, R-INT-02 |
| [0024](0024-stable-remote-manifest.md) | Hashed assets with a stable manifest; the shell never embeds remote content hashes | PH-6 | Closes: TDD GAP-14 | R-MF-06, R-MF-07, R-MF-08, R-MF-10, R-MF-16, R-PERF-11, R-RES-21 |
| [0025](0025-no-asynchronous-inter-context-integration.md) | No asynchronous inter-context integration in v3.0.0 | PH-6 | Supports: PRD D-03, §6.1 | R-BFF-23, R-BFF-19, R-DDD-02, R-TT-03 |
| [0026](0026-generated-dependency-manifests.md) | Package dependency lists are generated from the interface ledger | PH-3 | Refines: ADR-0007 | R-META-09, R-META-26, R-BND-12, R-BND-13, R-BUILD-02, R-BUILD-09 |
| [0027](0027-phase-sequencing-is-dependency-gated.md) | Phase sequencing is gated on artefact dependencies, not on phase order | PH-1 | Amends: PRD §18 (see PR-9 in the ADR README) | R-TT-03, R-OWN-03, R-OWN-04, R-RES-10, R-BUILD-01 |
| [0028](0028-one-owner-per-derived-fact.md) | Every derived fact has one owner; prose states rules, the model holds values | PH-1 | Amends: none | R-META-07, R-META-09, R-META-19, R-META-20, R-META-01, R-META-03, R-OWN-01, R-OWN-02, R-OWN-05, R-DOC-01, R-DOC-02 |
| [0029](0029-withdraw-r-bnd-11-citations.md) | Two records cited a rejected entry; the claims are true and the citations are withdrawn | PH-7 | Closes: `adr/README.md` rule-2 violation found by `DOC-90`; Amends: ADR-0012, ADR-0017 — | R-BND-01, R-BND-02, R-BND-04, R-BND-11, R-BND-12, R-BND-13, R-SOLID-10, R-BND-07, R-META-26, R-DOC-02 |
<!-- END GENERATED: adr-index -->

---
## Traceability: DEC → ADR

Generated from each record's own `Closes:` / `Refines:` / `Amends:` /
`Supports:` field. A decision listed here is claimed by at least one record.

<!-- BEGIN GENERATED: adr-traceability — owner: the header field of each ADR. Edit the owner, not this block. -->
| PRD decision | ADR |
|---|---|
| DEC-01 | 0001 |
| DEC-02 | 0001 |
| DEC-03 | 0002 |
| DEC-06 | 0010 |
| DEC-07 | 0018 |
| DEC-08 | 0005 |
| DEC-09 | 0004 |
| DEC-12 | 0009 |
| DEC-14 | 0012 |
| DEC-15 | 0006 |
| DEC-16 | 0011 |
<!-- END GENERATED: adr-traceability -->

### Editorial mappings not derivable from any record

These mappings are **authored, not derived**. The table above is generated from each
record's own header and is therefore the floor — what the records themselves assert. The
mappings below are not derivable from any record header, and they were lost the first time
this section was generated; they are preserved here rather than dropped, because the two
kinds of fact were indistinguishable in the hand-written table this replaced.

That gap is itself a finding. For each row, either the record's `Closes:` / `Refines:` field
should name the decision, or the mapping is a claim no record makes. The second case is not
automatically wrong — `DEC-10` is a standing example of a decision that is enforced
(`check:pins`, `D-11`) but deliberately carries no record, because `README.md` rule 3 reserves
records for decisions that are expensive to reverse.

**Rule 4 blocks the obvious fix.** Adding `Closes: PRD DEC-17` to ADR-0021 would make the row
derivable, but ADR-0021 is accepted and accepted records are not edited; such a change lands
as a superseding record. Until then these rows are maintained here, and a change to a row is a
change to this section, not to the generated one.

| PRD decision | ADR | Basis |
|---|---|---|
| DEC-04, DEC-09 | 0003, 0004 | authored; neither record names `DEC-04` in its header |
| DEC-05 (banner only), DEC-07 | 0011, 0018 | authored; scoped to banner, which is narrower than the decision text |
| DEC-11 (no federation), DEC-13 (Team API not normative) | 0004, 0006 | authored; parenthetical scoping is a judgement |
| DEC-17…DEC-19 | 0021, 0026, 0013 | authored; closed as a group, no record names the range |
| DEC-20…DEC-24 | 0013, 0019, 0020, 0026 | authored; closed as a group, no record names the range |
| DEC-21, DEC-22 | 0020, 0012 | authored; overlaps the range above |
| ADR-0012, ADR-0017 | 0029 | authored; R-BND-11 citations withdrawn, decisions unchanged |
| DEC-25 | 0025 | authored; ADR-0025 carries it under `Supports:` (PRD D-03, §6.1), not `Closes:` |
| DEC-10 | — **no record; see the note under the generated table** | enforced by `check:pins` and `D-11`; cheap to reverse per RES-01, so rule 3 does not require a record |


---
## Requested changes to `docs/PRD.md`

**Applied in PRD v3.1.0:** PR-2 (MF-4 split into MF-4a…MF-4d, PERF-03 reachability stated),
PR-5 (`.envrc` pinned `source_url` form), PR-8 (DEC-25), PR-9 (§18 prerequisite-gating, the closed
overlap set and the two hard exclusions), PR-7 (`route.dataStrategy`, FR-13),
PR-4 (§7.2 ordering, ALG-4 invariants O-1/O-2),
PR-6 (§12.2a BUD-06…BUD-09 with owners and gates; AC-13, AC-14), plus §21 items 11–13 and the gate naming unification.
PR-3 (§8.2 `Interface` and `Budget` kinds, `relations/` derived) completes the set.

**All nine applied in PRD v3.1.0.** Each is listed below with its source ADR. None was
disputed; the only reason any was outstanding is that a version bump was taken first and the
body amendments then followed, so that each edit could be verified against a working gate.

PR-9 was the sharpest of the nine. §18 still said *"a phase starts only when the previous
phase's exit criterion objectively holds"* while ADR-0027 had already replaced it — so the
document violated §21 item 12, the precedence clause added in this same version.

These are PRD amendments this record set requires. They are listed rather than applied, because the PRD is SA-owned and versioned separately (RACI §2).

| # | Amendment | Reason | Source |
|---|---|---|---|
| PR-1 | §21 item 7: the ADR range written against the original twelve-record scope → the full range | the ADR set grew to cover every TDD correction. **Corrected 2026-10-14:** this row previously read "→ `0001–0026`", which was itself stale — the set had already reached 0027, and now 0028 | ADR README index |
| PR-2 | §11.3 MF-4 amended: `disableShared` **off**; `disableSnapshot: true` in production; `provideExternalRuntime` on the shell | upstream constraints and the published size table | ADR-0013 |
| PR-3 | §8.2: add `Interface` and `Budget` kinds; `relations/` becomes derived | one declaration of each fact | ADR-0007, 0026, TDD §8.1 |
| PR-4 | §7.2: adopt ALG-4 with invariants O-1/O-2 | §7.2 leaves precedence undefined | ADR-0008, 0016 |
| PR-5 | §9/FR-18: `.envrc` uses the pinned `source_url` + sha256 form | the current snippet is unpinned against D-11 | ADR-0018 |
| PR-6 | §12.1: add BUD-06…BUD-09; §15: add the budget gate | artefact-side cost was unbudgeted | ADR-0019 |
| PR-7 | §16: add `remote/dataStrategy` to `clients/*.yaml` | the request path was unspecified | ADR-0014 |
| PR-8 | §22: add DEC-25 (no async inter-context integration) | closes the question rather than leaving it implicit | ADR-0025 |
| PR-9 | §18: replace "a phase starts only when the previous phase's exit criterion holds" with prerequisite-gating; enumerate the closed four-pair overlap set and the two hard exclusions (PH-1 serial; PH-9 ⇠ PH-3, PH-8 ⇠ PH-7) | strict ordering delays the first mechanically-caught violation to week 18 and costs ~4 weeks for no safety gain | ADR-0027, IMPLEMENTATION-PLAN §3.1, §5 |


---
