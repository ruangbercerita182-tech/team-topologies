# tools/checks — shared check harness

`TIMP-CMS-001` §2 sequences T-108 and T-105 as **standalone scripts**, folded into
this harness later by T-701 without changing their exit codes. This directory is that
harness. Exit codes are already the contract they will keep.

## check_pins — FR-21 / D-11 / CHK-09 (T-108)

Rejects floating references in build-affecting positions: `latest`, `^`/`~`/`>=`
ranges, wildcards, remotes not pinned to a commit or archive, and the two Nix
flags upstream documents as defeating the pin (`--override-input`,
`--no-update-lock-file`, R-NIX-03).

```sh
python3 tools/checks/check_pins.py -C .              # gate
python3 tools/checks/check_pins.py -C . --explain    # why each directory is skipped
python3 tools/checks/check_pins.py -C . --strict-deps  # also reject floating devDeps
python3 tools/checks/test_check_pins.py              # prove it can fail
```

| Exit | Meaning |
|---|---|
| 0 | no floating reference in a build-affecting position |
| 1 | findings |
| 2 | configuration or usage error — never a clean result |

**A floating `devDependency` is tolerated by default.** Floating a lint tool does not
change build output, and a gate that cannot be satisfied honestly gets switched off.
`--strict-deps` opts into the stricter rule for repositories that want it.

**Excluded directories are printed by `--explain`, not hidden.** `fixtures/` holds this
gate's own deliberately-drifting evidence, so scanning it would mean the gate could never
be green while the evidence exists. `.agents/` is vendored third-party content whose pin
policy belongs to its upstream.

**On this repository it currently scans 0 manifests and passes vacuously.** That is the
intended state: the gate stands before there is anything for it to catch. FR-21's own
verification text says the current tree failing is the point — which it will do the moment
a manifest lands.

## check_toolchain — FR-26 / FR-27 / RES-01 (T-105)

One documented package manager, one lockfile at the root, no nested `.git`.

```sh
python3 tools/checks/check_toolchain.py -C .
python3 tools/checks/test_check_pins.py     # covers both checks
```

| Rule | Asserts |
|---|---|
| RES-01 | exactly one lockfile, at the root. A manifest tree with no lockfile is a finding; a repository with no package manifests at all is vacuous, not a violation — "exactly one" has nothing to bite on until manifests exist |
| FR-26 | no nested `.git`. A nested repository is invisible to `CODEOWNERS` and to every review on this one |
| FR-27 | `README.md` names one package manager and it matches `package.json#packageManager`; another manager may appear only on a line marked as a citation, which is the escape hatch FR-27 itself states |

Two bugs here were only visible because the fixtures ran:

- `.git` was in the skip list, so the walk skipped every nested repository
  *before* looking at it. FR-26 could not report anything at all, and passed a tree
  containing nested repositories.
- The repository's own `.git` was reported as a nested one once the first bug was
  fixed.

## check_plans — phase criteria must be observable (PH-1 gate)

```sh
python3 tools/checks/check_plans.py -C docs              # gate: criteria only
python3 tools/checks/check_plans.py -C docs --report-only  # plus acceptance state
python3 tools/checks/check_plans.py -C docs --strict       # acceptance also fails
```

| Rule | Asserts |
|---|---|
| PLANS-01 | a phase entry criterion that asserts a state without a command is a finding. PH-1's was the phrase "plan accepted", which has no exit code and cannot be told from an assumed one |
| PLANS-02 | every entry and exit criterion names a command or a measurable condition |
| PLANS-03 | reports which artefacts are still `Proposed`. **Reported, not gated** — an unapproved plan does not become correct by failing CI every day, and a permanently-red gate gets switched off. `--strict` makes it gate |

**Acceptance is a signature, not a status this tool can set.** PLANS-03 exists so the
blocker stays visible. Marking a plan accepted is its accountable role's act; a check that
did it would be forging a sign-off.

**On this repository it currently fails two rules and passes after fixing them**, because
all three criteria it found were genuine: PH-1's entry criterion, and two exit criteria
written as prose ("contracts green", "PERF-02/03 enforced").

## check_lsc — FR-01 / AC-11 (T-107)

The only cross-team edit path. Two legal routes:

- **(a)** every non-owning team approves. A change proposed by a team that owns
  every path it touches overrides nobody, so it needs no trailer.
- **(b)** an `Owners-Override` trailer naming every non-owning team touched, plus
  a second approver who is not the author (AC-11).

Route (b) is the Chromium LSC mechanism §1.4 quotes.

### Which message carries the trailer

**The merge commit.** §1.4, quoting Chromium: *"The override is recorded in the merge
commit trailer and expires on merge."* On a repository that squashes, that is the single
squashed commit — the same message. It is **not** required on each commit in the branch,
and `check_lsc` never reads the branch's individual commits.

This is not cosmetic. A per-commit requirement would force the author to know, at each
commit, which teams will ultimately be touched — usually unknowable, because the owner set
is a property of the finished change rather than of any single step. Chromium's model is
post-hoc by design: the override is asserted once, on the artefact that carries the whole
change, and expires with it.

CI should pass `--merge-message-file` populated from the **merge** commit
(`git log -1 --pretty=%B` run after merge) or the squashed commit's body. Passing the tip
of a multi-commit branch is passing an ordinary commit, which is not what §1.4 asks for.

**Ownership is resolved by ADR-0008's single rule, not by parsing CODEOWNERS.**
Every path under `teams/<slug>/` is owned by that slug; everything outside `teams/`
is owned by platform. That is the rule the generated `CODEOWNERS` implements, so
there is nothing here that can disagree with the file.

A directory under `teams/` with no catalogue document is **rejected**, not treated
as unowned. ADR-0008 has no fallback, so a change touching it cannot be classified
as cross-team or not — and a check that guessed either way would be a guess.

```sh
python3 tools/checks/check_lsc.py -C . --changed a.ts --changed b.tsx
python3 tools/checks/check_lsc.py -C . --merge-message-file "$(git log -1 --pretty=%B)"
```

`--author-team` and `--team-approval` come from CI. An approver login cannot be
mapped to a team inside the check, so it is passed in rather than guessed.

### The trailer is only worth what git can find

`check_lsc` parses trailers **the way git does**, not the way the word
`Owners-Override:` appears in a message. A trailer followed by prose is body text to
`git interpret-trailers --parse`, which means `git log --format='%(trailers:key=Owners-Override)'`
reports nothing for it. Accepting such a message would grant an override on paper that
**no post-merge audit could find** — the exact property FR-01 exists to provide.

The parser was written by differential testing against git rather than from its
documentation, and the first version disagreed with git on five of ten observed behaviours:
keys may not contain spaces; one line of prose voids the whole block rather than diluting a
ratio; indented continuations fold into the value; the block must follow another paragraph;
and continuation indentation is free-form.

`test_trailers.py` keeps that agreement honest across 16 cases. It **fails** when git is
unavailable rather than skipping — a differential test that quietly stops testing is worse
than no test.

An `Owners-Override` naming a team that does not exist is rejected too. A typo there grants
nothing and hides the override from the audit that is its purpose.
