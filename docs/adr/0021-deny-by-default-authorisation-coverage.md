# ADR-0021 — Every inbound route must reference an authorisation port or declare itself public

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-6
- **Closes:** TDD GAP-11 · **Refines:** ADR-0009, PRD AC-12

## Context
`spec.authorises: every-request` is a literal in metadata. AC-12 checks that authorisation is not placed in the wrong tier — but it does not check that a *newly added route* evaluates authorisation. A public, unauthenticated route is fully compliant today.

## Decision
`check:authz-placement` is deny-by-default and runs over inbound routes:
- every inbound route must reference an authorisation port, **or**
- declare `public: true`, which requires an ADR stating why.

## Consequences
- The metadata literal becomes a checked property rather than a decoration.
- Adding a public endpoint becomes a deliberate, reviewed act with a paper trail.
- Access decisions remain fail-closed, so an unreachable policy engine denies rather than allows.

## Alternatives rejected
- **Covered by the existing AC-12 rule** — rejected: AC-12 checks placement, not coverage.
- **Code review as the control** — rejected: it is the class of control that decays first and is invisible afterwards.

## References
R-SEC-01, R-MFE-15, R-BFF-01
