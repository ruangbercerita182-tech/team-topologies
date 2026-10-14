# Architecture Decision Records

| Field | Value |
|---|---|
| Owner | **Solution Architect** (RACI-CMS-001 §2, §5) |
| Status of the set | 28 accepted records; none superseded |
| Basis | PRD DEC-01…DEC-24, TDD §14 (GAP-01…GAP-14), `docs/references.md` |
| Rules | (1) Every ADR cites ≥ 1 `R-xx` from the reference catalogue. (2) A cited URL must never be one of the **rejected** entries. (3) A decision is not reopenable without a superseding ADR. (4) An ADR is a decision about something **expensive to reverse**; if it is not, it belongs in the catalogue, not here. |

**Template:** Context (what forced a decision) → Decision → Consequences (including the costs we chose to pay) → Alternatives rejected → References.

---

## Index

### Foundations (from PRD DEC-01…DEC-14)

| ADR | Title | Gate | Primary evidence |
|---|---|---|---|
| [0001](0001-repository-topology-is-an-output.md) | Repository topology is a derived output, not an architectural input | PH-1 | R-MONO-01…08, R-MONO-13, R-MONO-16 |
| [0002](0002-team-scoped-top-level-directories.md) | Top-level directories are team-scoped, not layer-scoped | PH-1 | R-MONO-13, R-MONO-38 |
| [0003](0003-three-plane-model.md) | Three planes: presentation composition, business domain, response composition | PH-2 | R-DDD-01, R-BFF-04 |
| [0004](0004-aggregator-is-not-a-bounded-context.md) | The aggregator is composition only, with mechanical disqualification tests | PH-6 | R-BFF-01, R-AGGR-09 |
| [0005](0005-application-composition-layer.md) | Composition layer and UI business domain separated by vocabulary and state | PH-7 | R-DDD-01, R-MFE-04 |
| [0006](0006-declarative-composition.md) | Composition is declarative and generated, never imperatively registered | PH-3 | R-META-03, R-META-19 |
| [0007](0007-interfaces-are-the-unit-of-ownership.md) | Provider/consumer roles attach to interfaces, and interfaces are first-class metadata | PH-2 | R-META-09, R-META-26 |
| [0008](0008-ownership-resolution-is-total.md) | Ownership resolution is total | PH-2 | R-OWN-01…06 |
| [0009](0009-authorisation-in-every-context-per-request.md) | Authorisation is enforced in the bounded context, on every request | PH-6 | R-MFE-15, R-MFE-16 |
| [0010](0010-micro-frontends-for-deployment-independence-only.md) | Micro-frontends for deployment independence, never for isolation | PH-6 | R-MFE-01, R-MFE-04 |
| [0011](0011-solid-at-layer-boundaries-only.md) | SOLID is applied at layer boundaries only | PH-7 | R-SOLID-08, R-SOLID-10 |
| [0012](0012-two-boundary-mechanisms-not-one.md) | No critical constraint is gated on a single experimental mechanism | PH-7 | R-BND-01, R-BND-04 |

### Corrections and closures (from TDD §14 GAP-01…GAP-14)

