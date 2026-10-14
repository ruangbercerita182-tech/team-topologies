# Technical Implementation Plan

| Field | Value |
|---|---|
| Document ID | TIMP-CMS-001 |
| Version | 1.0.0 |
| Status | Proposed |
| Date | 2026-10-14 |
| Accountable | **Technical Lead** (RACI-CMS-001 §2) |
| Basis | `TDD-CMS-001` §8 (pipeline), §9 (context internals), §10 (frontend), §13 (checks), §24 (modules) |
| Companions | `IMPLEMENTATION-PLAN.md` (schedule), `TEST-PLAN.md` (verification) |

Every task carries: **ID · what · artefact produced · blocked by · effort (person-days) · role · acceptance (a command with an exit code)**. A task without an executable acceptance is not scheduled; it is wished.

Effort is engineering days including review, stated as point estimates. Each phase header states the arithmetic sum of its tasks; **a header that disagrees with its own table is a defect**, and this plan treats it as one (§14). Programme total: **129.0 pd**.

### 0.1 Identifier namespaces

Three `D-nn` families and several check names collide across the document set. Every citation in this plan is therefore qualified:

| Written as | Means | Never means |
|---|---|---|
| `TDD D-nn` | TDD design definition (§3–§24), D-01…D-20, D-25…D-33 | PRD definitions |
| `PRD D-nn` | PRD normative definitions, D-01…D-12 | TDD definitions |
| `D-nn` (cross-phase) | dependency register in `IMPLEMENTATION-PLAN.md` §5, D-1…D-7 | either D-family above |
| `R-n` (programme) | risk register in `IMPLEMENTATION-PLAN.md` §6, R-1…R-10 | `references.md` evidence codes |
| `check:*` | TDD §13 check inventory, `CHK-01`…`CHK-22` | the generator's `catalog:*` commands |

The PRD names two gates `pins:check` and `catalog:verify-ownership`; TDD §13 names the same gates `check:pins` (CHK-09) and `check:catalog` (CHK-01). **This plan uses the TDD §13 names**, because CHK is the inventory every phase exit is measured against; the PRD naming is recorded as a defect for the SA in §14.

---

## 1. Ordering principle

Tasks are ordered by **architectural dependency, not by convenience**. A task that would require rewriting an earlier task is scheduled *after* the decision that makes it unnecessary. Three orderings dominate the plan:

1. **Metadata before generator before enforcement.** No check may be written against an artefact whose shape is still moving (D-2).
2. **Enforcement before enforcement-of-enforcement.** The boundary checks land after the boundaries they police exist (PH-7 after PH-6), except for checks that analyse no application code.
3. **Instrumentation before the second artefact of its kind.** OTel browser instrumentation precedes a second remote (D-3), and the budget gate precedes the regression it must catch.

---

## 2. PH-1 — Workspace truth (2 weeks · 7.5 pd)

| ID | Task | Artefact | Blocked by | Effort | Role | Acceptance |
|---|---|---|---|---|---|---|
| T-101 | Extend workspaces to `teams/*/*`; namespace-qualify every package name | `package.json` | — | 1.0 | Dev | `check:repo-shape` finds no duplicate name |
| T-102 | Delete per-package lockfiles; consolidate to one root lockfile; make CI install with `--frozen-lockfile` (RES-01, RES-02) | 5 files deleted | T-101 | 0.5 | Dev | `find . -name node_modules -prune -o -name '*.lock' -print \| wc -l` = 1 |
| T-103 | Remove nested `.git` directories | — | — | 0.25 | Dev | `check:repo-shape` |
| T-104 | Add missing `lint` / `typecheck` scripts to every deployable | manifests | T-101 | 1.0 | Dev | `check:tasks` resolves every declared task to ≥ 1 package |
| T-105 | Correct `README.md` to one documented package manager; declare the manifest-authority rule in `catalog/teams/platform.yaml` (FR-27) | docs | — | 0.25 | Dev + PO | `check:toolchain` (CHK-22, added by T-701) reports exactly one package manager and one lockfile name |
| T-106 | Remove scaffold/demo content | — | — | 1.0 | Dev | manual review + `check:repo-shape` |
| T-107 | Branch protection: required reviewers + LSC trailer rule | repo settings | — | 1.0 | DevOps | `check:lsc` rejects a cross-team PR with one approval |
| T-108 | `check:pins` (CHK-09) — reject floating references in CI | config | — | 0.5 | Dev | `check:pins` fails on a `@latest` fixture |
| T-109 | **Pin every floating reference the gate now reports** (FR-21, PRD D-11) | 5 manifests | T-108 | 2.0 | Dev | `check:pins` exits 0 on the tree; PH-1 exit criterion met |

