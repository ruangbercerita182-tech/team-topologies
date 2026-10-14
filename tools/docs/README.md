# check_docs

Mechanical coherence gate for the CMS document set. Standard library only —
no dependency may become a reason a build breaks (`adr/README.md`, ADR-0022).

It lives in `tools/docs/`, deliberately **outside** `docs/`, so the gate does
not become part of the corpus it judges.

## Usage

```sh
python3 tools/docs/check_docs.py -C docs --fail-on warning
python3 tools/docs/check_docs.py -C docs --fail-on none --format json > baseline.json
python3 tools/docs/check_docs.py --list-blind-spots
python3 tools/docs/test_check_docs.py
```

| Exit | Meaning |
|---|---|
| 0 | no findings at or above the threshold |
| 1 | findings at or above the threshold |
| 2 | configuration or usage error — never a finding |

Exit 2 is reserved on purpose: a typo in configuration must not be able to
mask real drift behind a green build.

## Checks

| ID | Severity | Asserts |
|---|---|---|
| DOC-01 | error | every cited `R-xx` resolves in `references.md` |
| DOC-02 | error | local markdown link targets exist |
| DOC-03 | warning | link anchors correspond to a real heading |
| DOC-04 | error / warning | ADR range and count claims match the files on disk |
| DOC-05 | warning | every PRD decision is claimed by some ADR |
| DOC-06 | error | every TDD §14 GAP is closed by an ADR |
| DOC-07 | error | a gate does not have two different names |
| DOC-08 | error / warning | the README §2 artefact index agrees with the artefacts' own header blocks |

DOC-08 is the Tier A case: `README.md` §2 is a hand-maintained table of
artefact, id, version, status and accountable, and all five are already
declared by each artefact in its own `| Field | Value |` block. ADR-0028
would generate that table; until then it is at least checked.

## Declared blind spots

`--list-blind-spots` prints checks that are **not** implemented, with the
reason. A blind spot on the record is acceptable; a silently missing check
is not. Both current entries trace to the same unblock: making a fact a
field rather than prose (candidate ADR-0028).

## Adding a check

1. Add the check with a stable `DOC-nn` id and a one-line statement of the
   fact it owns.
2. Add a fixture under `fixtures/drift/` where that check fires, and register
   it in `test_check_docs.py`.
3. Keep `doc00-clean` clean. A new check that fires on a well-formed corpus
   is a false positive, not a discovery.

R-3: a check whose fixture is deleted fails review. TDD §13: a gate never
observed red is not known to work.

## Corpus status

All current findings are SA-owned. None may be fixed by editing a document
outside the document's accountable role (`RACI.md` §2).

| Check | Finding |
|---|---|
| DOC-04 | `PRD.md:12` and `README.md:75` name the ADR set as 0001–0012; 0027 exist |
| DOC-07 | `pins:check` (9×) vs `check:pins`; `catalog:verify-ownership` (5×) vs `check:catalog` |
| DOC-05 | DEC-10 has no ADR, though `adr/README.md:77` claims full coverage |
| DOC-08 | `PRD.md`, `TDD.md` and `references.md` are assigned an accountable in `README.md` §2 but declare none themselves, so the "one accountable role per artefact" rule cannot be verified from the artefact |
| DOC-08 | `DOC-INDEX-CMS-001` is not registered in the artefact index it defines |

Note that `adr/README.md:87` (PR-1) proposes amending `0001–0012` to
`0001–0026`. The set is `0027`. The proposed correction is itself stale.