<!-- check:docs:allow DOC-04 This record quotes the stale ADR range and gate spellings in order to explain them. Rule 1 below forbids the check from distinguishing "asserts a stale value" from "describes a stale value" by parsing prose, so the opt-out is explicit and lives in this file. -->

# ADR-0028 — Every derived fact has one owner; prose states rules, the model holds values

- **Status:** Accepted · **Date:** 2026-10-14 · **Decider:** Solution Architect · **Gate:** PH-1 (programme-level)
- **Amends:** none · **Closes:** — (decision, not a TDD §14 GAP; §14 records gaps *in the PRD*, and this record concerns the governance set, which §14 does not cover) · **Origin:** mechanical audit of `docs/` against itself, 2026-10-14

## Context

The complaint that motivates this record is usually filed as "documentation goes stale". That diagnosis is wrong for this corpus, and the wrong diagnosis produces the wrong remedy.

Audited mechanically against itself, the document set contains no gradual decay. It contains **facts with no single owner**, duplicated by hand across files:

| Fact | Claimed in | Actual state |
|---|---|---|
| size of the ADR set | `PRD.md` header and `README.md` §3, both naming a twelve-record scope | 0027 records existed at audit |
| the name of one gate | `PRD` named the pinning gate 4× in a form `TDD` §13 does not use | both names were in use |
| a second gate | `PRD` named the ownership gate 3× in a form `TDD` §13 does not use | both names were in use |
| which ADR closes `DEC-10` | `adr/README.md` claims full coverage | `DEC-10` was claimed by no record |

The literal strings are not reproduced here on purpose. A coherence check scans for them, and an ADR that quotes a stale literal in order to explain it would trip that check — which would mean the gate can only be satisfied by deleting the evidence it was built from. Making the check distinguish "asserting a stale value" from "describing a stale value" requires understanding what each sentence is about, which is the capability this record does not grant it.

None of these is a fact that decayed. Each was correct when written and is contradicted by a fact that moved afterwards. `adr/README.md:87` (PR-1) proposes repairing the first by rewriting `0001–0012` as `0001–0026`, which is itself already wrong — the set is `0027`. **A correction authored by hand and not checked becomes stale faster than the original**, because a correction carries the authority of having been made deliberately.

Generating the affected text does not fix this. A generator that emitted both copies would emit both, from a model that is equally wrong in both places, and the output would then *look* authoritative while two documents still contradict each other. The defect is ownership, not duplication of characters.

## Decision

**A fact that can be computed from another file in this repository has exactly one owner. Prose states rules; the model holds values.** Every other mention of that fact is either generated from the owner or mechanically checked against it.

Concretely, every fact is in exactly one of two tiers:

**Tier A — derived.** The value is computable from another file. Examples: the ADR set size and range; the DEC → ADR and GAP → ADR maps; the artefact index (id, version, status, accountable — all four are already declared by each artefact in its own `| Field | Value |` header block); the list of `R-xx` a given record cites.
- The owner is a **field**, not a sentence. `ADR-0001` states `closes: [DEC-01, DEC-02]`, not *"this record closes decisions 01 and 02"* in a prose table.
- Any other document containing that value is **generated or checked**. Never hand-maintained.
- The envelope is the catalog descriptor already adopted for `catalog/`: `kind` / `metadata` / `spec`, with relations expressed as directional pairs (`ownedBy`/`ownerOf`, R-META-09) so that "who owns this" is an edge in a graph rather than a repeated string.

**Tier B — authored.** The value cannot be computed because it encodes a human judgement: why a decision was taken, which alternatives were rejected, what cost was knowingly accepted, what a budget means to the business.
- **Never generated.** Modelling rationale into YAML yields a document that is more greppable and less honest.
- Staleness is handled by **expiry, not generation**: each such value carries a re-verification trigger, as `references.md` and the PRD §12 "honest limits" table already do.

Three rules make this enforceable rather than aspirational:

**1. A check whose verdict depends on parsing English prose is not a check.** `references.md` encodes reference status as prose inside a free-text column rather than as a field, so "no record may cite a REJECTED reference" — a stated rule at `adr/README.md:8` — **cannot currently be enforced**. A substring scan for `REJECTED` over this corpus produced 12 hits, of which 11 were false positives: `R-SOLID-09` is named in `PRD.md:664` and `adr/0011:21` precisely to forbid citing it, and `R-SEC-01` is `VERIFIED` while its row merely mentions the word "REJECTED" in passing. A gate that cannot distinguish those cases would be switched off within a week, and a switched-off gate is worse than no gate because it is counted as coverage. **A check that cannot be made sound is recorded as a declared blind spot, not shipped.**