**Sequencing note.** T-108 detects and T-109 remediates — they are one piece of work split across two commits, because a gate that has never been observed red is not known to work (TDD §13). T-108 cannot be closed while it fails on `main`; land it `continue-on-error` for at most 48 h with a named owner, and T-109 in the same PR. T-108 and T-105 write standalone scripts; T-701 later folds them into the shared harness (`tools/checks`) without changing their exit codes.

---

## 3. PH-2 — Metadata layer (3 weeks · 12 pd)

| ID | Task | Artefact | Blocked by | Effort | Role | Acceptance |
|---|---|---|---|---|---|---|
| T-201 | Catalogue schemas: zod, `.strict()` on every object (TDD MOD-1) | `catalog/schema/*` | T-101 | 2.0 | Dev | `check:catalog` (CHK-01) rejects an unknown key, naming the key path |
| T-202 | `apiVersion` / `kind` / `metadata.id` discipline | schema | T-201 | 0.5 | Dev | missing any of the three fails |
| T-203 | `Team` documents + team types + `owns` shape; invariants O-1/O-2 (**GAP-06**) | `catalog/teams/*.yaml` | T-201 | 1.5 | Dev + TL | `check:ownership` (CHK-02) fails a team claiming `teams/other/**` with E-OWN-INTRUSION |
| T-204 | `BoundedContext` documents incl. ubiquitous-language seeds | `catalog/contexts/*.yaml` | T-201 | 1.0 | Dev | `spec.authorises` accepts only the literal |
| T-205 | `ClientPlatform` documents incl. **`route.dataStrategy`** (**GAP-04**) | `catalog/clients/*.yaml` | T-201 | 1.5 | Dev + SA | `direct` with 2 contexts fails; `composed` with 1 context fails |
| T-206 | `Interface` documents — the ownership ledger made metadata (ROW-01…11) | `catalog/interfaces/*.yaml` | T-201 | 2.0 | Dev + SA | every declared consumer resolves to a known unit |
| T-207 | `Budget` documents | `catalog/budgets.yaml` | T-201 | 1.0 | Dev + TL | `check:budgets` fails a budget with no `gate` |
| T-208 | Relation validation, derived not authored (R-META-26) | validator | T-206 | 1.0 | Dev | `check:relations` (CHK-03) fails an import of a package absent from the generated manifest |
| T-209 | Seed: platform, banner, web teams; banner context; web/mobile/desktop clients | `catalog/**` | T-203…T-208 | 1.5 | Dev | `check:catalog` exits 0 |

**Path note.** The catalogue lives at root `catalog/` until PH-9. PRD §4.3, §8.1, TDD MOD-1 and the S7 purity rule all place it there, and `catalog/teams/platform.yaml` claims `catalog/**` as platform-owned. Placing the schema under `teams/platform/` in PH-2 would front-run the relocation, break S7, and make the generator's input a function of two roots.

---

## 4. PH-3 — Generator (3 weeks · 14.5 pd) · *longest single-task concentration*

