# ADR-0022 — Generated files inside another team's directory are tamper-evident, not exempt

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-3
- **Closes:** TDD GAP-12 · **Design:** TDD D-10

## Context
The generator is the Platform team's tool, and it writes into other teams' directories (`teams/web/client/src/generated/…`) and at the repository root (`CODEOWNERS`, `turbo.json`). Unaddressed, that is an undeclared cross-team write — the thing FR-01 exists to govern.

## Decision
Generated artefacts are **tamper-evident, not exempt**:
1. `CODEOWNERS` still assigns the *consuming* team as reviewer. Human review is unchanged.
2. Correctness is guaranteed mechanically: any hand edit diverges from generator output and fails `catalog:generate && git diff --exit-code` in CI, before review matters.
3. `CODEOWNERS` itself is platform-owned, and every ownership change re-evaluates invariants O-1/O-2. The ownership map may be changed only through the ownership map.
4. **No exclusions, no suppressions, no "we edit this one by hand".** If the generator cannot express something, the fix is in the generator — which lives in the Platform team's own directory, so the LSC rule already applies to it.

## Consequences
- Teams keep human review of generated code without owning the tool that produces it.
- There is no legitimate mechanism by which a generated file can be edited, which removes an entire class of argument.

## Alternatives rejected
- **Exempt generated files from CODEOWNERS** — rejected: it removes review of exactly the files most likely to be wrong.
- **Move all generated output to a top-level `generated/` directory** — rejected: it destroys proximity and would violate ADR-0002's one-team-one-directory rule.

## References
R-OWN-02, R-OWN-06, R-META-03, R-MONO-38
