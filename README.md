# CMS Platform Architecture

This repository is an **engineering-standards repository**, not a CMS. It produces the
architecture, the decision record and the gates that a CMS product organisation would later
build on. Product functionality is an explicit non-goal (`NG-07` in `docs/PRD.md`) and is
deliberately absent.

**There is no application code here yet.** The programme builds it, phase by phase, under
`docs/IMPLEMENTATION-PLAN.md`. What exists today is the standard, the record of the decisions
that produced it, and the gates that keep them honest.

---

## Start here

| Question | Read |
|---|---|
| What must be true, and why was it decided that way? | [`docs/adr/`](docs/adr/README.md) — 29 records: 27 current, 2 retired by ADR-0029 |
| What is the normative architecture standard? | [`docs/PRD.md`](docs/PRD.md) — the only *Approved* artefact |
| How is it designed in detail? | [`docs/TDD.md`](docs/TDD.md) |
| What is the schedule and phase order? | [`docs/IMPLEMENTATION-PLAN.md`](docs/IMPLEMENTATION-PLAN.md) |
| Who owns what, and who decides? | [`docs/RACI.md`](docs/RACI.md) |
| Where did the evidence come from? | [`docs/references.md`](docs/references.md) — 405 fetch-verified references |
| What is open, deferred or referred? | [`docs/REFERRALS-SA.md`](docs/REFERRALS-SA.md) |

[`docs/README.md`](docs/README.md) is the index and explains which document owns which question.

---

## Run the gates

One command runs everything. It is the same command CI runs.

```sh
python3 tools/docs/run_all.py
```

Exit codes: `0` all gates pass · `1` a gate found something to act on · `2` a gate could not
run, which is **not** a pass.

Requires Python 3.9+ (`str.removeprefix` is the newest thing used; all annotations are postponed with `from __future__ import annotations`). No third-party packages — a dependency may never become a reason a
build breaks.

| Gate | Enforces |
|---|---|
| `check:docs` | 10 coherence checks over `docs/` (DOC-01 … DOC-10, DOC-90, DOC-91) — a fact with no single owner goes stale the moment the thing it describes changes ([ADR-0028](docs/adr/0028-one-owner-per-derived-fact.md)) |
| `gen_docs --check` | the ADR index, traceability table and artefact index are generated, not maintained by hand |
| `check:pins` | FR-21 / D-11 — no floating reference in a build-affecting position |
| `check:toolchain` | FR-26 / FR-27 / RES-01 — one package manager, one root lockfile, no nested `.git` |
| `check:plans` | every phase entry and exit criterion is observable, i.e. is a command with an exit code |
| fixtures | 60 cases proving each check can fail, and that correct input produces no finding |

`check:pins` and `check:toolchain` currently report nothing, because the repository has no
package manifests. That is a gate standing before there is anything to catch — not a
satisfied requirement.

### Run one gate, or explain one

```sh
python3 tools/docs/check_docs.py -C docs --fail-on warning
python3 tools/docs/check_docs.py --list-blind-spots   # checks deliberately not shipped, and why
python3 tools/docs/gen_docs.py -C docs                # regenerate the generated blocks
python3 tools/checks/check_pins.py -C . --explain     # why each directory is skipped
python3 tools/checks/check_plans.py -C docs --report-only   # which artefacts are still Proposed
```

---

## How the documentation is kept true

Documentation that rots is worse than none, because it is confidently wrong. Three rules,
recorded in [ADR-0028](docs/adr/0028-one-owner-per-derived-fact.md):

1. **A fact that can be computed from another file has exactly one owner.** Everything else is
   generated from it or checked against it. A number that changes whenever a record is added
   is deleted, not corrected — the correction goes stale faster than the defect.
2. **A check whose verdict depends on parsing English prose is not a check.** It ships as a
   declared blind spot instead, so the coverage it does not provide is visible.
3. **A gate never observed red is not known to work.** Every check lands with a fixture that
   makes it fail.

Concretely: the ADR index and the artefact index are generated; ADR count, gate names and
version cross-references are checked; and `check_docs.py` regenerates tables and diffs them,
so hand-editing a generated block fails CI.

---

## Working on this repository

```sh
pip install pre-commit && pre-commit install    # optional; the same gates run in CI
```

Before opening a pull request:

```sh
python3 tools/docs/run_all.py
```

**Cross-team changes.** `FR-01` makes an LSC the only path to edit another team's directory.
If your change touches a directory you do not own, it needs either that owner's approval or an
`Owners-Override` trailer naming them:

```
Owners-Override: web
```

The trailer goes on the **merge commit** — or the squashed commit, which is the same
message — not on each commit in the branch. §1.4 quotes Chromium's rule that *"the override
is recorded in the merge commit trailer and expires on merge."* A per-commit requirement
would demand knowing the finished change's owner set at every step, which is usually not
knowable yet.

`python3 tools/checks/check_lsc.py -C . --changed <path> …` implements the rule branch
protection cannot express. See [`tools/checks/README.md`](tools/checks/README.md).

### A README is checked too

Every factual claim on this page — the check count, the fixture count, the ADR count, the
reference count, the minimum Python version — was verified against the files rather than
written from memory. Two were wrong on the first draft: this page said "12 coherence checks"
when there are 10, and "28 cases" when the suites run 60. A README that misstates its own
gate count is the exact defect this repository exists to prevent, and it is the first thing a
newcomer would rely on.

---

## Current state

Phase 1 of ten. Four of its tasks are complete (three of them gates) — `check:pins` (T-108), `check:toolchain`
(T-105), `check_lsc` (T-107) and the phase-criterion gate — because the technical plan
sequences the first two as standalone scripts that do not depend on a workspace existing.

The rest of Phase 1, and every phase after it, assumes a workspace that this repository does
not yet have. `docs/REFERRALS-SA.md` §8 states exactly which tasks are done, which are blocked
and why, and which are waiting on a signature that is not the author's to give.