# ADR-0025 — No asynchronous inter-context integration in v3.0.0

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-6
- **Design:** TDD §19.1 · **Supports:** PRD D-03, §6.1

## Context
It is tempting to add domain events for projections and decoupling. PRD D-03 states a bounded context exposes exactly two artefacts — an API and a UI artefact — and an event stream is a third. Adopting it introduces unresolved ownership: schema registry, delivery semantics, ordering, replay, idempotency, and a new on-call surface, none of which any current requirement justifies.

## Decision
v3.0.0 has **no** asynchronous inter-context integration. All cross-context composition happens inside one aggregator request, in parallel and budgeted (TDD ALG-3).

The cost is stated rather than hidden: a page needing four contexts pays four context round trips within one request. The aggregation layer's job is to make them parallel and budgeted, not to avoid them.

## Consequences
- No schema registry, no delivery guarantees to design, no replay tooling.
- Read amplification is explicit and measurable (PERF-08 makes N+1 a hard failure).
- Cross-context workflows are routed through the §6.3 extraction procedure rather than through events.

## Revisit trigger
The first context-to-context requirement that extraction cannot satisfy — typically a real-time projection. When adopted it is a **new artefact kind in `catalog/interfaces/`**, an ADR, and a named registry owner; it is never a library a team adds.

## Alternatives rejected
- **Event-driven projections now** — rejected: speculative infrastructure with an owner nobody has been assigned.
- **Shared read model** — rejected: violates OD-1 immediately and produces a database nobody can migrate.

## References
R-BFF-23 (Reach-in Reporting, I Was Taught to Share), R-BFF-19, R-DDD-02, R-TT-03
