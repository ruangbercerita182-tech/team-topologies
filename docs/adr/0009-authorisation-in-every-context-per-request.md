# ADR-0009 — Authorisation is enforced in the bounded context, on every request

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-6
- **Closes:** PRD DEC-12, D-06, AC-12 · **Design:** TDD §22

## Context
Module Federation confers **no** browser security boundary: a remote's JavaScript executes with the host page's privileges. Any control that lives in a shell, a remote or client-side route guard is presentation only and is bypassable.

## Decision
Every bounded-context service authorises **every** request, for the requested operation, resource and tenant. Client-side guards are documented as presentation, never as security controls. `@cms/authz` ships the claim **format** and an evaluator interface only — no decision logic, no organisation-specific conditions (FR-20).

## Consequences
- CSP allow-listing remote origins is a **supply-chain** control, not a substitute for server-side authorisation.
- Access decisions are fail-closed and logged (correlation id, subject, operation, resource, outcome).
- A route with no authorisation evaluation and no declared `public: true` fails `check:authz-placement` — closing the decorative-literal hole (GAP-11).

## Alternatives rejected
- **Authorising in the aggregator** — rejected: it is not an authority, and it would put a composition tier on the authorisation path.
- **Trusting the shell's route guards** — rejected: they are trivially bypassed and would create a false sense of safety.

## References
R-MFE-15, R-MFE-16, R-MFE-17, R-SEC-01, R-BFF-01, R-TT-03
