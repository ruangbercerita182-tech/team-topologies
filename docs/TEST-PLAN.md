# Test Plan

| Field | Value |
|---|---|
| Document ID | TEST-CMS-001 |
| Version | 1.0.0 |
| Status | Proposed |
| Date | 2026-10-14 |
| Accountable | **QA / Test Lead** (RACI-CMS-001 §2) |
| Basis | PRD §14 (FR-01…FR-28), §12 (PERF-01…13), §13 (RES-01…10), §15 (AC-01…12); TDD §13 (CHK-01…21) |
| Rule | QA verifies. QA does not implement fixes. The verifier is never the implementer (RACI §4) |

---

## 1. Strategy in one paragraph

Verification here is overwhelmingly **not** manual test execution. Almost every normative statement in this programme is either a static property (a graph, a schema, a file layout) or a measured number (a size, a time, a ratio). Both are executable. The test strategy is therefore: **one assertion per requirement, expressed as a command with an exit code, run in CI, and proven to fail by a seeded fixture.** Manual and exploratory testing remains, but it is a small and *differently purposed* activity: finding the requirement that nobody wrote down.

---

## 2. Test levels

| Level | Scope | Runs on | Gate | Owner of the harness |
|---|---|---|---|---|
| **L0 — Schema** | catalogue validity, ownership invariants, relation closure, budget schema | every PR | blocks merge | Platform (T-201) |
| **L1 — Static architecture** | layer rules, purity rules, vocabulary rules, dependency graph, pin check | every PR | blocks merge | Platform + TL |
| **L2 — Unit** | domain (pure, no mocks), application (fakes), generators | every PR | blocks merge | owning team |
| **L3 — Contract** | provider schema vs consumer expectations, incl. denial cases | every PR | blocks merge | owning teams jointly |
| **L4 — Slice / integration** | HTTP slices, store integration, aggregator pipeline | every PR to `main` | blocks merge | owning team |
| **L5 — Composition** | shell + remote(s) + aggregator + context, assembled from the built artefacts | per release | blocks release | QA |
| **L6 — Budget** | bundle, artefact, duplication, CSS, time, cache, cost | per release + nightly | blocks release | QA + DevOps |
| **L7 — Exploratory** | one session per phase exit, on the phase's own user-visible outcome | phase boundary | informs exit review | QA + PO |

**Ordering principle:** L0/L1 are cheap, run first, and are what make the later levels trustworthy. A failure at L7 when L1 was skipped is the most common way a programme discovers an architectural breach as a production incident.

---

## 3. Test cycles

| Cycle | Trigger | Content | Exit criteria |
|---|---|---|---|
| **C0 — Pre-merge** | every push to a PR | L0–L4 | all green; every seeded fixture still fails |
| **C1 — Merge to `main`** | merge | L0–L4 again (uncached, to catch cache-key bugs) + affected-task selection | green; cache hit ratio reported |
| **C2 — Release candidate** | release of any deployable | C1 + L5 + L6 | all budgets met; rollback rehearsed |
| **C3 — Nightly** | 02:00 | L6 telemetry: cache ratio, dev-server RSS, container limits, cost attribution | report published; drift alerts on |
| **C4 — Phase exit** | phase boundary | all applicable levels + L7 exploratory + exit commands run live | exit review signed (RACI §4) |
| **C5 — Quarterly** | quarterly | budget re-baseline review, reference-catalogue re-verification, SPL trigger evaluation | ADRs for any re-baseline (no silent changes) |

---

## 4. Coverage matrix — the three maps QA maintains

### 4.1 FR → test

| FR group | Checks | Level | Seeded fixture |
|---|---|---|---|
| FR-01, FR-11, AC-11 | `check:lsc`, branch protection | L1 | cross-team PR with one approval |
| FR-02…04, FR-06, FR-07, FR-13, D-04 | `check:catalog` | L0 | unknown key; dangling relation; `direct` with 2 contexts |
| FR-05, FR-08, FR-09, FR-10 | `check:generated-fresh` | L0/L1 | hand-edited generated file |
| FR-12 | template runner + `typecheck && lint && check:boundaries` | L2 | n/a (timed: ≤ 60 s) |
| FR-14, AC-01, AC-02 | `check:boundaries` | L1 | cross-team import (both tools) |
| FR-15 | `check:tasks`, workspace checks | L1 | lockfile below root |
| FR-16, AC-09 | `check:config-strict` | L4 | unknown env key |
| FR-17, FR-18 | devenv/direnv assertions | L1 | `.envrc` containing `[whitelist]` |
| FR-19, FR-22, AC-08 | `check:layers` | L1 | `domain/` importing `@nestjs/common` |
| FR-20 | authz lint | L1 | an org-specific condition string in `authz/` |
| FR-21 | `check:pins` | L1 | `@latest` fixture |
| FR-23 | `check:contracts` | L3 | adapter expectation diverging from provider |
| FR-24 | CI reuse check | L1 | a duplicated workflow body |
| FR-25 | cache-config checker | L1 | an undeclared env var in a cacheable task |
| FR-26…28, AC-10 | `check:repo-shape`, `check:tasks` | L1 | nested `.git`; a task resolving to zero packages |

### 4.2 PERF / RES → measurement

