# Deployment and Cutover Plan

| Field | Value |
|---|---|
| Document ID | DEP-CMS-001 |
| Version | 1.0.0 |
| Status | Proposed |
| Date | 2026-10-14 |
| Accountable | **DevOps lead**; Technical Lead co-signs application rollout order (RACI-CMS-001 §2) |
| Basis | TDD §23 (deployment architecture), §11 (budget ledger), PRD §12–13 |
| Scope note | PRD NG-04 excludes *provisioning*. This document specifies what is deployed, in what order, against which target, and how it is rolled back. Infrastructure as code lives elsewhere. |

---

## 1. Deployment units

A deployment unit is a catalogue entry, not a repository. Units release independently (PRD B3); one commit may produce many releases.

| Unit | Artefact | Rollout order constraint |
|---|---|---|
| Context service | container image | **after** its contract version is published; **before** any consumer needs a new field |
| Aggregator | container image | after the context services it fans out to are healthy; before any client that needs a new page DTO |
| Shell | static bundle + stable remote manifest | independent; consumers of the manifest (browsers) cache it briefly, so a shell rollout is effectively instant |
| Remote | static bundle + hashed `remoteEntry` | **no** coupling to the shell (TDD D-33) |
| Store schema | forward-only migrations | expand before any writer emits; contract after all readers migrate (§20.3) |

**Rollback asymmetry, stated up front:** shell, remote, aggregator, context image, and config all roll back by pointer change. **A schema cannot.** This asymmetry is the entire reason the migration rules are expand/contract.

## 2. Environments

| Environment | Composition | Data | Purpose | Gate out |
|---|---|---|---|---|
| Local | `devenv up` | synthetic | development | — |
| CI | devenv + workflows | ephemeral | all checks L0–L4, budgets | — |
| Preview | catalogue-derived subset per PR | synthetic | review the actual topology | tests green on the preview |
| Staging | production-shaped, reduced replicas | anonymised production-shaped | load, migration rehearsal, rollback rehearsal | full C2 cycle green |
| Production | full | production | — | — |

**Preview construction rule:** only the deployables the PR touched, plus the transitively required providers, plus **one aggregator**, plus the shell if the shell changed. Derived from the catalogue, not hand-listed — this is where the interface metadata pays for itself a second time.

## 3. Configuration and secrets

| Item | Delivery | Failure behaviour |
|---|---|---|
| Non-secret config | environment, delivered (12-factor) | invalid value → process exits **before** binding a socket (FR-16) |
| Secrets | SecretSpec at start-up, pluggable backend | unresolvable → process exits before binding |
| Remote URLs | runtime manifest, stable path | stale manifest ≤ TTL; hashed assets immutable |
| Federation runtime | served by the shell, short TTL | a remote whose runtime is missing **fails to load** — the shell always provides it (D-15) |

**No secret is ever baked into an image or a generated file.** A generated file that needs a secret is a design error, and `catalog:generate` has no way to obtain one.

## 4. CI/CD pipeline

```
on PR        → L0 schema → L1 static → L2 unit → L3 contract → L4 slice → affected-only
on merge     → L0–L4 uncached → build every affected deployable → publish preview (if web/shell touched)
on release   → build once (immutable, tagged with commit) → L5 composition → L6 budgets → canary → promote
nightly      → L6 telemetry: cache ratio, RSS baseline, container limits, cost allocation
```

Three non-negotiables:

1. **Build once, promote the same artefact.** No environment rebuilds anything. A rebuild is an incident.
2. **The `check:*` gates are non-cached and required.** They are cheap and they are the product.
3. **No pipeline step may pass by selecting zero files** (FR-28). Vacuous green is the failure mode this whole programme is designed against.

## 5. Rollout strategy

| Stage | Population | Observe | Abort if |
|---|---|---|---|
| Preview | PR-scoped | C2 cycle | any gate red |
| Staging | full, reduced | 24 h | migration rehearsal or rollback rehearsal fails |
| Canary | 1 deployable, 5 % traffic | p99 per route class, error rate, event-loop lag | p99 or errors breach the route-class SLO for 10 min |
| Progressive | 25 % → 50 % → 100 % | same, per step | any breach |
| Independent | each deployable's own schedule | — | — |

