# ADR-0002 — Top-level directories are team-scoped, not layer-scoped

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-1
- **Closes:** PRD DEC-03, D-12 · **Depends on:** ADR-0001

## Context
The earlier layout used four top-level axes (`apps/`, `bff/`, `teams/`, `platform/`). Three defects follow: one team is fragmented across up to three directories, so "one team, one directory" is false; ownership becomes a longest-prefix-glob precedence problem; and splitting a team's UI from its aggregation tier reintroduces a hand-off that the topology exists to eliminate.

## Decision
**One team owns exactly one top-level directory.** `teams/<slug>/**` is owned by the team whose document declares `metadata.id: <slug>`, and nothing else may claim it. Paths outside `teams/` are owned by the platform team and are enumerated explicitly.

## Consequences
- Ownership resolution needs **no** glob evaluation and **no** precedence rule: the second path segment *is* the answer.
- Locating "the shell" is no longer a directory guess. It is one lookup in `catalog/clients/web.yaml`, generated into an index.
- `apps/`, `bff/`, `packages/` and `composition/` are prohibited directories, and their absence is checked.

## Alternatives rejected
- **Layer-scoped layout** — rejected: it makes ownership a precedence problem and fragments teams.
- **Owners-propagation from Chromium/Gerrit** — rejected as our *mechanism*: it took years to make non-bypassable (R-MONO-38, R-MONO-39). We get the same property structurally instead.

## References
R-MONO-13, R-MONO-38, R-MONO-39, R-TT-03, R-MONO-13 (structure mirrors the organisation)