| Requirement | Instrument | Where | Baseline then threshold |
|---|---|---|---|
| PERF-01 | RUM + Lighthouse CI | L5/L6 | field data p75, segmented |
| PERF-02, PERF-03, BUD-06/08 | `size-limit` + Lighthouse budgets | L6 | 300 KB route / 8 KB `remoteEntry` |
| PERF-04 | network trace in CI | L6 | no off-route remote fetch |
| PERF-05 + singletons | runtime assertion at shell start | L5 | exactly 1 React, 1 federation runtime, 1 tracer |
| PERF-06 | in-process histogram, **p99** | L2/L6 | per route class SLO |
| PERF-07 | plan/trace inspection | L2 | zero gratuitous `Sequence` |
| PERF-08 | instrumented call counts | L2 | zero N+1 |
| PERF-09 | config assertion + retry metric | L6 | retry ≤ 10 % |
| PERF-10 | `monitorEventLoopDelay` p99 | L6 | < 50 ms |
| PERF-11 | cache-hit + read-amplification metric | L6 | single-flight on hot keys |
| PERF-12 | manifest assertion | L6 | every container declares limits |
| RES-03, RES-04, RES-05, RES-05a, RES-06 | timers in CI | L3 | 10 s / 300 s / 5 s / 60 s / 30 s |
| RES-07 | dev-server RSS, fixed fixture | C3 | **3 data points before any threshold** |
| RES-08 | cache telemetry | C3 | ≥ 80 % on `main` |
| RES-09, RES-10 | image size + FinOps allocation | C3 | multi-stage, no shell in base image |

### 4.3 AC → enforcement

| AC | Enforced by | Redundant with another mechanism? |
|---|---|---|
| AC-01 | `turbo boundaries` **and** dependency-cruiser | **yes** (package graph) — see TDD §13.1 / GAP-07 |
| AC-02 | dependency-cruiser | yes |
| AC-03 | dependency-cruiser | **no** — Turbo cannot express an npm deny list (R-BND-13) |
| AC-04 | `check:catalog` | no |
| AC-05 | vocabulary lint + `no-restricted-imports` | no |
| AC-06 | `no-restricted-imports` + cycle check | no |
| AC-07 | catalogue co-ownership + branch protection | no |
| AC-08 | dependency-cruiser layers | **no** — intra-package, outside Turbo's model |
| AC-09 | `check:config-strict` | no |
| AC-10 | filesystem check | no |
| AC-11 | branch protection + trailer check | no |
| AC-12 | `check:authz-placement` | no |

**Seven of twelve constraints have exactly one enforcing mechanism.** That is a deliberate, recorded fact (TDD §13.1), not an oversight: each of the seven is a file-graph or npm-dependency rule that a package-graph tool cannot express. The compensation is that each carries a seeded fixture, so "single mechanism" never means "unverified mechanism".

---

## 5. Test data strategy

| Class | Handling |
|---|---|
| Fixtures | small, deterministic, checked in, per-fixture README; a fixture's hash appears in the CI run so a pass cannot be attributed to a changed fixture |
| Generated data | seeded PRNG only; the seed is checked in and printed on failure |
| Personal data | synthetic only; real personal data never enters a fixture or a test environment |
| Contract tests | run against the provider's **published** schema (TDD INT-05), never a local copy |
| Database | per-run isolated; migrations applied per run; **one test asserts migrations are expand/contract only** |
| Time and randomness | injected ports; a test that depends on the wall clock or on randomness is a defect (D-14) |

## 6. Non-functional test approach

| Aspect | Approach |
|---|---|
| Performance | budgets in CI (L6) + field data (C3); a regression is a build failure, not a report |
| Resilience | fault injection at each aggregator dependency: timeout, 5xx, slow-body, reset. Assert partial responses and that the retry budget is not exceeded |
| Security | the four classes QA owns directly: session handling (CSRF, cookie flags, expiry), authorisation denial cases per context, aggregator attestation rejection, remote-origin CSP enforcement |
| Accessibility | keyboard navigation and focus management **across** remote boundaries — the shell must not lose focus order when a remote mounts; this is the one place micro-frontending degrades UX and it is routinely untested |
| Compatibility | the browser matrix from the Web Almanac's own top set, applied to the composed page |
| Observability | a smoke test that a synthetic user action produces one connected trace with a remote child span (§11.5 / D-19) — if tracing breaks, the programme loses its ability to debug itself |

## 7. Entry and exit criteria

**Entry into a test cycle:** the artefact under test exists, its acceptance command exists, and its seeded fixture exists. A cycle does not start for work that cannot fail.

**Exit from a phase (C4):**

1. every FR verification in §4.1 executes and passes;
2. every PERF/RES in §4.2 is measured — thresholds met, or a named re-baseline ADR exists;
3. every AC has its mechanism present **and** its fixture failing;
4. `catalog:validate && catalog:generate && git diff --exit-code && turbo boundaries && dependency-cruiser` exits zero on a clean tree;
5. L7 exploratory session completed with findings either fixed or explicitly accepted;
6. no finding older than one phase remains open without an owner.

**Exit is signed by QA for PH-8 and by the SA or TL per RACI §4 for the others** — QA prepares the evidence, the accountable role signs. A phase is not complete because time ran out.

## 8. Test risks

| ID | Risk | Mitigation |
|---|---|---|
| Q-1 | Checks pass vacuously (nothing ran) | FR-28 asserts every declared task resolves to ≥ 1 package; a check that selects zero files is itself an error |
| Q-2 | Fixtures deleted once a check is green | deleting a fixture fails review; the fixture is referenced from the check's own file header |
| Q-3 | Budgets tuned until they never fail | RES-07 collects 3 points before asserting; the baseline-before-threshold order is in §4.2 |
| Q-4 | Performance verified only in lab | BUD-09 requires field data tagged by route and remote |
| Q-5 | The verifier becomes the implementer | RACI §4 fixes this; QA's tasks are never "fix it" |
| Q-6 | Security testing collapses into "the tool passed" | the four security classes in §6 are executed by a person, not inferred from a linter |
