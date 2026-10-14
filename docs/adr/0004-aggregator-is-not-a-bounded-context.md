# ADR-0004 — The aggregator is composition only, with mechanical disqualification tests

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-6
- **Closes:** PRD DEC-09, D-02, §6.2 · **Design:** TDD §6

## Context
A BFF that starts implementing business rules has those rules "tested, maintained, and replicated across BFFs when they change" (R-BFF-01). The failure mode is silent: the rule is tested in the BFF, changes when the domain changes, and is duplicated into a second BFF.

## Decision
`aggregator` is the normative term. An aggregator owns no store, no migration, no business rule, and no state between requests. Disqualification is mechanical: T1 (store/ORM/migration), T6 (domain terms outside generated adapters), **T7 (branching on a domain value — may read and format, may not decide)**, T8 (re-deriving a provider value). The first failing test determines the outcome, so two teams cannot disagree.

## Consequences
- T7 converts PRD's silent T2 into a static check.
- A rule extracted twice is treated as evidence that the **boundary** is wrong, not that the extraction failed (PRD §6.3 step 7).
- The cost of a composition tier is stated rather than waved away: it is a resource cost, which is why PRD DEC-11 keeps GraphQL federation out of v3.

## Alternatives rejected
- **GraphQL federation as the aggregation tier** — recorded, not adopted: the query planner is itself a resource cost (Rust planner; bounded `beam_width`/`fuel`/`timeout` because planner cost explodes with directive density).
- **One shared aggregator for all clients** — rejected: it re-creates the coupling the tier exists to remove, and turns it into the monolith R-BFF-04 warns about.

## References
R-BFF-01, R-BFF-03, R-BFF-04, R-BFF-05, R-BFF-13, R-BFF-19 (Mediator vs Facade), R-AGGR-09, R-AGGR-10