| ADR | Closes | Finding | Gate |
|---|---|---|---|
| [0013](0013-module-federation-optimisation-flags.md) | GAP-01, GAP-02, GAP-03 | `disableShared` contradicts the React singleton; the ≤ 8 KB budget needs `disableSnapshot`; `externalRuntime` requires the shell to provide the runtime | PH-6 |
| [0014](0014-route-data-strategy.md) | GAP-04 | Nothing stated when the aggregator is in the request path | PH-2 |
| [0015](0015-aggregator-forwards-the-user-subject.md) | GAP-05 | Identity propagation across the aggregator unspecified | PH-6 |
| [0016](0016-self-declared-ownership-invariants.md) | GAP-06 | §7.2 precedence undefined; nothing forbade claiming another team's directory | PH-2 |
| [0017](0017-boundary-enforcement-scope.md) | GAP-07 | "Two mechanisms" overstated: Turbo cannot express AC-03/AC-08 today | PH-7 |
| [0018](0018-direnv-activation-with-pinned-script.md) | GAP-08 | devenv 2.x moved; the `.envrc` snippet is unpinned against D-11 | PH-5 |
| [0019](0019-artefact-duplication-budgets.md) | GAP-09 | Nothing bounded artefact duplication, remote count, CSS or mount latency | PH-8 |
| [0020](0020-contract-verification-against-the-published-schema.md) | GAP-10 | Consumer tests run against a stale local schema | PH-6 |
| [0021](0021-deny-by-default-authorisation-coverage.md) | GAP-11 | `authorises: every-request` was decorative; a public route was compliant | PH-6 |
| [0022](0022-generated-artefacts-are-tamper-evident-not-exempt.md) | GAP-12 | The generator writes into other teams' directories | PH-3 |
| [0023](0023-shell-attested-sessions.md) | GAP-13 | "External consumers prohibited" had only a code-level check | PH-6 |
| [0024](0024-stable-remote-manifest.md) | GAP-14 | `contenthash` filenames and "redirect without a rebuild" were incompatible | PH-6 |
| [0025](0025-no-asynchronous-inter-context-integration.md) | — (decision) | No event streams in v3.0.0; revisiting trigger defined | PH-6 |
| [0026](0026-generated-dependency-manifests.md) | — (decision) | Package dependency lists are generated from the interface ledger | PH-3 |
| [0027](0027-phase-sequencing-is-dependency-gated.md) | — (decision) | IMPLEMENTATION-PLAN §3.1: phases gate on declared prerequisites (D-1…D-7), with a closed four-pair overlap set and two hard exclusions | PH-1 |
| [0028](0028-one-owner-per-derived-fact.md) | — (decision) | Every derived fact has exactly one owner; prose states rules, the model holds values; a check that must parse prose is not a check | PH-1 |

---

## Traceability: DEC → ADR

| PRD decision | ADR |
|---|---|
| DEC-01, DEC-02 | 0001 |
| DEC-03 | 0002 |
| DEC-04, DEC-09 | 0003, 0004 |
| DEC-08 | 0005 |
| DEC-15 | 0006 |
| D-05 (provider/consumer) | 0007 |
| D-12 (ownership resolution) | 0008, 0016 |
| DEC-12 | 0009 |
| DEC-06, NG-03 | 0010 |
| DEC-16 | 0011 |
| DEC-14 | 0012, 0017 |
| DEC-05 (banner only), DEC-07 | 0011, 0018 |
| DEC-11 (no federation), DEC-13 (Team API not normative) | 0004, 0006 |
| DEC-17…DEC-19 | 0021, 0026, 0013 |
| DEC-20…DEC-24 | 0013, 0019, 0020, 0026 |
| DEC-10 | — **uncovered; see note below** |
| DEC-21, DEC-22 | 0020, 0012 |
| PRD §18 (phase ordering) | 0027 |
| ADR range, §21 completion gate, gate naming, one-owner-per-fact | 0028 |

Every PRD decision maps to at least one ADR. Decisions with **no** ADR are decisions nobody has made deliberately.

**One exception, recorded rather than papered over.** `DEC-10` ("Floating remote versions? Prohibited. Every build-affecting reference is pinned") is claimed by no record. The previous version of this line asserted full coverage; that assertion was false, and the mechanical check `DOC-05` now reports it. Whether `DEC-10` needs its own ADR depends on a judgement this set has not yet made: pinning policy is enforced by `check:pins` and `D-11`, which is strong enforcement on cheap-to-reverse ground (dependency versions are reversible per RES-01), and `README.md` rule 3 says a decision gets an ADR only if it is expensive to reverse. **On that reading `DEC-10` is enforced and does not need one, and the honest fix is to record it here as deliberately ADR-less rather than to manufacture a record to satisfy a coverage count.** If the TL or PM disagrees, the ADR is theirs to demand; SA will write it.

---

## Requested changes to `docs/PRD.md` (to be applied as PRD v3.1.0)

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
