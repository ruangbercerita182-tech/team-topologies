# ADR-0013 — Federation size is bought with `externalRuntime` + `disableSnapshot`, never with `disableShared`

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-6 (config) / PH-8 (budget)
- **Closes:** TDD GAP-01, GAP-02, GAP-03 · **Supersedes nothing** in PRD §11.3, which it corrects

## Context
PRD §11.3 MF-4 enables `disableShared` and MF-5 requires a shared React singleton. Upstream is explicit that `disableShared` "removes shared dependency registration, selection, and loading… use it only when the build has no `shared` configuration", and both the Vite and Rspack surfaces warn when it is combined with a non-empty `shared` block. Setting it in a build that consumes React from the host share scope is not a size optimisation — it removes the mechanism that makes PERF-05 true.

PRD §11.3 also never states `disableSnapshot`, yet the published size table shows the ≤ 8 KB target is reachable **only** with it: `externalRuntime` with `disableSnapshot` off is 8,222 B gzip, over budget.

## Decision
| Flag | Remote | Shell | Reason |
|---|---|---|---|
| `disableShared` | **false** | **false** | singleton guarantee (PERF-05) is not negotiable |
| `disableRemote` | **true** | n/a | a remote provably never consumes another remote |
| `disableSnapshot` | **true in prod**, false in dev | true | required for the budget; costs HMR and TS type sync, which are dev-time concerns |
| `target` | `web` | `web` | part of the same published reduction |
| `externalRuntime` | **true** | n/a | the reduction that actually matters |
| `provideExternalRuntime` | n/a | **true** | legal only because the shell has **no `exposes`** |

The shell therefore becomes the federation **runtime provider**, not only a mount point. "Exactly one instance" applies to the federation runtime exactly as it applies to React, and the shell asserts it at boot.

## Consequences
- `remoteEntry.js` gzip lands at 5,381 B against PERF-03's 8 KB budget, with the singleton intact.
- If the shell ever gains an `exposes`, `provideExternalRuntime` **throws** — a build-time failure we want.
- The optimiser flags are generated from the catalogue with an environment-derived switch, so the dev/prod difference is never hand-set.

## Alternatives rejected
- **Keep `disableShared: true`** — rejected: it directly contradicts PERF-05 and is warned against upstream.
- **Relax PERF-03 to 9 KB** — rejected: it buys 0.6 KB at the cost of the correctness property.

## References
R-MF-21, R-MF-22, R-MF-23, R-MF-24, R-MF-03, R-MF-08
