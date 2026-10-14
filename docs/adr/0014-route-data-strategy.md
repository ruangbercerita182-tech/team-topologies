# ADR-0014 — Every route declares a data strategy; the aggregator participates only where it is needed

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-2
- **Closes:** TDD GAP-04 · **Design:** TDD D-04

## Context
The PRD forbids the shell from calling any bounded-context API and forbids a domain UI artefact from calling an aggregator — but never states **when the aggregator is in the request path at all**. Three designs are compliant: every read direct (aggregator is dead code); every read through the aggregator (every domain DTO is re-serialised into a page DTO); or a mix decided per pull request. The third is the expensive one.

## Decision
Every route declares `dataStrategy`:

| Value | Legal iff | Data path |
|---|---|---|
| `none` | no `context` | shell → aggregator for chrome/session only |
| `direct` | **exactly one** `context` | remote → **its own** context API; aggregator not involved |
| `composed` | **≥ 2** contexts, or an explicit `clientShape` | shell → aggregator → N context APIs; each remote receives its section as props |

Validation rejects `direct` with ≠ 1 context, and `composed` with < 2 contexts and no `clientShape`.

## Consequences
- The aggregator is never speculative. A product with one context has no composed routes and a correspondingly small aggregation tier.
- One vocabulary per data shape: `direct` speaks the context DTO, `composed` speaks the page DTO. A single domain is never re-serialised twice on one request.
- The decision is one reviewable line of YAML rather than a design discussion.
- PH-6 must build **one** `composed` route across two contexts, or the aggregator design is never exercised (programme risk R-8).

## Alternatives rejected
- **Always compose through the aggregator** — rejected: a one-domain page pays a hop and a translation for nothing, and creates two serialisation vocabularies.
- **Leave it to the team** — rejected: that is how a rule becomes a per-PR accident.

## References
R-BFF-01, R-BFF-02, R-BFF-05, R-BFF-13, R-RES-09, R-AGGR-06
