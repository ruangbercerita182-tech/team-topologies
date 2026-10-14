# ADR-0018 — direnv stays for reviewability, with the activation script pinned by hash

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-5
- **Amends:** PRD DEC-07 and §9's `.envrc` snippet · **Closes:** TDD GAP-08

## Context
Two things changed upstream since the PRD's reference was taken. devenv 2.0 states that "direnv isn't needed anymore with `devenv shell`", providing native shell reloading — so the PRD's citation of "upstream recommends `devenv hook`" is stale. Separately, upstream's canonical `.envrc` snippet pins the activation script by **URL + sha256** via `source_url`, which is not what the PRD shows.

## Decision
1. Keep **direnv**, for a reason that capability did not change: it makes the trust decision a reviewable, per-file-hash authorisation (`direnv allow`) rather than an invisible mutation of the environment. Upstream's own reasoning recommends the native path for *convenience*; our reason is *auditability*, and convenience is not our constraint.
2. Adopt the **pinned `source_url` + sha256** form, not `eval "$(devenv direnvrc)"`. An unpinned download violates D-11 in exactly the position D-11 exists to protect.
3. `[whitelist]` stays prohibited; `require_allowed` stays on.
4. Because devenv 2.x no longer includes `git-hooks` as an implicit input, any hook the programme relies on is declared explicitly in `devenv.yaml`.
5. Re-verify FR-17/FR-18 against devenv 2.x before PH-5 exits.

## Consequences
- A reviewer reads the exact bytes that will run in their shell.
- Upstream direnvrc updates become a visible, reviewable diff rather than a silent behaviour change.
- Revisit trigger: measured onboarding friction exceeding RISK-08's tolerance, **and** only then.

## Alternatives rejected
- **Adopt `devenv shell` native activation** — rejected for auditability, not capability; the trade is documented so it can be revisited with data.
- **Vendor the direnvrc script into the repository** — rejected: a vendored copy silently diverges from the version devenv expects.

## References
R-DIR-01, R-DIR-02, R-DIR-03, R-DV-10, R-DV-15, R-DV-16, R-DV-17, R-DV-08
