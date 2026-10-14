# ADR-0005 — Composition layer and UI business domain are separated by vocabulary and state

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-7
- **Closes:** PRD DEC-08, D-04, §5 · **Design:** TDD §5

## Context
"The shell must not contain domain logic" is a review convention, and conventions decay. The specific failure is a shell holding domain logic: it then deploys rarely *and* changes often, so every domain change becomes a shell release and all teams serialise behind the slowest deployable.

## Decision
The distinction is enforced by three mechanical tests, not by intent:
1. **Vocabulary test** — an identifier exported from `**/client/**` must belong either to the composition vocabulary or to a bounded context's declared ubiquitous language. Any other identifier fails. The vocabulary is total.
2. **State test** — the shell holds no state surviving navigation.
3. **Rule test** — deleting a bounded context changes a shell module's configuration, never its logic.

Opaque branded types (`RouteSegment`, `RemoteHandle`) make the boundary unrepresentable in TypeScript rather than merely discouraged.

## Consequences
- The ubiquitous language already declared in `catalog/contexts/*.yaml` becomes a lint input instead of prose.
- Route guards and hidden controls are documented as **presentation only**, never as security controls.

## Alternatives rejected
- **Web Components / Shadow DOM per remote** — rejected: strongest encapsulation story of the three (R-MFE-12) but incompatible with the shared-singleton requirement that PERF-05 depends on.
- **iframe isolation** — rejected: real isolation, at a cost the product has not asked us to pay.

## References
R-DDD-01 (§1 ubiquitous language), R-MFE-04 (Mega Frontend, Lack of Skeleton), R-MFE-15, R-MFE-16
