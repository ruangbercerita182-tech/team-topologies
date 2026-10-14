# Overall Implementation Plan

| Field | Value |
|---|---|
| Document ID | IMP-CMS-001 |
| Version | 1.0.0 |
| Status | Proposed |
| Date | 2026-10-14 |
| Accountable | **Project Manager** (RACI-CMS-001 §2) |
| Basis | PRD-CMS-001 v3.0.0 §18 (phases), §19 (risks), TDD-CMS-001, RACI-CMS-001 |
| Companion | `TECHNICAL-IMPLEMENTATION-PLAN.md` (TL), `TEST-PLAN.md` (QA), `DEPLOYMENT-PLAN.md` (DevOps), `adr/` (SA) |

---

## 1. Objective and definition of success

The programme does **not** deliver a CMS. It delivers a **repository whose architecture is derived from metadata, enforced mechanically, and provably so** — the substrate on which a CMS product organisation later builds (PRD §2 NG-07). Success is PRD §21: every FR verification passes, every PERF/RES threshold is measured in CI, every AC has a seeded violation proving its check fails.

**Anti-goal for this plan:** shipping features. Any task in this plan that cannot be justified by a PRD identifier is out of scope, regardless of how obviously useful.

---

## 2. Resourcing

| Role | Allocation | Peak | Notes |
|---|---|---|---|
| Solution Architect | 0.5 FTE | 1.0 during PH-3, PH-6, PH-7 | architectural gates, ADRs |
| Technical Lead | 1.0 FTE | 1.0 from PH-2 | owns the WBS and the design |
| Platform engineers | 2.0 FTE | 2.5 during PH-3 | generator, templates, checks — the critical path |
| Web engineers (shell + aggregator) | 2.0 FTE | 2.0 during PH-6 | the only client platform implemented (NG-02) |
| Banner engineers (context) | 1.0 FTE | 1.5 during PH-6 | reference bounded context |
| QA | 0.5 FTE | 1.0 during PH-7, PH-8 | verification, not assistance |
| DevOps | 0.5 FTE | 1.0 during PH-5, PH-8, PH-9 | environments, CI, cutover |
| Product Owner | 0.2 FTE | 0.5 at phase gates | acceptance of exits |

**Key-path staffing observation.** Platform engineering is both the highest-loaded role and the owner of the artefact every other team consumes (the generator). SPL-02 exists precisely because of this concentration; the plan treats it as the top structural risk (§6, R-1) rather than as a contingency.

---

## 3. Schedule

Phases are ordered per PRD §18. Durations are calendar weeks at the staffing above, and include review latency.

| Phase | Weeks | Cumulative | Entry criterion | Exit criterion (abbrev.) | Accountable |
|---|---|---|---|---|---|
| **PH-1** Workspace truth | 2 | 2 | plan accepted | one lockfile; no nested `.git`; no duplicate package names; cross-team PR rejected | TL |
| **PH-2** Metadata layer | 3 | 5 | PH-1 exit | `catalog:validate` passes; 4 seeded violations each fail with a precise message | TL |
| **PH-3** Generator | 3 | 8 | PH-2 exit | `catalog:generate && git diff --exit-code` clean | SA |
| **PH-4** Scaffolding + platform contracts | 2 | 10 | PH-2 exit | each template yields a unit passing typecheck/lint/boundaries, zero edits | TL |
| **PH-5** Environment, config, cache | 2 | 12 | PH-1 exit | `devenv up` cold ≤ 300 s, warm ≤ 10 s; invalid env fails before binding | DevOps |
| **PH-6** Reference context + aggregator | 4 | 16 | PH-3 + PH-4 exit | contracts green; aggregator store-free; **OTel browser instrumentation present** | SA |
| **PH-7** Boundary + shell purity | 2 | 18 | PH-5 exit | all `check:*` pass; 4 seeded violations each fail | SA |
| **PH-8** Performance + resource | 3 | 21 | PH-6 + PH-7 exit | PERF-02/03 enforced; budgets in CI; dev-server RSS baseline has 3 data points | QA |
| **PH-9** Relocation to team-scoped layout | 3 | 24 | PH-1…PH-7 exit | `apps/`, `bff/`, `packages/`, `composition/` gone; one MF host; `check:pins` zero | TL |
| **PH-10** Documentation + ADRs | 2 | 26 | PH-9 exit | a newcomer completes a local run from docs alone; every ADR in `adr/` cites ≥ 1 `R-xx`; ADR-0027 (sequencing) accepted | SA |

