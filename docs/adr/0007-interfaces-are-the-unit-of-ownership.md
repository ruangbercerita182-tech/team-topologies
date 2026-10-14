# ADR-0007 — Provider/consumer roles attach to interfaces, and interfaces are first-class metadata

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-2
- **Closes:** PRD D-05, §7.1 · **Design:** TDD §7

## Context
Provider and consumer are properties of **interfaces**, not of teams: one team is frequently both. Declaring them in two places (`contexts.*.provides/consumes` *and* `relations/`) is exactly the "declared twice" failure mode G-04 exists to prevent.

## Decision
An `Interface` is a first-class catalogue kind with provider, consumers, contract artefact, breaking-change policy, deprecation window and availability commitment. `relations/` becomes a **derived index**, never hand-authored — which is also what Backstage's descriptor model requires, since `relations` is read-only and derived.

Package dependency lists are generated from these interface rows (ROW-10).

## Consequences
- A team cannot import an interface it did not declare: the manifest is rewritten and the diff gate fails the PR.
- A provider may change internals freely; a consumer may never patch a provider's source to get a fix.
- Co-ownership must be *declared with an ADR reference*, which converts AC-07 from a social rule into a validation error.

## Alternatives rejected
- **Authoring `relations/` by hand** — rejected: it duplicates `provides`/`consumes` and drifts within one release.
- **Deriving ownership from `spec.owner` or CODEOWNERS** — rejected on Backstage's own advice: ownership is for display and review routing, explicitly not for runtime authorisation.

## References
R-META-09, R-META-26, R-META-27, R-META-28, R-CDC-01, R-CDC-03, R-TT-03
