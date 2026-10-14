# ADR-0008 — Ownership resolution is total and safe under self-declaration

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-2
- **Closes:** PRD FR-06, FR-09, D-12 · **Design:** TDD §7.2 (ALG-4, O-1, O-2)

## Context
PRD §7.2 leaves precedence between the `teams/` segment rule and `owns` globs undefined, and nothing forbids a team from declaring ownership of another team's directory. Since a team's own document declares its own ownership, and that document is reviewed by that team, this is the one place where self-declaration could grant dangerous power.

## Decision
Two invariants make self-declaration safe without a second ownership map:
- **O-1** — no team may own a path under another team's directory. A violation is `E-OWN-INTRUSION`.
- **O-2** — a team's `owns` list is exactly `{ "teams/<slug>/**" }`. Nothing more, nothing less.

Outside `teams/`, a path must be matched by exactly one `owns` entry: zero matches is an error, two is an error naming both.

## Consequences
- Every path has exactly one owner, resolved without glob evaluation or precedence.
- The cost of adding a new root-level file is **one line of YAML** — which is the intended ergonomics.
- `CODEOWNERS` itself is platform-owned, and every ownership change re-evaluates O-1/O-2. You may change the ownership map only through the ownership map.

## Alternatives rejected
- **Longest-prefix glob with tie-breaking** — rejected: complexity manufactured purely by the directory layout.
- **A human-maintained ownership file beside the generated one** — rejected: two maps will disagree, and the disagreement is invisible.

## References
R-MONO-38, R-MONO-39, R-OWN-01 … R-OWN-06, R-META-26