**Total: ~26 weeks (~6 months), 10 phases.** With a second platform engineer, PH-3 shortens by roughly 1 week; without a second web engineer, PH-6 does not shorten at all, because it is the only phase where the reference implementation must be genuinely good rather than merely compliant.

### 3.1 Proposed relaxation of strict sequencing (requires ADR + PO sign-off)

PRD §18 states a phase starts only when the previous phase's exit criterion holds. Strictly serialising all ten costs ~4 weeks and delays the first moment a violation can be caught. The plan proposes gating on **exit criteria of prerequisites**, allowing overlap where the artefacts are independent:

| Overlap permitted | Why it is safe | Cost of not doing it |
|---|---|---|
| PH-4 ∥ PH-3 | templates consume the catalogue, not the generator | +1 week |
| PH-5 ∥ PH-3/PH-4 | environment work touches `devenv.nix`, not `catalog/` | +1 week |
| PH-7 ∥ PH-6 (checks first, seeded violations second) | checks are static analysis; the reference implementation is what they analyse | +1 week |
| PH-10 documentation drafting ∥ PH-9 | docs describe artefacts that exist from PH-3 | +1 week |

**Not permitted:** PH-9 relocation before PH-3 (the generator produces the new `CODEOWNERS` and boundaries for the new layout), and PH-8 before PH-7 (a budget without an enforcement gate is a wish — PRD §15).

**Decision owner:** PM, with SA confirming the architectural safety argument. Default if undecided: serialise.

---

## 4. Milestones

| ID | Milestone | Phase | Demonstrable outcome | Sign-off |
|---|---|---|---|---|
| **M1** | Truthful workspace | PH-1 | `turbo run typecheck` executes in every package; five lockfiles reduced to one | TL |
| **M2** | Metadata is authoritative | PH-3 | a route added in YAML appears in the shell with no code edit | SA |
| **M3** | Self-service | PH-4 | a new context scaffolded in ≤ 60 s, passing every check | TL |
| **M4** | Reproducible environment | PH-5 | `devenv up` from a clean checkout, twice, identically | DevOps |
| **M5** | Reference vertical slice | PH-6 | banner context + web aggregator, contract-verified, no rules in the BFF | SA |
| **M6** | Boundaries are real | PH-7 | four seeded violations, each caught by two independent tools | SA |
| **M7** | Performance is measured | PH-8 | an oversized route fails CI; `remoteEntry` ≤ 8 KB | QA |
| **M8** | Target topology | PH-9 | exactly one MF host; prohibited directories gone | TL |
| **M9** | Handover-ready | PH-10 | a new engineer runs the stack from docs with no help | SA |

---

## 5. Cross-phase dependencies (the ones that bite)

| # | Dependency | Blocks | Consequence if wrong |
|---|---|---|---|
| D-1 | Generator (PH-3) before relocation (PH-9) | PH-9 | manual `CODEOWNERS` edits; G-04 lost |
| D-2 | `package.json` deps generated (ROW-10) before boundary enforcement | PH-7 | Turborepo's undeclared-dependency check fires on every legitimate edge |
| D-3 | OTel browser instrumentation before a **second** remote exists | PH-6 exit | retroactive instrumentation across N bundles — the cost PRD §11.4 warns about |
| D-4 | Contract digest (GAP-10) before the first provider version bump | PH-6+ | a consumer is green against a contract that already changed |
| D-5 | Route `dataStrategy` (GAP-04) before the second bounded context | PH-6+ | the aggregator becomes either dead or bypassed; the first real decision is made by accident |
| D-6 | `devenv` pin + pinned `direnvrc` (GAP-08) before onboarding anyone | PH-5 | every developer hand-patches their environment; reproducibility is lost at the first new hire |
| D-7 | Budget metadata before any budget is claimed | PH-8 | thresholds live in prose and in code, and re-baselining becomes invisible |

---

## 6. Risk register (programme view)

The PRD's RISK-01…RISK-17 are technical and remain owned by the SA. This register adds the **programme** risks that a PM owns.

