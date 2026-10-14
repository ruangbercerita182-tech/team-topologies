# ADR-0015 — The aggregator forwards the end-user subject and never substitutes a service identity

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-6
- **Closes:** TDD GAP-05 · **Design:** TDD D-05, D-09

## Context
A composed read is `browser → shell → aggregator → context API ×N`. The PRD specifies that the aggregator evaluates no policy, but not **what identity it calls with**. If it authenticates as a service, the bounded context's per-request authorisation (ADR-0009) silently becomes delegated privilege, and the aggregator becomes an authorisation hole with no owner.

## Decision
1. The aggregator forwards the end-user subject, tenant and session reference as **opaque forwarded claims**. It does not read, evaluate or re-issue them.
2. A context receiving a subject it cannot verify **denies** the request. There is no "fall back to service identity".
3. The aggregator accepts only **shell-attested** sessions: a short-lived, opaque session reference bound to the client platform's transport identity. A request without one is refused with `401` **before any downstream call is planned**.
4. Delegated context-to-context calls are not available. If a context needs another context, that is an AC-02 violation and requires the extraction procedure.

## Consequences
- The aggregator is a trusted **transport**, not a trusted tier. It can be wrong or slow without becoming a security hole.
- Row 7's "external consumers prohibited" finally has a runtime control, not only a lint.
- Cross-origin federation telemetry becomes a deliberate data-egress decision: `traceparent` requires explicit CORS allow-listing.

## Alternatives rejected
- **Service identity + coarse permission on behalf of the user** — rejected: it converts a composition tier into an authority.
- **Aggregator asks the shell who the user is** — rejected: it puts the composition tier on the authorisation path, which both this ADR and D-02 exist to prevent.

## References
R-BFF-01, R-BFF-04, R-SEC-01, R-INT-02, R-MFE-25, R-META-27
