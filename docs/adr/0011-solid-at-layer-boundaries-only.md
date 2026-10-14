<!-- check:docs:allow DOC-90 R-SOLID-09 — marked REJECTED inline, in order to forbid citing it. -->

# ADR-0011 — SOLID is applied at layer boundaries only

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-7
- **Closes:** PRD DEC-16, §10.1 · **Design:** TDD §9

## Context
SOLID is routinely over-applied inside layers, producing ceremony without benefit. The commonly circulated justification — "Solid Considered a Harmful", attributed to Brian Foote — **does not exist** and must never be cited.

## Decision
SOLID binds **only at layer boundaries**. Inside a single layer no SOLID-derived pattern is imposed. Each principle has exactly one enforcement mechanism, and a new abstraction is justified only by a port with a real consumer **and** a second implementation (a test fake counts).

## Consequences
- The guard is grounded in two independently verified positions: Martin's own limitation of the principles, and Big Ball of Mud — the actual Patterns-community objection to integration-heavy architecture.
- Ports are declared by the *consumer*, one capability per interface; a shared "Ports" package is structurally owned by nobody and is therefore prohibited.

## Alternatives rejected
- **Citing a SOLID critic for the over-application guard** — rejected: the cited article is a hallucination.
- **Blanket Clean Architecture across every context** — rejected as speculative (PRD DEC-05, NG-08); `banner` is the exemplar and the templates copy it.

## References
R-SOLID-01 … R-SOLID-08, **R-SOLID-09 (REJECTED — never cite)**, R-SOLID-10, R-CA-01, R-CA-02, R-CA-06