| ID | Risk | Likelihood | Impact | Mitigation | Trigger to escalate | Owner |
|---|---|---|---|---|---|---|
| **R-1** | Platform team becomes the bottleneck (PRD RISK-13) | High | High | Cap platform scope at the generator/templates/checks; every non-platform request is refused by the ownership rule. Second platform engineer from PH-3. Measure `check:*` SLOs quarterly | SPL-02 trigger: 2 quarters of missed check SLOs | PM + SA |
| **R-2** | Generator scope creep — it becomes a framework | Medium | High | The generator emits 10 artefact classes and nothing else. A new output requires an ADR (D-13) | any 11th artefact class proposed | TL |
| **R-3** | Enforcement adopted but not funded — checks rot | Medium | High | Every check has a seeded fixture in the same PR. A check whose fixture is deleted fails review | a check lands without a fixture | TL + QA |
| **R-4** | Phase exits are argued instead of measured | Medium | High | Every exit criterion is a command with an exit code; a verbal exit is not an exit | any exit accepted without the command output | PM |
| **R-5** | Reference implementation quality gets sacrificed for compliance | Medium | High | PH-6 is the exemplar the templates copy. "It passes the checks" is explicitly insufficient there | PH-6 exit accepted with known shortcuts | SA |
| **R-6** | devenv adoption friction stalls onboarding (PRD RISK-08) | Medium | Medium | `devenv.local.*` for per-developer escape; measure time-to-first-run as a phase-5 metric | median onboarding > 1 working day | DevOps |
| **R-7** | Performance budgets land after the first regression is normalised | Medium | Medium | PH-8 explicitly re-baselines the current numbers first, then tightens; RES-07 collects 3 data points before any threshold is asserted | a regression reaches `main` before PH-8 | QA |
| **R-8** | Single-client reality hides aggregator design flaws | High | Medium | PH-6 forces one `composed` route with two contexts, so the aggregator is exercised before the second context really exists | no `composed` route exists at PH-6 exit | SA |
| **R-9** | Scope creep from "we might as well build the CMS" | High | High | NG-07 and NG-01 remain exclusions; any feature request during the programme is logged as post-programme, not absorbed | a feature PR targets a platform package | PO |
| **R-10** | Reference drift as tooling moves (the GAP-08 class of problem) | High | Low–High | Every vendor-documented behaviour carries a re-verify trigger (§21.1); CI fails loudly when an upstream default changes shape | an upstream release changes a cited behaviour | SA |

---

## 7. Governance cadence

| Cadence | Meeting | Attendees | Output |
|---|---|---|---|
| Weekly | Delivery review: WBS status, blocked items, seeded-violation health | TL, team leads, QA | updated `TECHNICAL-IMPLEMENTATION-PLAN.md` status column |
| Weekly | Architecture clinic: any proposed change to a `D-`/`ALG-`/`BUD-` element | SA, TL | ADR opened or explicitly rejected |
| Per phase | **Exit review** — run the phase's exit commands live, in the room | SA/TL/QA per RACI §4 | signed exit or a named blocker |
| Monthly | Risk review: R-1…R-10 and PRD RISK-01…17 | PM, SA | updated register |
| Quarterly | Budget review: every `catalog/budgets.yaml` entry, re-baseline proposals | budget owners, FinOps | ADR per re-baseline (no silent changes, PRD RISK-15) |

**No meeting is added for a reason that cannot be named.** PRD/R-TT-01's cognitive-load argument applies to governance too.

---

## 8. Change control

| Change type | Approval | Effect on plan |
|---|---|---|
| Within a phase, ≤ 2 working days | TL | none |
| Adding a task inside a phase | TL, informed to PM | none |
| Reordering or overlapping phases | PM + SA | schedule re-baseline |
| Adding or relaxing a requirement/constraint/decision | SA, PO informed | **ADR required**; PRD version bump if normative |
| Changing a budget threshold | budget owner + ADR | quarterly window only |
| Splitting a bounded context or changing ownership | both teams + SA | may trigger SPL review |

The single most important line: **a schedule change is never a licence to skip a phase exit.** Every shortcut taken under schedule pressure is written into the register as a debt item with an owner and a date.
