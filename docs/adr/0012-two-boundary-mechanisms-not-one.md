# ADR-0012 — Critical constraints are not gated on a single experimental mechanism

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-7
- **Closes:** PRD DEC-14, AC-01, FR-14, RISK-05

## Context
`turbo boundaries` is labelled **Experimental**. Gating a critical architectural constraint on a feature whose semantics may change is an unacceptable single point of failure.

## Decision
Two independent mechanisms police the dependency graph: `turbo boundaries` tags and `dependency-cruiser` (paired with ESLint `no-restricted-imports`, which resolves through the module resolver rather than raw paths, closing the alias-bypass hole of RISK-11).

**Scope correction (GAP-07):** the two mechanisms are not redundant over the same ground. Boundaries operate on the **workspace package graph by tag**; they cannot today express an **npm deny list** or an **intra-package layer rule**. Therefore AC-03 and AC-08 are enforced by `dependency-cruiser` + ESLint alone, and those checks remain mandatory regardless of Turborepo's maturity.

## Consequences
- Seven of twelve ACs have exactly one enforcing mechanism. This is recorded, not hidden, and each of the seven carries a seeded fixture so "single mechanism" never means "unverified".
- Revisit trigger: when R-BND-13 (npm names in allow/deny) ships **and** boundaries is no longer experimental.

## Alternatives rejected
- **Gate on Turborepo boundaries alone** — rejected: single experimental mechanism as a critical gate.
- **Write our own dependency checker** — rejected: dependency-cruiser is maintained, understood, and paired with the resolver-aware ESLint rule.

## References
R-BND-01, R-BND-02, R-BND-04, R-BND-11, R-BND-12, R-BND-13, R-SOLID-10
