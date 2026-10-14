# ADR-0024 — Hashed assets with a stable manifest; the shell never embeds remote content hashes

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-6
- **Closes:** TDD GAP-14 · **Design:** TDD D-33

## Context
PRD MF-6 mandates `[name].[contenthash:8].js` for immutable caching, and MF-7 states remotes must be redirectable **without a rebuild**. As written these are incompatible: a shell that embeds a remote's content hash must be rebuilt on every remote deploy — destroying exactly the deployment independence DEC-06 exists to buy.

## Decision
| Artefact | Naming | Cache |
|---|---|---|
| shell + remote chunks | `[name].[contenthash:8].js` | `immutable`, 1 year |
| `remoteEntry` | content-hashed | `immutable`, 1 year |
| **remote manifest** (name → hashed entry, exposes, shared versions) | **stable path**, `no-store` or seconds-max-age | never immutable |
| federation runtime file | stable path, short TTL | — |

The shell's build embeds remote **contracts** — names, exposed modules, shared versions — and never remote content hashes. At boot it reads the manifest.

`manifest.disableAssetsAnalyze` stays unset, because disabling it disables the preload function entirely (MF-2), and PERF-04's no-speculative-preload rule is enforced by the manifest not listing assets for unvisited routes.

## Consequences
- **A remote can ship with no shell change.** This is the operational expression of DEC-06.
- Cache invalidation is content-addressed on the asset side and time-bounded on the manifest side — the only combination that gives both immutability and independence.
- Rollback of a remote is a manifest re-point, in seconds.

## Alternatives rejected
- **Shell embeds remote hashes** — rejected: a remote deploy would force a shell deploy, serialising every team behind the shell.
- **Unhashed remote entries for "simplicity"** — rejected: it destroys immutable caching for every asset.

## References
R-MF-06, R-MF-07, R-MF-08, R-MF-10, R-MF-16, R-PERF-11, R-RES-21
