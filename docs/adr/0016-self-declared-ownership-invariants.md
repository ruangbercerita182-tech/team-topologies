# ADR-0016 — Self-declared ownership is safe only because of two invariants

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-2
- **Closes:** TDD GAP-06 · **Design:** TDD §7.2

## Context
ADR-0008 already decided the total resolution rule. This ADR records *why it is safe* to let a team author its own ownership entry, since a team reviewing its own claim is otherwise a circular guarantee.

## Decision
The circularity is broken by structural restriction, not by additional review:
- **O-1** — no `owns` entry may match a path under another team's directory. A team therefore **cannot** grant itself power over anyone else.
- **O-2** — a team's `owns` list is exactly `{ "teams/<slug>/**" }`.

Self-declaration remains legitimate because the set of things one may declare about oneself is exactly one directory, and every cross-team property (the catalogue as a whole, the generator, `CODEOWNERS`) is platform-owned.

## Consequences
- No second, human-maintained ownership map is needed, and none is permitted.
- Adding a team cannot disturb another team's ownership.
- Uncovered root-level files are a hard error, which keeps the cost of adding one at a single YAML line.

## Alternatives rejected
- **Central ownership file reviewed by the SA** — rejected: it becomes a bottleneck exactly where the model was supposed to scale.
- **Directory-name inference only, no `owns` entries** — rejected: root-level files would then have no possible owner.

## References
R-OWN-01 … R-OWN-06, R-MONO-38, R-META-26