**2. A gate never observed red is not known to work.** Every check ships in the same change as a fixture that makes it fail, and a clean-corpus fixture asserts that correct input produces no finding. A check whose fixture is deleted fails review. This extends R-3 from product artefacts to the governance set itself.

**3. One gate has one name.** The pinning gate and the ownership gate each carried two names across the PRD and `TDD`; the two spellings were used interchangeably and both appear in phase exit criteria. The `TDD` §13 inventory is now the canonical naming, because it is the set every phase exit is measured against. The PRD has been amended to match. This record does not reproduce either superseded spelling: a normative document that names an alias in order to forbid it propagates the alias, and the coherence gate scans for the string rather than for intent.

## Consequences

- **The document set stops being self-describing and starts being checkable.** Drift moves from "someone forgot" — invisible until someone is misled — to a non-zero exit code, which is the same property the programme already requires of every phase exit.
- **`references.md` must gain a machine-readable status field before DOC-90 can ship.** That is a schema change to an SA-owned artefact and is the one piece of this decision with immediate work attached. Until it lands, the rejected-citation rule remains unenforced, and that is now written down rather than assumed.
- **Prose gets smaller, not bigger.** The traceability tables in `adr/README.md` and the artefact index in `README.md` become generated artefacts. The reasoning behind a decision stays where it is.
- **The catalogue gains a second consumer.** `docs/` joins `CODEOWNERS`, boundaries and budgets as things the generator emits. ADR-0022 already fixed the rule for artefacts the generator writes into another team's directory — tamper-evident, never exempt — and the same rule applies here without re-deciding it.
- **This is not a documentation platform.** There is no schema registry, no template language, and no prose linting. The scope is the closed set of facts this repository already claims to own.
- **An artefact that declares no accountable role cannot satisfy the rule it is governed by.** `PRD.md`, `TDD.md` and `references.md` are each assigned an accountable in `README.md` §2 but declare none themselves, so "one accountable role per artefact" was verifiable only from the index. Tier A applies: the artefact declares it, the index reads it.

## Revisit trigger

Reconsider if any of the following occurs: the `references.md` status field cannot be added without restructuring the catalogue's section layout; the generated artefact index diverges from the header blocks often enough that the index is edited by hand more than it is regenerated; or the fixture suite for the coherence gate is deleted or bypassed. Default if undecided: **keep the split, keep authored rationale in prose**.

## Alternatives rejected

- **Generate every table from a metadata model, including ADR rationale** — rejected: rationale is not computable. A Y-statement captures the shape of a decision (`In the context of …, facing …, we decided for … to achieve …, accepting …`) but the content of `accepting` is the entire reason the record exists. Diátaxis separates reference material, which is canonical and generated, from explanation, which is discursive and authored (R-DOC-01); migrating the second into a schema inverts that distinction rather than applying it.
- **Adopt an existing documentation-as-code tool** — rejected on the evidence. The tools that report the highest numbers detect drift between documentation and *source code*, which is not the failure mode here: this repository has no source code. `remark-validate-links` (R-DOC-02) is the exception and is adopted, because its subject — do links and anchors resolve, offline, in a Git repo — is exactly one of the Tier A checks required. The rest were not evaluated against this corpus and are not cited as support.
- **A single "document linter" that parses prose and reports contradictions** — rejected: this is rule 1 stated as a product. Detecting that two documents disagree requires knowing what each sentence is *about*, which requires the field this decision introduces. It is downstream work, not a shortcut past it.
- **Fix the four known contradictions by hand and revisit later** — rejected: PR-1 is the counter-example. The contradiction was fixed by hand, the fix was wrong, and nothing said so. A fix without a check is a guess with a date on it.
- **Adopt ADR-0027's prerequisite-gating for documents** — rejected: ADR-0027 gates *work*, and works have exit criteria with commands. A document has no exit criterion until this decision defines one, so gating documents on ADR-0027 would be circular.

## References

R-META-07 (catalog descriptor format — the `kind`/`metadata`/`spec` envelope every Tier A owner conforms to), R-META-09 (well-known relations — ownership as a directional edge rather than a repeated string), R-META-19 (life of an entity — coarse validation at ingest, precise validation at processing; the two-tier check), R-META-20 (creating the catalog graph — the catalogue is a cache over files in version control, not a second source of truth, and humans must govern the metadata), R-META-01 and R-META-03 (operator pattern and declarative desired state — the precedent this programme already follows for `catalog/`), R-OWN-01 and R-OWN-02 (CODEOWNERS and protected branches — ownership enforced by a gate rather than by convention), R-OWN-05 (DORA research index — no finding exists for documentation structure; cited to record that this decision rests on mechanism, not on a survey result), R-DOC-01 (Diátaxis — reference is canonical and generated, explanation is authored), R-DOC-02 (remark-validate-links — offline link and anchor validation adopted as a Tier A check)