| ID | Task | Artefact | Blocked by | Effort | Role | Acceptance |
|---|---|---|---|---|---|---|
| T-301 | Pipeline skeleton: load → validate → plan → emit → verify, one graph, no re-read (MOD-2) | `teams/platform/generator` | T-209 | 3.0 | Dev | `catalog:generate` then `git diff --exit-code` is clean on an unchanged tree |
| T-302 | Byte-stability S1–S7 (LF, key order, no clock/paths, atomic write, marker line); `catalog:generate` ≤ 5 s (RES-05) | MOD-2 | T-301 | 2.0 | Dev | generate twice → identical bytes and unchanged mtimes; `res:timings` (CHK-18) reports ≤ 5 s |
| T-303 | `CODEOWNERS` + `docs/ownership.md` via ALG-4 (**GAP-12** — generator writes into other teams' trees, ADR-0022) | emit | T-301 | 2.0 | Dev | 100 % coverage of tracked paths; 3 seeded errors each fail |
| T-304 | Route map + remote registry (pinned per PRD D-11) | emit | T-301 | 1.5 | Dev | adding a route in YAML produces a registry entry with no code edit |
| T-305 | Deadline plan (ALG-3) emitted from catalogue | emit | T-301 | 1.5 | Dev | sum of per-dependency budgets < request budget, asserted |
| T-306 | Generated `package.json#dependencies` (ROW-10) | emit | T-301 | 1.5 | Dev | a consumer of an undeclared interface is rewritten by the generator |
| T-307 | `turbo.json#boundaries.tags`, merged between markers | emit | T-301 | 1.0 | Dev | regenerating never clobbers hand-written task config |
| T-308 | Per-deployable CI manifests (reusable, pinned) (FR-24) | emit | T-301 | 1.0 | Dev | no workflow duplicates a reusable definition's body |
| T-310 | **`check:generated-fresh`** (CHK-08 — FR-05, FR-10, D1) | config | T-301 | 1.0 | Dev | a hand-edited generated file fails |

**Sequencing note.** T-306 has a wide blast radius: every manifest changes at once. It must land as its own PR with a review from all team leads, because after it merges, *every* undeclared import becomes a diff failure.

**Sequencing note.** T-310 is not optional and was absent from v1.0.0 of this plan. Without it, FR-05 ("the catalogue is the sole topology input") and FR-10 ("markers on generated files") have no enforcement: a hand-edited generated file would be merged silently, and the generator's output would drift from the catalogue. A generated artefact with no drift check is a suggestion.

---

## 5. PH-4 — Scaffolding and platform contracts (2 weeks · 9 pd)

| ID | Task | Artefact | Blocked by | Effort | Role | Acceptance |
|---|---|---|---|---|---|---|
| T-401 | Template: bounded-context API (MOD-7) | `templates/api` | T-209 | 2.5 | Dev | scaffold → `typecheck && lint && check:boundaries` pass, zero manual edits, ≤ 60 s |
| T-402 | Template: client shell | `templates/shell` | T-401 | 2.0 | Dev | as T-401 |
| T-403 | Template: domain UI artefact (federation config from catalogue) | `templates/remote` | T-402 | 1.5 | Dev | produced config equals the hand-written reference config |
| T-404 | Template: aggregator | `templates/bff` | T-401 | 1.5 | Dev | no store dependency in the generated manifest (AC-03) |
| T-405 | `@cms/authz` — claim JSON Schema + evaluator interface, zero policy logic | package | — | 1.0 | Dev | lint proves the package exports no executable policy function |
| T-406 | `@cms/composition` — route/remote/session/chrome types, opaque brands | package | — | 0.5 | Dev | a shell module cannot construct a `RouteSegment` |

---

## 6. PH-5 — Environment, config, cache (2 weeks · 9 pd)

| ID | Task | Artefact | Blocked by | Effort | Role | Acceptance |
|---|---|---|---|---|---|---|
| T-501 | `devenv.nix` / `devenv.yaml` with pinned inputs; committed `devenv.lock` | env | T-102 | 2.0 | DevOps | `devenv up` cold ≤ 300 s, warm ≤ 10 s (RES-03/04) |
| T-502 | **`.envrc` with the pinned `source_url` + sha256 form** (**GAP-08**) | `.envrc` | T-501 | 0.5 | DevOps | `direnv allow` then entering the dir yields the toolchain; no `[whitelist]`; `require_allowed` set |
| T-503 | Declare services/processes/tasks; explicitly declare `git-hooks` input (devenv 2.x removed the default) | `devenv.yaml` | T-501 | 1.0 | DevOps | `devenv up` starts the local stack |
| T-504 | `secretspec.toml` declarations only; migrate off `.env` if one exists | secrets | T-501 | 1.0 | DevOps | no secret value in any tracked file |
| T-505 | Per-deployable `config.schema.ts`, strict parse **before** socket bind | code | T-401…T-404 | 2.0 | Dev | unknown env key → non-zero exit, offending key logged; valid key → binds |
| T-506 | Cache-key hygiene: `outputs`, declared `env`, narrowed `inputs` (FR-25) | `turbo.json` | T-307 | 1.5 | Dev | a declared var busts the cache; an undeclared one does not |
| T-507 | Binary cache wiring for onboarding latency | env | T-501 | 1.0 | DevOps | median onboarding time to first run ≤ 1 working day |

---

## 7. PH-6 — Reference bounded context and aggregator (4 weeks · 29.0 pd) · *the exemplar*

| ID | Task | Artefact | Blocked by | Effort | Role | Acceptance |
|---|---|---|---|---|---|---|
| T-601 | `banner` domain: aggregates, value objects, repository interfaces; **functional core** (TDD D-14) | code | T-401 | 3.0 | Dev | zero imports outside `domain/`; no mocks in domain tests |
| T-602 | `application` use cases + per-use-case ports (ALG-6) | code | T-601 | 2.5 | Dev | every port has ≥ 1 call site and a second implementation |
| T-603 | `adapters/inbound` + `adapters/outbound` + `main.ts` composition root | code | T-602 | 3.0 | Dev | only `main.ts` binds a port to an adapter |
| T-604 | Store + migrations, **expand/contract only** (TDD §20.3) | code + schema | T-603 | 2.0 | Dev | no migration takes a write lock; no destructive migration exists |
| T-605 | `openapi.yaml` (3.1.x pinned, DEC-22) + **published contract digest** (**GAP-10**) | contract | T-604 | 1.0 | Dev + SA | `check:contracts` (CHK-15) fails a consumer gate on an unconsumed contract change |
| T-606 | Consumer-driven contract suite incl. **denial cases** (R-SEC-01) (MOD-9) | tests | T-605 | 1.5 | Dev + QA | `check:contracts` green; an intentional divergence fails |
| T-607 | Shell: bootstrap sequence MOD-3, generated route map, chrome | code | T-402, T-304 | 3.0 | Dev | boots with a fake remote per route (PRD §5.1) |
| T-608 | Federation config builder from catalogue (MOD-5), incl. **GAP-01, GAP-02, GAP-03** fixes | code | T-403, T-304 | 2.0 | Dev | `shareStrategy='loaded-first'`; `disableAssetsAnalyze` absent; `disableShared=false`; `disableSnapshot` prod-only |
| T-609 | Error boundaries + fallback runtime plugin (TDD D-17) | code | T-608 | 1.0 | Dev | one bad remote degrades its region, not the page |
| T-610 | OTel browser instrumentation, single shared tracer (TDD D-19, cross-dep D-3) | code | T-607 | 2.0 | Dev | one click → one trace; remotes are child spans; CORS allow-list present |
| T-611 | Aggregator: pipeline MOD-6 order, deadline plan, per-request loaders | code | T-404, T-305, **T-605** | 3.0 | Dev | no downstream call before attestation; loader per request; `perf:runtime` (CHK-20) p99 < 50 ms |
| T-612 | Aggregator resilience: breaker, bulkhead, timeout, retry budget, cache-aside (PERF-09/10/11) | code | T-611 | 2.0 | Dev | retry rate ≤ 10 %; event-loop lag p99 < 50 ms |
| T-613 | One **`composed`** route exercising ≥ 2 contexts (**R-8**) | code | T-611, **T-610** | 1.5 | Dev + SA | partial responses demonstrably work; the second remote appears in the trace |
| T-614 | **End-user subject forwarding** (TDD D-05, **GAP-05**, ADR-0015) | code | T-611 | 1.5 | Dev + SA | a downstream call carrying a service identity instead of the forwarded subject fails; ADR-0015 accepted |

**Sequencing note.** T-611 is blocked by T-605 because the aggregator is the sole consumer of the `banner` context. Writing it before the contract is published makes the aggregator the second, unauthenticated source of truth about what the context exposes — the exact shape of GAP-05.

**Sequencing note.** T-613 is blocked by T-610 because cross-dep D-3 exists precisely to stop OTel instrumentation being retrofitted across N bundles after the second remote ships. T-613 was on the declared critical path in v1.0.0 while carrying no dependency on the instrumentation it was supposed to justify.

---

## 8. PH-7 — Boundary and shell purity enforcement (2 weeks · 11.5 pd)

| ID | Task | Artefact | Blocked by | Effort | Role | Acceptance |
|---|---|---|---|---|---|---|
| T-701 | Check harness `tools/checks`: shared CLI, exit codes, fixture runner (MOD-10); host T-105/T-108; add **CHK-22 `check:toolchain`**; `turbo boundaries` ≤ 30 s (RES-06, CHK-18) | code | T-104 | 2.5 | Dev | every `check:*` behaves identically and is testable; a check exiting 2 is treated as failure |
| T-702 | `check:boundaries` — Turbo tags + dependency-cruiser, AC-01/AC-02 (**GAP-07** scope fix) | config | T-307, T-306 | 1.5 | Dev | cross-team import fails in **both** tools |
| T-703 | `check:layers` (AC-08, TDD D-14) | config | T-603 | 1.5 | Dev | `domain/` importing `@nestjs/common` fails |
| T-704 | `check:bff-purity` (AC-03, T1, T7) | config | T-611 | 1.0 | Dev | `bff/` importing `pg` fails; branching on a domain value fails |
| T-705 | `check:shell-purity` (AC-05, AC-06, ALG-1, vocabulary lint) | config | T-607 | 2.0 | Dev | a shell module exporting `Banner` fails |
| T-706 | `check:authz-placement` (AC-12, **GAP-11** deny-by-default, **GAP-13** ROW-7) | config | T-604 | 1.5 | Dev | a route with no authz evaluation and no `public: true` fails; a row-7 endpoint reachable without a shell-attested session fails |
| T-707 | `check:lsc` trailer rule | config | T-107 | 0.5 | DevOps | a cross-team PR with one approval is rejected |
| T-708 | Five seeded-violation fixtures, each in the same PR as its check | fixtures | T-702…T-706 | 1.0 | QA | all five fail, then are reverted in the same commit |

---

## 9. PH-8 — Performance and resource enforcement (3 weeks · 12.5 pd)

| ID | Task | Artefact | Blocked by | Effort | Role | Acceptance |
|---|---|---|---|---|---|---|
| T-801 | `perf:budgets` — `size-limit` per route and per remote (PERF-02/03/13, CHK-17) | config | T-608 | 1.5 | Dev | a deliberately oversized route fails; `remoteEntry.js` over 8 KB fails inspection |
| T-802 | **Duplicate-artefact budget** BUD-06 and **remote count** cap (**GAP-09**) | config | T-801 | 1.0 | Dev | aggregate emitted JS per route is measured and reported |
| T-803 | **Shared-duplication detector** BUD-07 (`check:deps-duplicate`, CHK-16) | config | T-608 | 1.5 | Dev | a remote bundling a shared singleton fails |
| T-804 | CSS budget BUD-08 | config | T-801 | 0.5 | Dev | one design-system stylesheet per route, asserted |
| T-805 | Lighthouse / CWV budget in CI (PERF-01) | config | T-607 | 1.5 | Dev | LCP/INP/CLS thresholds fail the build |
| T-806 | Field instrumentation for **remote mount latency** BUD-09 | code | T-610 | 1.5 | Dev | RUM tags every measurement by route and owning remote |
| T-807 | Cache-hit telemetry + affected-based selection (RES-08, `res:telemetry` CHK-21) | CI | T-506 | 1.5 | DevOps | hit ratio ≥ 80 % reported per run on `main` |
| T-808 | Dev-server RSS baseline, 3 data points (**no threshold yet** — RES-07) | report | T-801 | 1.0 | Dev | baseline exists with 3 points; no assertion made |
| T-809 | Container `requests`/`limits`, multi-stage images, size tags (PERF-12, RES-09, RES-10) | manifests | T-308 | 1.5 | DevOps | every container declares limits; cost tags derive from `catalog/` |
| T-810 | Budget enforcement wired to `catalog/budgets.yaml` owners (`check:budgets` CHK-19) | config | T-207, T-802, T-803, T-804 | 1.0 | TL | a threshold change without an ADR fails |

---

## 10. PH-9 — Relocation to the team-scoped topology (3 weeks · 16 pd)

| ID | Task | Artefact | Blocked by | Effort | Role | Acceptance |
|---|---|---|---|---|---|---|
| T-901 | Move each deployable under its owning team directory | tree | T-801, **T-303, T-306** | 4.0 | Dev | no import is rewritten by hand — the generator follows the move |

**Sequencing note.** T-901 is blocked by the generator artefacts, not only by the budgets. Cross-dep D-1 states that the relocation is safe *because* the generator re-emits `CODEOWNERS` (T-303) and dependency manifests (T-306) for the new layout; without them the move becomes a hand-maintained topology and G-04 is lost. The declared blocker in v1.0.0 was T-801 alone, which reaches neither.
| T-902 | Fold duplicate MF hosts into the single shell | config | T-901 | 2.5 | Dev | exactly one MF host in the repository |
| T-903 | Pin every federation remote (D-11) + stable manifest (**GAP-14**) | config | T-902 | 2.0 | Dev | a remote deploys with **no shell rebuild** |
| T-904 | Design system relocated to `teams/platform/ui` | tree | T-901 | 2.0 | Dev | `@cms/ui` still resolves; no team imports it by path |
| T-905 | Delete prohibited directories (`apps/`, `bff/`, `packages/`, `composition/`) | tree | T-901 | 1.5 | Dev | `check:repo-shape` |
| T-906 | Wire `teams/web/bff` into `teams/web/client` end to end | code | T-611, T-901 | 3.0 | Dev | the browser reaches the aggregator and nothing else |
| T-907 | Full re-verification of all `check:*` on the new topology | — | T-902…T-906 | 1.0 | QA | every gate green on the relocated tree |

---

## 11. PH-10 — Documentation and decision records (2 weeks · 8 pd)

| ID | Task | Artefact | Blocked by | Effort | Role | Acceptance |
|---|---|---|---|---|---|---|
| T-1001 | 27 ADRs drafted and cross-checked against `docs/references.md` | `docs/adr/*` | — | 3.0 | SA | every ADR cites ≥ 1 `R-xx`; no ADR cites a rejected URL |
| T-1002 | `docs/getting-started.md` written by someone who did not build the stack | docs | T-907 | 2.0 | TL | a newcomer completes a local run with no clarification |
| T-1003 | Generated `docs/ownership.md` accepted | docs | T-303 | 0.5 | TL | matches the catalogue |
| T-1004 | Reference-catalogue re-verification sweep | `references.md` | — | 1.5 | SA | no URL 404s; vendor claims still marked as vendor claims |
| T-1005 | PRD §12.3 "honest limits" table re-checked | PRD | T-1004 | 0.5 | SA | every claim added since has a measurement behind it |
| T-1006 | Every SPL-01…SPL-05 trigger evaluated and recorded | record | — | 0.5 | SA | written result per trigger, not "none apply" |

---

## 12. Critical path and float

The critical path is **derived from the `blocked by` column**, not asserted. In v1.0.0 of this plan the declared chain contained three edges that were not dependencies of any task (T-303→T-401, T-605→T-611, T-613→T-801), so it described a sequence the schedule did not actually enforce.

```
T-101 → T-201 → T-206 → T-208 → T-209 → T-401 → T-601 → T-602 → T-603 → T-604 → T-605 → T-611 → T-906 → T-907 → T-1002
```

**30.5 pd of the 129.0 pd programme (24 %).**

**The critical path runs through Platform engineering and through the exemplar, not through the web team.** It follows the generator's schema→interface→contract spine into the bounded context and then into the aggregator, which is the only component that consumes what the context publishes. Two consequences:

1. **Platform capacity is the schedule.** Cross-dep R-1 in the programme register is not a generic risk; it is a statement about this chain. The first 7.5 pd of the path are PH-2 metadata work owned by one platform engineer.
2. **T-613 (the `composed` route) is the one task on the path that can be argued away.** It is the only evidence that the aggregator design is sound before the second bounded context exists. Removing it saves 1.5 pd and removes the programme's ability to detect R-8.

**Float.** The longest non-critical branch into T-907 is `… → T-401 → T-402 → T-403 → T-608 → T-801 → T-901 → T-906`, which finishes 3.0 pd earlier than the path — so the aggregator→client wiring (T-906) carries ~3 pd of float, not zero as v1.0.0 claimed. PH-4 and PH-5 carry the remaining float: PH-5's longest chain (`T-101 → T-102 → T-501 → T-507`) is 5.5 pd against a 2-week phase, and PH-4's terminal tasks T-405/T-406 are unblocked. **There is no float before PH-3 or inside PH-6.** A slip in PH-3 or PH-6 moves the programme end date day for day.

**Schedule consequence.** The corrected chain adds 4.0 pd versus v1.0.0 (T-109 +2.0, T-310 +1.0, T-614 +1.5, less T-305 −0.5, T-108 −0.5 and T-701 +0.5): 125.0 → 129.0 pd. PH-6 rises from 27.5 pd (its true v1.0.0 sum, not the 22 pd its header claimed) to 29.0 pd but stays inside its 4 calendar weeks at the staffing in `IMPLEMENTATION-PLAN.md` §2 — the exemplar phase has the most review latency per person-day, so the added engineering days are absorbed. **No calendar week changes.** The PM is notified under IMPLEMENTATION-PLAN §8 ("adding a task inside a phase").

---

## 13. Definition of done per task

A task is done when **all four** hold:

1. its acceptance command exits 0 in CI;
2. if it introduces a check, the check's seeded fixture **fails** in the same PR (R-3);
3. if it changes a budget or a constraint, the change is in `catalog/` and has an ADR;
4. if it changes a contract, the consumer's verification was re-run (not just the provider's tests).

