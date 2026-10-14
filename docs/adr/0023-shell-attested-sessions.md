# ADR-0023 — "External consumers prohibited" gets a runtime control

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-6
- **Closes:** TDD GAP-13 · **Design:** TDD D-09

## Context
PRD §7.1 row 7 says an aggregator "versions freely; external consumers prohibited", and AC-04 enforces the *code* rule (a client may not use another client's aggregator). A prohibition with no runtime control is a convention, and aggregator endpoints are exactly the kind of thing that acquires a script or a second client.

## Decision
The aggregator accepts only **shell-attested sessions**: a short-lived, opaque session reference bound to the client platform's transport identity, issued by session bootstrap in the shell. A request without a valid attestation is refused with `401` **before the aggregator plans any downstream call**.

The aggregator still authorises nothing about the domain; it validates **transport provenance** only.

## Consequences
- Row 7's prohibition is enforceable at runtime, not merely at build time.
- Refusal before planning means an unauthenticated request costs no downstream traffic — a security property and a cost property in one.
- The attestation is opaque, so it cannot be repurposed as an authority.

## Alternatives rejected
- **Network policy / API gateway allow-list** — rejected: it identifies the client by network position, which is not a client identity.
- **A bespoke API key per client** — rejected: reintroduces shared-secret distribution and rotation cost for no gain.

## References
R-BFF-01, R-BFF-03, R-SEC-01, R-INT-02