**The canary is per deployable, not per commit.** A context rollout and a shell rollout can be, and usually are, minutes or weeks apart. That independence is PRD B3 expressed operationally; collapsing it into one big-bang release would defeat DEC-06's reason for existing.

## 6. Cutover — the PH-9 relocation (the one genuinely risky release)

The relocation moves every deployable to a new path and folds duplicate federation hosts into one. It is the only change that can break a working system without changing behaviour.

| Step | Risk | Control | Verification |
|---|---|---|---|
| S1 — land the new layout with generated artefacts, keep both routings | two truths in flight | `CODEOWNERS` still valid; no directory deleted yet | `check:*` green on the new tree |
| S2 — dual-publish shell + remote bundles under both layouts | asset duplication | immutable CDN; cost is temporary and bounded | composed page renders from the new path |
| S3 — point the stable remote manifest at the new assets | a stale manifest pins old assets | short manifest TTL; rollback = re-point | manifest resolution observed in the field |
| S4 — remove the old layout | the point of no return | verified by S1–S3 evidence, not by confidence | `check:repo-shape` |
| S5 — delete the duplicate federation host | two hosts is the bug being fixed | `check:repo-shape` | exactly one host |
| S6 — remove the last floating pins | D-11 becomes real | `check:pins` zero | CI green |

**Rollback:** S1–S3 are revertible by re-pointing the manifest. **S4 is not.** S4 is therefore gated on a written go/no-go with the SA accountable, and S2–S3 must each show a full release cycle green.

## 7. Availability and operations

| Component | Availability class (TDD §18.1) | On failure |
|---|---|---|
| Edge / gateway / IdP | A | cached shell; gateway fails closed |
| Aggregator, context service | B | partial responses; breakers; retry budget |
| One remote | C | region fallback only |

| Operational item | Decision |
|---|---|
| Scaling axis | Aggregator: concurrency/QPS, stateless. Context: domain load. UI: CDN |
| Autoscaling | CPU + in-flight requests, within PERF-12 requests/limits; **throttling, not rejection, is the right-sizing penalty** |
| Multi-region active-active | **not designed here** — no requirement justifies the cost; revisit with the FinOps input |
| Backup / restore | store-level, per context; **rehearsed**, not assumed; RTO/RPO declared per store rather than invented in this document |
| Incident runbook | one per availability class; the C-class runbook is the one that gets used |
| Observability | one tracer across the federation boundary; correlation id forwarded on every hop |

## 8. Post-deployment verification

| Window | Action | Owner |
|---|---|---|
| 0–15 min | synthetic path per route class, including one `composed` and one `direct` | DevOps |
| 0–60 min | p99 per route class, error rate, retry rate, event-loop lag | DevOps |
| 24 h | cache-hit ratio, asset hit ratio, duplicate-dependency count, cost per team | QA |
| 7 d | budget report; any threshold crossed is a defect, not a surprise | QA + budget owner |

## 9. Deployment risks

| ID | Risk | Mitigation |
|---|---|---|
| D-1 | A remote deploys and the shell cannot see it | stable manifest, not a build-time hash (GAP-14) |
| D-2 | Federation runtime missing → every remote fails | shell provides it; asserted at boot (GAP-03) |
| D-3 | Duplicate React silently reintroduced by a version bump | PERF-05 runtime assertion + BUD-07 |
| D-4 | Migration deployed before the writer that needs it | rollout order from `catalog/interfaces/`; expand before contract |
| D-5 | Cache-key hygiene bug makes CI green on stale code | FR-25's regression test: declared var busts, undeclared does not |
| D-6 | Environment drift between preview and production | build once, promote; no per-environment rebuild ever |
| D-7 | Cost attribution lost because tags were added by hand | tags generated from the catalogue (RES-10) |
