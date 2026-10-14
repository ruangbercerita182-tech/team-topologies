# ADR-0003 — Three planes: presentation composition, business domain, response composition

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-2
- **Refines:** PRD D-02, D-03, D-04 · **Design:** TDD §4

## Context
The PRD names four unit kinds. Naming alone does not prevent the three merges that actually occur in practice: a shell that accumulates domain logic; an aggregator that accumulates business rules; and a client-side composition tier with no owner.

## Decision
Arrange the units into **three planes** with a strictly one-way interaction order:
- **A — Presentation composition**: the shell. Owns routes, registry, session bootstrap, chrome, error boundaries.
- **B — Business domain**: bounded-context services and their domain UI artefacts. Owns all rules and all writes.
- **C — Response composition**: the aggregator. Owns fan-out, shaping, deadlines, partials, transport resilience — and no authority.

Plane order is total. A unit straddling two planes fails the architecture.

## Consequences
- Each merge now has a named detection mechanism rather than a code-review opinion.
- The PRD's D-10 (layer rule) is retained for *source trees*; this ADR adds the orthogonal *plane* rule for ownership and deployment boundaries. Layer-correct but plane-wrong is still wrong.

## Alternatives rejected
- **Layers only** — rejected: it permits a `bff/` that imports a repository, because the source tree can look perfectly layered.
- **Single tier (shell + aggregator + domain in one service)** — rejected: that is the monolith PRD DEC-01's evidence base says not to arrive at by accident.

## References
R-DDD-01, R-DDD-03, R-TT-03, R-BFF-01, R-BFF-04, R-CA-02
