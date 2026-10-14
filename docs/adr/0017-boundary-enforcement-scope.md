# ADR-0017 — The boundary gate matrix: what each mechanism actually covers

- **Status:** Superseded by ADR-0029 · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-7
- **Refines:** ADR-0012 · **Closes:** TDD GAP-07 · **Design:** TDD §13.1

## Context
ADR-0012 mandates two mechanisms. This ADR fixes the **scope** of each, because "two mechanisms" was being read as "two mechanisms over the same ground", which would have implied a redundancy that does not exist.

## Decision
| Layer of the graph | Mechanism | Notes |
|---|---|---|
| Workspace **package** graph | `turbo boundaries` (tags, transitive) **and** dependency-cruiser | genuine double coverage |
| **npm third-party** dependencies | dependency-cruiser + ESLint only | boundaries rules are tag-based; npm deny lists are an open request |
| **Intra-package** layer rules | dependency-cruiser + ESLint only | outside Turborepo's model entirely |

## Consequences
- AC-01, AC-02: double-enforced.
- AC-03, AC-05, AC-06, AC-08: single-enforced, each with a seeded fixture.
- If `turbo boundaries` reaches GA *and* gains npm deny lists, this ADR is revisited and AC-03 may gain a second mechanism — but not before.

## Alternatives rejected
- **Assume boundaries will gain the capability** — rejected: designing for an unshipped feature is how gates become nominal.
- **Write the missing rules into Turborepo config anyway** — rejected: unsupported keys silently do nothing.

## References
R-BND-01, R-BND-04, R-BND-12, R-BND-13
