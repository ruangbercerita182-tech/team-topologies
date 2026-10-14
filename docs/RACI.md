# RACI — Responsibilities, Artefacts and Decision Rights

| Field | Value |
|---|---|
| Document ID | RACI-CMS-001 |
| Version | 1.0.0 |
| Status | Proposed |
| Date | 2026-10-14 |
| Governs | `docs/IMPLEMENTATION-PLAN.md`, `docs/TECHNICAL-IMPLEMENTATION-PLAN.md`, `docs/TEST-PLAN.md`, `docs/DEPLOYMENT-PLAN.md`, `docs/adr/` |
| Basis | `docs/PRD.md` (G-01…G-10, DEC-01…DEC-24), `docs/TDD.md` (TDD-CMS-001) |

**R** = Responsible (does the work) · **A** = Accountable (one name, signs it off) · **C** = Consulted (input required before the decision) · **I** = Informed (told after).

The single rule this document enforces: **one accountable name per artefact and per decision.** A document with two owners has none.

---

## 1. Role definitions and the accountability test

| Role | Owns in the implementation plan | Accountability test |
|---|---|---|
| **Business Analyst / Product Owner** | Business requirements, acceptance criteria, stakeholder readiness | Every FR traces to a user-visible outcome the PO can accept or reject |
| **Solution Architect (SA)** | Solution architecture, architectural ordering, ADRs, boundary decisions | Every architectural choice has an ADR citing ≥ 1 verified `R-xx` |
| **Technical Lead (TL)** | Technical design module specs, work breakdown, effort, execution strategy | Every module in `TDD §24` has an owner and an acceptance test |
| **Developer / Engineering Team** | Estimation of technical tasks, implementation | A task is done when its check passes, not when the code is merged |
| **QA / Test Lead** | Test plan, test cycles, exit criteria | Every FR, PERF, RES and AC has at least one executable test, listed in `TEST-PLAN.md` |
| **DevOps / Infrastructure** | Environments, CI/CD, deployment, configuration, operational readiness | Every environment is reproducible from a committed definition |
| **Project Manager (PM)** | Schedule, milestones, resources, dependencies, risk, coordination | A phase starts only when the previous phase's exit criterion objectively holds (PRD §18) |

**Every role above is both a producer and a consumer.** No role is exempt from a phase's exit criterion.

---

## 2. Artefact ownership (canonical)

| Artefact | Accountable (A) | Responsible (R) | Consulted | Informed | Status |
|---|---|---|---|---|---|
| Business requirements / functional specification | **Product Owner** | BA | SA, TL, QA | all | *product-facing spec — not yet produced; out of scope for this repository, which is an engineering-standards repo (PRD NG-07)* |
| **Solution Architecture** | **Solution Architect** | SA | TL, DevOps, Platform team, all stream-aligned leads | PM, PO | ✅ `docs/PRD.md` §1–§5, §16 · `docs/TDD.md` §4–§8, §18–§23 |
| **Technical Design** | **Technical Lead** | TL, under SA direction | SA, developers, QA | PM | ✅ `docs/TDD.md` — **split by section, see §3** |
| **Technical Implementation Plan** | **Technical Lead** | TL | SA, team leads, QA | PM | ✅ `TECHNICAL-IMPLEMENTATION-PLAN.md` |
| **Overall Implementation Plan** | **Project Manager** | PM | TL, SA, DevOps, QA, PO | steering group | ✅ `IMPLEMENTATION-PLAN.md` |
| **Test Plan** | **QA / Test Lead** | QA | TL, developers, SA | PM, PO | ✅ `TEST-PLAN.md` |
| **Deployment / Cutover Plan** | **DevOps lead** (TL co-signs on app-ordering) | DevOps | TL, SA, developers | PM, QA | ✅ `DEPLOYMENT-PLAN.md` |
| **Decision records (ADR)** | **Solution Architect** | SA | TL, affected team lead | all | ✅ `adr/` — 27 records, §5 |
| **Reference catalogue** | **Solution Architect** | SA | all | all | ✅ `docs/references.md` |
| **Ownership ledger / catalogue schema** | **Platform team lead** | platform developers | SA | all | `catalog/` — produced in PH-2 |

---

## 3. The one deviation, and why it is deliberate

The ownership table says Technical Design is *Technical Lead's*, under architectural direction from the *Solution Architect*. `TDD.md` was therefore written as one document, and that is a deviation worth naming rather than hiding:

