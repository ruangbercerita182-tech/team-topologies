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
