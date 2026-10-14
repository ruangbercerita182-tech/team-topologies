# ADR-0019 — Budget what the artefact costs, not only what one navigation downloads

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-8
- **Closes:** TDD GAP-09 · **Design:** TDD §11.2

## Context
PRD §12 budgets what a single route *transfers*. Nothing bounds what the *artefacts* cost: total emitted JavaScript across a route's remotes, the count of remotes per route, duplicated CSS, or how long a named remote takes to mount. Those are the metrics CI stores, the CDN serves, and each pipeline rebuilds — and they are where micro-frontend cost actually accumulates.

## Decision
Four budgets are added as metadata in `catalog/budgets.yaml`, each with an owner and a gate:

| ID | Budget | Threshold | Why |
|---|---|---|---|
| BUD-06 | aggregate JS emitted for one route across all remotes | ≤ 2× the route budget, ≤ 3 remotes per route | artefact + build + CDN cost, unmeasured by PERF-02 |
| BUD-07 | shared-module duplication count per route | **0** | a semver mismatch silently bundles a private copy and everything still renders |
| BUD-08 | CSS transferred per route | ≤ 1 design-system stylesheet | federation does not isolate CSS |
| BUD-09 | remote mount p95, measured in the field | ≤ 250 ms after navigation commit | Core Web Vitals do not attribute a regression to a named remote |

## Consequences
- Every budget has a named owner team; a threshold change requires an ADR (no silent re-baselining).
- BUD-07 is the highest-value low-cost check in the programme: it catches the failure mode where nothing is visibly broken.
- Field data must be tagged by route **and** by the remote that owns it, or a slow remote hides inside a route average.

## Alternatives rejected
- **Measure only transferred bytes** — rejected: it is optimised by caching while the artefact cost grows.
- **Set thresholds from published studies** — rejected: no vendor-neutral target exists; RES-07 collects our own three points first.

## References
R-MFE-06, R-MFE-24, R-MFE-26, R-PERF-11, R-PERF-15, R-PERF-19
