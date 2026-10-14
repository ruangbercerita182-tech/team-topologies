# ADR-0001 — Repository topology is a derived output, not an architectural input

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-1
- **Closes:** PRD DEC-01, DEC-02 · **Amends:** none

## Context
"Monorepo or poly-repo?" was treated as the architecture question. Four independent lines of evidence show it is a tool-selection question wearing an architecture costume: the Team Topologies corpus contains **zero** repository guidance; Fowler never uses repo topology as an axis; ownership, versioning and deployment are formally separable boundaries; and Bazel itself defines a repository as a directory tree with a boundary marker, with multiple such files coexisting.

## Decision
Fix B1 (ownership), B3 (deployment) and B4 (repository) separately. Repository topology is whatever satisfies all three. The outcome is a **single monorepo**, conditional on SPL-01…SPL-05, with a designed exit rather than an improvised one.

## Consequences
- Ownership is one team ↔ one top-level directory, so ownership resolution is total and order-free (ADR-0002).
- The monorepo is a **bet on organisational capability that must be continuously funded**; SPL-02 makes tooling-budget loss a leading indicator, not a slow slide.
- Repository size, clone time and "CI is slow" are explicitly **not** triggers. Tooling determines the *cost* of a monorepo, not its correctness.

## Alternatives rejected
- **Poly-repo by default** — rejected: Nx names exactly two legitimate reasons (hard perimeter access control, teams sharing no code); we hold neither, and our teams *do* share the design system, composition contracts, generator and authz format.
- **Leave the question open** — rejected: an undecided boundary is decided later by whoever is most tired.

## References
R-MONO-01 … R-MONO-08, R-MONO-10, R-MONO-13, R-MONO-16, R-MONO-20, R-MONO-23, R-MONO-26, R-MONO-34, R-MONO-38 … R-MONO-40
