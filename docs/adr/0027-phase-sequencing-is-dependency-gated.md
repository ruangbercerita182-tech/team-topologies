# ADR-0027 — Phase sequencing is gated on artefact dependencies, not on phase order

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect (architectural safety) with PM (schedule) · **Gate:** PH-1 (programme-level)
- **Amends:** PRD §18 (see PR-9 in the ADR README) · **Origin:** IMPLEMENTATION-PLAN §3.1, §5 (D-1…D-7), §7

## Context
PRD §18 states: *"Phases are ordered. A phase starts only when the previous phase's exit criterion objectively holds."* Read literally, that serialises all ten phases: ~26 weeks, with PH-7 — the first phase whose output can catch a violation — landing in week 18.

That sequencing has a cost the plan does not price. The programme's premise (PRD §2 NG-07) is that a violation is caught **mechanically and early**. Under strict serialisation the first mechanically-caught violation cannot occur before the reference implementation exists in PH-6 and the boundary checks in PH-7. A generator defect introduced in PH-3 is therefore discovered four phases after it was written, in a phase whose exit criterion depends on the generator having been right.

The overlap proposed in IMPLEMENTATION-PLAN §3.1 is defensible only if "the artefacts are independent" is a checkable statement rather than an assurance. This ADR makes it checkable: the prerequisite edges already exist as D-1…D-7 (§5 of the plan), and the permitted overlap set is enumerated, closed, and small.

## Decision
**A unit of work may start when the exit criteria of its *declared prerequisites* hold — not when the preceding phase completes.** The dependency list in IMPLEMENTATION-PLAN §5 becomes normative; the phase numbering becomes documentation of that graph.

Three rules follow:

**1. PH-1 is a hard serial gate.** No phase starts before PH-1's exit criterion holds (one lockfile, no nested `.git`, no duplicate package names). Workspace truth is the one thing every later phase assumes and cannot independently establish.

**2. The overlap set is closed.** Exactly these four pairs may run concurrently:

| Overlap | Why the artefacts are independent | Cost if serialised |
|---|---|---|
| PH-4 ∥ PH-3 | templates consume the **catalogue**, not the generator's output | +1 week |
| PH-5 ∥ PH-3 / PH-4 | environment work touches `devenv.nix`; it does not read `catalog/` | +1 week |
| PH-7 ∥ PH-6 | checks are static analysis; the reference implementation is merely what they analyse | +1 week |
| PH-10 (drafting) ∥ PH-9 | documentation describes artefacts that exist from PH-3 onward | +1 week |

Anything not in this table is serial by default. **Adding a pair is an amendment to this ADR, not a PM scheduling decision.**

**3. Two exclusions are decisions, not omissions.**
- **PH-9 may not precede PH-3.** The generator emits the new `CODEOWNERS` and the boundary configuration for the new topology (D-1). Relocating first means hand-maintaining both, and G-04 is lost.
- **PH-8 may not precede PH-7.** A budget with no enforcement gate is a wish (PRD §15). Measuring before the gate exists produces numbers nobody is bound by.

## Consequences
- **The programme is ~22 weeks, not ~26.** The saving is real only if the overlapping pairs are genuinely staffed concurrently — SA at 1.0 FTE across PH-3/PH-6/PH-7 is a precondition of this ADR, not an incidental assumption of it.
- **Exit criteria attach to artefacts, not to phases.** A half-completed phase has no gate, so nothing may depend on "PH-4 is 60% done". This sharpens RACI §5 accountability: verification is attributable to a named artefact and a named owner.
- **Review becomes the contended resource, not engineering.** Three pairs are in flight across weeks 5–12, so boundary and ownership reviews arrive in overlapping windows. DORA records approval latency as a throughput factor in its own right (R-OWN-03), which is why each permitted pair above was chosen so its review surface is disjoint from its partner's — different directories, different owners.
- **A slipped prerequisite is now discovered downstream rather than at the gate.** Under serialisation, a late PH-3 stopped the programme where it was late. Under overlap, PH-4's templates can sit waiting on catalogue output with no visible signal. The weekly architecture clinic (IMPLEMENTATION-PLAN §7) therefore re-checks each D-* edge against actual artefact state; it is not a formality.
- **The dependency list is now load-bearing.** A D-* entry that is wrong is a scheduling defect, not a documentation typo. Edits to §5 require this ADR's amendment path.

## Revisit trigger
Revert to serialisation if any of the following occurs: a permitted overlap is found to have a real prerequisite edge not in D-1…D-7; review latency, not engineering, becomes the measured constraint on M1…M9; or the first missed prerequisite exit is discovered downstream rather than at the gate. Default if undecided at any point: **serialise**.

## Alternatives rejected
- **Keep PRD §18 strict serialisation** — rejected: pays ~4 weeks for no architectural safety gain, and delays the first mechanically-caught violation from week ~12 to week 18. The safety argument for strictness is satisfied by rules 1 and 3, which are retained.
- **Parallelise everything the dependency graph permits** — rejected: the dependency graph is not the binding constraint; reviewer attention is. The SRE book names "inappropriate parallelism" as a failure mode (R-RES-10). With 2 web engineers and 1.0 SA at peak, unbounded parallelism moves the queue, not the throughput — and it makes the safety argument unverifiable, because every pair would then need its own justification.
- **Let the PM decide case-by-case at kickoff** — rejected: unrecorded judgement. The next person cannot distinguish a deliberate relaxation from an oversight, and the D-* list would stop being the answer to "why is this running early?".
- **Split the programme into two concurrent tracks (platform ∥ reference implementation)** — rejected: a resourcing decision with a materially different reversal cost, and it collides with D-3 — browser OTel instrumentation must exist before a second remote does, or the retrofit runs across N bundles. It belongs in its own ADR if it is ever proposed.

## References
R-TT-03 (flow-of-change, interaction modes — sequencing follows the dependency direction, not the calendar), R-OWN-03 (DORA: streamlining change approval — approval latency is a throughput factor), R-OWN-04 (DORA four keys — lead time is the metric this decision moves), R-RES-10 (SRE ch. 2 — "inappropriate parallelism"), R-BUILD-01 (incremental, task-graph-scoped work — the build system already treats independent artefact sets as independently verifiable)
