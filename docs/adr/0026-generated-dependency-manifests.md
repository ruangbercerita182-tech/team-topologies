# ADR-0026 — Package dependency lists are generated from the interface ledger

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-3
- **Refines:** ADR-0007 · **Design:** TDD ROW-10, TDD §8.2

## Context
The interface ledger already states, declaratively, which unit consumes which interface. Package manifests state the same fact a second time, by hand. Two statements of one fact drift, and when they do, Turborepo's "imports a package not specified in dependencies" check fires on **legitimate** edges — which trains developers to ignore the check, which removes the very signal it was meant to provide.

## Decision
`package.json#dependencies` / `devDependencies` are **generated from the catalogue's interface rows**. A hand-added dependency is a diff failure under `catalog:generate && git diff --exit-code`.

## Consequences
- A team cannot import an interface it has not declared as a consumer of — the error surfaces as a manifest diff, in review, before it is a runtime or review problem.
- Turborepo's undeclared-dependency diagnostic becomes structurally unreachable, freeing its tag rules to carry the actual architecture.
- The interface ledger stops being documentation and becomes the build graph's source of truth.
- Blast radius: every manifest changes at once, so this lands as its own PR with all team leads reviewing.

## Alternatives rejected
- **Hand-written manifests plus a lint rule** — rejected: a lint rule reports violations after the fact; generation makes them unrepresentable.
- **Workspaces-only, no manifest dependency declarations** — rejected: it breaks hoisting assumptions, tool detection and pruning.

## References
R-META-09, R-META-26, R-BND-12, R-BND-13, R-BUILD-02, R-BUILD-09