No task is closed by "code reviewed and merged". A green pipeline is the only definition, and PRD FR-28 closes the vacuous-pass hole that makes this enforceable.

---

## 14. Audit record

Version 1.0.0 of this plan was audited against `PRD-CMS-001`, `TDD-CMS-001`, `TEST-CMS-001`, `DEP-CMS-001`, `RACI-CMS-001` and the 27 records in `adr/`. This section is the record of what the audit changed and what it could not change here.

### 14.1 Defects found and corrected in this document

| # | Severity | Defect | Correction |
|---|---|---|---|
| 1 | **High** | PH-6 header claimed 22 pd; its tasks summed to 27.5. PH-1 claimed 8, summed to 6.0. PH-8 claimed 16, summed to 12.5. The three errors cancelled, so the programme total of 125 was accidentally right while three phase headers were wrong. | Headers now state arithmetic sums. Added §14.4 rule making this a standing self-check. |
| 2 | **High** | `check:tools` (T-105) exists in no other document. It is not in TDD §13's CHK-01…CHK-21 inventory, and FR-27 has no enforcement anywhere. | Replaced with `check:toolchain`, assigned as **CHK-22** to be added to TDD §13 by T-701. TDD §13 is SA-owned; the row must land before T-105's acceptance can pass. |
| 3 | **High** | **CHK-08 `check:generated-fresh` had no task.** FR-05 (catalogue is the sole topology input) and FR-10 (generated-file markers) were therefore unenforced — a hand-edited generated file would merge silently. | Added **T-310** (1.0 pd, PH-3). |
| 4 | **High** | **No task pinned anything.** T-108 built the gate; nothing remediated what it reported. PH-1's exit criterion was unreachable by the WBS. | Added **T-109** (2.0 pd, PH-1) and made T-108 a prerequisite of it. |
| 5 | **High** | The declared critical path contained three edges that were not dependencies in any `blocked by` cell (T-303→T-401, T-605→T-611, T-613→T-801). | Path re-derived from the graph; the three dependencies are now expressed as real blockers (T-611←T-605, T-613←T-610, T-901←T-303/T-306). |
| 6 | **High** | **GAP-05 had no task.** Subject forwarding (TDD D-05, ADR-0015) is the condition that stops the aggregator becoming an authz hole — a security defect, assigned to PH-6 by TDD §14, and absent from the WBS. | Added **T-614** (1.5 pd, PH-6) with a negative acceptance. |
| 7 | **Medium** | T-201 placed the schema at `teams/platform/catalog/schema/*`, contradicting PRD §4.3/§8.1, TDD MOD-1, and S7 — and front-running the PH-9 relocation. T-207 simultaneously used root `catalog/budgets.yaml`, so the plan specified two locations. | T-201 corrected to `catalog/schema/*`; rationale recorded in a phase note. |
| 8 | **Medium** | T-901 was blocked only by T-801, which reaches neither T-303 nor T-306, yet the relocation's stated justification is that the generator follows the move (cross-dep D-1). | T-901 now blocked by T-801, T-303, T-306. |
| 9 | **Medium** | Nine gates were invoked under names not in TDD §13: `catalog:validate` (CHK-01 `check:catalog`), `check:ownership`, `check:relations`, `check:config-strict`, `check:contracts`, `check:budgets`, `check:deps-duplicate`, and a bare `size-limit` standing in for `perf:budgets` (CHK-17). Phase exits are measured against CHK, so an unnameable gate is an unverifiable exit. | All acceptances now cite the CHK id and the TDD §13 command name. |
| 10 | **Medium** | GAP-01, GAP-12 and GAP-13 were cited nowhere; GAP-11 was cited in PH-7 although TDD §14 assigns it PH-6; GAP-14 was assigned to PH-9 although TDD §25.1 assigns it PH-6. | GAP-01/02/03 consolidated into T-608; GAP-12 into T-303; GAP-11 and GAP-13 into T-706; GAP-14 into T-903. The PH-6/PH-9 divergence for GAP-14 is left standing and is deliberate — see 14.2. |
| 11 | **Medium** | T-305 in PH-3 mixed a generated artefact (deadline plan) with runtime aggregator adapters, placing aggregator code in the generator phase and inflating PH-3 by 0.5 pd. | T-305 narrowed to the emitted deadline plan (2.0 → 1.5 pd). Adapters were already T-611's. |
| 12 | **Low** | `D-nn` is used with three meanings (TDD design definitions, PRD normative definitions, cross-phase dependencies) and `R-8` is a programme risk presented beside TDD evidence codes. | Added §0.1 namespace table; every citation qualified. |
| 13 | **Low** | Header claimed "ranges are given where variance is genuine"; no range appeared anywhere. T-102's acceptance used an ungrouped `find -name a -o -name b` that also walked `node_modules`. T-810 was blocked by the budget *schema* but not by the gates it wires. | Header corrected; T-102 pruned and folded to `--frozen-lockfile` (RES-02); T-810 now blocked by T-802/803/804. |
| 14 | **Low** | RES-01, RES-02, RES-05, RES-06 and PERF-13 appeared in no acceptance although TDD CHK-18 and CHK-17 are the instruments for them. | Folded into T-102, T-302, T-701 and T-801 acceptances. |