| Part of `TDD.md` | Natural owner | Status |
|---|---|---|
| §1–§17 (planes, ownership ledger, algorithms, gaps) | **Solution Architect** | architecture — A: SA |
| §18–§23 (the seven views, minus module specs) | **Solution Architect** | architecture — A: SA |
| §24 (MOD-1…MOD-10 module specifications) | **Technical Lead** | technical design — A: TL |
| §13 check inventory | TL, with SA owning the *set* of constraints | split: SA owns which constraints exist, TL owns how they are implemented |

**Resolution:** on PH-1 kickoff, `TDD.md` §24 and §13 are frozen as the TL's artefact and re-approved by the SA. Splitting the file is optional; splitting the **accountability** is not. If the two views are later separated physically, the ID prefixes (`D-`, `ALG-`, `BUD-`, `CHK-`, `MOD-`) must not be renumbered, because `docs/PRD.md` and the ADRs cite them.

---

## 4. Phase-level RACI

Phases are PRD §18 `PH-1 … PH-10`. `V` = verifies the exit criterion (independently of the team that did the work).

| Phase | PO | SA | TL | Dev | QA | DevOps | Gate |
|---|---|---|---|---|---|---|---|
| **PH-1** Workspace truth | I | C | A | R | I | C | TL |
| **PH-2** Metadata layer | I | C | A | R | C | I | TL |
| **PH-3** Generator | I | C | A | R | V | I | SA |
| **PH-4** Scaffolding + platform contracts | I | C | A | R | C | I | TL |
| **PH-5** Environment, config, cache | I | C | A | R | I | R | DevOps |
| **PH-6** Reference context + aggregator | C | C | A | R | C | C | SA |
| **PH-7** Boundary + shell purity enforcement | I | C | A | R | V | I | SA |
| **PH-8** Performance + resource enforcement | I | C | A | R | V | R | QA |
| **PH-9** Relocation to team-scoped topology | I | C | A | R | V | R | TL |
| **PH-10** Documentation + decision records | I | **A/R** | C | C | C | C | SA |

**Three patterns in that table are deliberate:**

1. **SA is consulted, never responsible, for execution phases.** The architect who also implements stops noticing their own wrong assumptions.
2. **The verifier is never the implementer.** PH-3, PH-6, PH-7, PH-8, PH-9 are verified by QA or the SA because a green pipeline produced by the team that wrote the pipeline is not evidence (PRD FR-28's spirit).
3. **DevOps is Responsible, not Accountable, for PH-5.** The Technical Lead owns the outcome (a reproducible environment); DevOps does the work. Reversing this is the most common way environments become unreproducible — the person who provisions them stops feeling responsible for whether they can be derived.

---

## 5. Decision rights

| Decision class | Decided by | Must consult | Reversibility |
|---|---|---|---|
| Repository topology, team boundaries | **SA** | Platform lead, all team leads | Reversible only via SPL-01…SPL-05 (PRD §4.5) |
| Layer/plane separation, ownership invariants | **SA** | TL | Cheap — but touches D-10/D-12, so still an ADR |
| Which technology, which version | **TL** | SA | Reversible (RES-01) |
| Anything entering `domain/` or the `shared` singleton list | **SA** (ADR) | TL, Platform lead | Expensive — the whole point of the rule |
| A budget threshold change | **budget owner** (in `catalog/budgets.yaml`) | TL, FinOps | Cheap, but requires an ADR record |
| Test exit criteria | **QA** | TL, PM | Cheap |
| Schedule, scope trade-off inside a phase | **PM** | TL | Cheap |
| Anything crossing a team boundary | **both owning teams + SA** | — | LSC (PRD FR-01) |
| Risk acceptance | **PM** | SA, TL | Recorded in the risk register |

**Escalation path:** developer → TL (1 day) → SA (architecture disagreement) → PM+PO (scope or schedule). An escalation that has not produced a written outcome in 5 working days is itself a schedule risk and goes on the register.

---

## 6. Artefact flow

```
PRD (SA) ──► TDD (SA §1-23, TL §24) ──► TECH IMPLEMENTATION PLAN (TL)
     │                                            │
     │                                            ├──► TEST PLAN (QA)  ── independent verification
     │                                            ├──► DEPLOYMENT PLAN (DevOps)
     ▼                                            │
  ADRs (SA) ────────── architectural gates ────────┘
     │
     └──► catalogue (Platform) ──► generated topology ──► checks (TL) ──► CI (DevOps)
```

No artefact is written without its accountable role, and no phase starts without the artefact upstream of it being accepted.
