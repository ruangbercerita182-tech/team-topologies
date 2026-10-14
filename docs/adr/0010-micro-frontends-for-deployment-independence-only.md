# ADR-0010 — Micro-frontends are adopted for deployment independence, never for isolation

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-6
- **Closes:** PRD DEC-06, NG-03, §11.1 · **Design:** TDD §10

## Context
"Micro Frontend as the Goal" is a named anti-pattern at 100 % practitioner agreement. Isolation is the most frequently stated justification and is **false** for this mechanism.

## Decision
Adopt Module Federation for exactly one reason: **B3 deployment independence and team autonomy**. Isolation must never appear in a design justification. Build-time integration is explicitly rejected (Fowler recommends "strongly against" it because of lockstep-release pain); runtime via Web Components and iframes are recorded, not adopted.

The costs are budgeted, not waved away: payload, duplication and monitoring complexity are the documented costs and each has a budget (BUD-06…BUD-09).

## Consequences
- Frontend observability is a **precondition**, not a follow-up: OTel browser instrumentation must exist before a second remote does (D-3).
- Style and dependency leakage between remotes is accepted and mitigated by contract and shared singletons, not by isolation.

## Alternatives rejected
- **Build-time integration** — rejected: forces coordinated releases, which is the exact thing the pattern exists to remove.
- **iframe isolation** — rejected: real isolation, unrequested cost.
- **Native composition only (no federation)** — rejected for the browser client platform only; mobile and desktop compose natively because Module Federation is a bundler concern.

## References
R-MFE-01 (Cam Jackson), R-MFE-02 (Michael Geers), R-MFE-03, R-MFE-04, R-MFE-06, R-MFE-12, R-MFE-15
