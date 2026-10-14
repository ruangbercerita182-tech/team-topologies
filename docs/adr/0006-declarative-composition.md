# ADR-0006 — Composition is declarative and generated, never imperatively registered

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-3
- **Closes:** PRD DEC-15, D-07, D-09, G-04 · **Design:** TDD §8

## Context
Imperative registration — a client or context pushing itself into a runtime host object — makes the topology invisible, un-reviewable and non-deterministic. Backstage replaced it with a declarative extension tree; Kubernetes' model is the canonical one: declare desired state, let an imperative reconciler make it true or fail.

## Decision
Composition is expressed as data in `catalog/` and realised by generated code. The generator is a **single pass over one in-memory graph**, re-reading nothing, and satisfies byte-stability rules S1–S7 so that `catalog:generate && git diff --exit-code` is a meaningful gate.

The catalogue is a *checked-in desired-state document*, not a running system of record — an explicit correction carried from R-META-19.

## Consequences
- Generated files carry exactly one first-line marker containing `@generated` and `do not edit` (S5).
- The generator writes files atomically and never rewrites unchanged content, so a no-op regeneration cannot invalidate build caches (S6).
- Validation is total: all violations reported, sorted, never fail-fast; exit 0/1/2 with 2 reserved for "could not judge".

## Alternatives rejected
- **CUE as the schema language** — recorded, not adopted (PRD DEC-24): zod gives static inference into the generator at no extra tool, and CUE↔JSON Schema interop keeps a later adoption additive rather than a migration.
- **Editing generated files by hand** — prohibited with no exclusions; the fix is in the generator, which lives in the Platform team's directory.

## References
R-META-01, R-META-03, R-META-04, R-META-09, R-META-17, R-META-19, R-META-20, R-META-30, R-META-31, R-CFG-03