### 14.2 Deliberate deviations, left standing

| Item | Deviation | Why |
|---|---|---|
| GAP-14 placement | TDD §25.1 assigns the stable-remote-manifest work to PH-6; this plan schedules it in T-903 (PH-9). | Correct on the merits: MF-6 contenthash and MF-7 rebuild-free pinning cannot both hold in PH-6, because only one remote exists to pin. Solving it in PH-9 is when a second remote makes the constraint observable. Needs SA confirmation. |
| GAP-02 placement | TDD §14 assigns it PH-8; this plan resolves it inside T-608 (PH-6). | The fix is a federation-config-builder change and lands with the builder. The PH-8 element is the *measurement* (T-801, PERF-03), which is present. |
| FR-27 enforcement | `check:toolchain` is a **new** CHK row, not a rename of an existing one. | TDD §13's inventory has no slot for FR-27. Inventing a check that the SA's inventory does not sanction is how the check inventory rots. SA must add CHK-22 before T-105 can be accepted. |
| BUD-05 | TDD §20.6 cites "BUD-05" which §11.2 never defines (BUD-01…04 do not exist either). | Not schedulable against an undefined threshold. Raised to SA as a TDD defect; no task invented for it. |

### 14.3 Defects outside this document, referred

| Owner | Defect |
|---|---|
| **SA** | TDD §13 CHK-13 row cites "§14 GAP-13" while §14 assigns GAP-11 to ADR-0021 and GAP-13 to ADR-0023. The two tables disagree about which gap `check:authz-placement` closes. T-706 covers both until the TDD is corrected. |
| **SA** | Gate naming: PRD uses `pins:check` and `catalog:verify-ownership`; TDD §13 uses `check:pins` and `check:catalog`; TEST-PLAN lists both spellings. One gate cannot have two commands. |
| **SA** | TDD D-21…D-24 are unnumbered gaps in the D-series; BUD-01…BUD-04 absent and BUD-05 undefined. |
| **SA** | PRD FR-01 is defined twice with different one-line titles (§1.4 and §14). |
| **PM** | `IMPLEMENTATION-PLAN.md` §8 lists "adding a task inside a phase" as TL-approved and PM-informed. This audit added four tasks (T-109, T-310, T-614, plus CHK-22 into T-701) and corrected three phase effort figures. No calendar week moved. |
| **PM** | `IMPLEMENTATION-PLAN.md` §12 float claim ("~1 week, entirely in PH-4/PH-5") is superseded by §12 above. The rest of that document is the PM's to re-baseline. |
| **QA** | TEST-PLAN §4.2 has no instrument row for PERF-13, RES-01 or RES-02, which T-102/T-801 now cover on the engineering side. |

### 14.4 Standing self-check

Before this plan is issued in any version, the TL verifies:

1. every phase header equals the sum of its task efforts;
2. every command named in an acceptance appears in TDD §13 as a CHK row, or is a `catalog:*` generator command;
3. every GAP-01…GAP-14 named in TDD §14 and §25.1 appears in at least one task cell;
4. the critical path is recomputed from the `blocked by` column, not copied from the previous version;
5. no task cites an identifier that is not defined in the document named in its prefix.
