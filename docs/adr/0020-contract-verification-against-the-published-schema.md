# ADR-0020 — Consumer verification runs against the provider's published contract

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-6
- **Closes:** TDD GAP-10 · **Refines:** PRD FR-23 · **Design:** TDD INT-05

## Context
PRD FR-23 verifies contracts locally. A consumer's expectations can therefore be green while the provider has already shipped an incompatible change — the test is green against yesterday's world.

## Decision
1. Each provider publishes its resolved OpenAPI document **and a digest** of it.
2. Each consumer's gate runs against the provider's **published** schema, and fails on an unconsumed digest change.
3. Change policy is `expand → change → contract`, with the deprecation window recorded in the interface row. Removal happens only after the window.
4. A consumer may not hand-author a copy of a provider DTO; a check asserts it.
5. Contract suites include **denial** cases, not only success cases.

## Consequences
- A provider cannot ship a breaking change silently, and cannot claim "we never changed the contract".
- The interface row's `breakingChangePolicy` becomes executable rather than documentary.

## Alternatives rejected
- **Local verification only** — rejected: it proves internal consistency, not agreement.
- **A Pact broker in v3** — rejected as separate work (PRD NG-09); the digest mechanism delivers the guarantee without the infrastructure.

## References
R-CDC-01, R-CDC-03, R-CDC-04, R-META-12, R-META-13, R-SEC-01
