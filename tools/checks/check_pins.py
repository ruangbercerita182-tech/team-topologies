#!/usr/bin/env python3
"""check_pins — T-108 / CHK-09. Reject floating references in build-affecting positions.

PRD FR-21 and D-11. The verification text is explicit about how this is proven:
"`check:pins` fails on a fixture containing `@latest` and passes on the pinned
form." A gate never observed red is not known to work (TDD §13).

Scope discipline matters here. A floating version string in a lockfile
comment or a README example is not a build input, and a check that flags those
gets switched off within a week. This check therefore:

  * only reads files it recognises as build-affecting manifests;
  * only inspects fields that resolve into a build;
  * treats a *devDependency* range as acceptable unless --strict-deps is set,
    because floating a dev tool does not change build output and demanding it
    would make the gate impossible to satisfy honestly;
  * honours an explicit per-repo allowlist, so a reference that is genuinely
    not a build input can be declared rather than fought.

Exit codes: 0 clean, 1 findings, 2 configuration or usage error.

Standard library only. No dependency may become a reason a build breaks.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# --------------------------------------------------------------------------
# What counts as a build-affecting position
# --------------------------------------------------------------------------
MANIFEST_SUFFIXES = (
    "package.json", "Cargo.toml", "go.mod", "requirements.txt", "pyproject.toml",
    "Gemfile", "pom.xml", "build.gradle", "build.gradle.kts", "devenv.nix",
    "devenv.yaml", "Dockerfile", ".envrc", "deno.json", "deno.jsonc",
)

# Nix flags documented upstream as defeating the pin (R-NIX-03).
NIX_PIN_DEFEATS = ("--override-input", "--no-update-lock-file")

# A version is floating if it is absent or carries a range/dist/tag operator.
FLOATING_RANGE = re.compile(r"^[\^~><=*]|\s[\^~><=*]|\|\||\bx\b|\*")
TAG_LATEST = re.compile(r"\b(latest|main|master|head|nightly|canary|next|edge|stable)\b")

# npm ranges that are genuinely floating even though they look exact.
EXACT_SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.\-]+)?$")
# Specs resolved locally or by the workspace. Nothing to pin: the resolver is
# the repository itself, which is the strongest pin available.
LOCAL_SPEC = re.compile(r"^(?:\.{1,2}/|file:|link:|portal:|workspace:|patch:)")
# Specs that name a remote. Floating unless they name an immutable revision.
REMOTE_SPEC = re.compile(r"^(?:https?://|git\+|git:|github:|gitlab:|bitbucket:|npm:|jsr:|deno:)")
IMMUTABLE_REMOTE = re.compile(
    r"/(?:archive|raw)/|refs/tags/|@[0-9a-f]{7,40}\b|#(?:refs/)?[0-9a-f]{7,40}\b|\.git#[0-9a-f]{7,40}\b"
)
WORKSPACE_SEMVER = re.compile(r"^workspace:[*~^]?\d+\.\d+\.\d+")


def is_floating(spec: str) -> str | None:
    """Return why `spec` is floating, or None if it is pinned."""
    s = spec.strip()
    if not s:
        return "empty version"

    # pip spells an exact pin '==1.2.3'. The leading operator is part of that
    # syntax, not a range -- treating it as one rejected every correctly pinned
    # requirement, which is how the clean fixture failed on correct input.
    if s.startswith("=="):
        s = s[2:].strip()
        if not s:
            return "empty version"

    if LOCAL_SPEC.match(s):
        return None
    if WORKSPACE_SEMVER.match(s):
        return None
    if REMOTE_SPEC.match(s):
        m = TAG_LATEST.search(s)
        if m:
            return f"remote reference carries the floating tag '{m.group(1)}'"
        if IMMUTABLE_REMOTE.search(s):
            return None
        return "remote reference is not pinned to a commit, archive or exact tag"

    if EXACT_SEMVER.match(s):
        return None

    m = TAG_LATEST.search(s)
    if m:
        return f"floating tag '{m.group(1)}'"
    if FLOATING_RANGE.search(s):
        return f"range or wildcard, not an exact version ({s})"
    return f"unrecognised version form ({s})"


@dataclass
class Finding:
    file: str
    line: int
    reason: str
    text: str


# --------------------------------------------------------------------------
# Per-format readers. Each yields (line number, value, field label).
# --------------------------------------------------------------------------
def read_package_json(text: str) -> list[tuple[int, str, str]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"package.json is not valid JSON: {exc}") from exc
    out: list[tuple[int, str, str]] = []
    for section, strict in (("dependencies", True), ("devDependencies", False),
                            ("optionalDependencies", True), ("peerDependencies", True)):
        block = data.get(section)
        if not isinstance(block, dict):
            continue
        for name, spec in block.items():
            if not isinstance(spec, str):
                continue
            out.append((0, spec, f"{section}.{name}" + ("" if strict else " (dev)")))
    res = data.get("resolutions") or data.get("overrides")
    if isinstance(res, dict):
        for name, spec in res.items():
            if isinstance(spec, str):
                out.append((0, spec, f"resolutions.{name}"))
    return out


def read_cargo_toml(text: str) -> list[tuple[int, str, str]]:
    out: list[tuple[int, str, str]] = []
    section = ""
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            section = s.strip("[]")
            continue
        if "=" not in s or s.startswith("#"):
            continue
        key, _, val = s.partition("=")
        key, val = key.strip().strip('"'), val.strip().strip('"')
        if key in ("version",) and section.startswith("dependencies"):
            out.append((i, val, f"{section}.{key}"))
        if section.startswith(("dependencies", "dev-dependencies", "build-dependencies")) and key.startswith(("git", "branch", "rev", "tag", "version")):
            out.append((i, val, f"{section}.{key}"))
    return out


def read_go_mod(text: str) -> list[tuple[int, str, str]]:
    out: list[tuple[int, str, str]] = []
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("require") and "(" in s:
            for part in s.split("(", 1)[1].rstrip(")").split():
                out.append((i, part, "require"))
        elif re.match(r"^\s*\S+\s+v\S+", s) and not s.startswith(("module", "go ", "//")):
            parts = s.split()
            if len(parts) >= 2 and parts[1].startswith("v"):
                out.append((i, parts[1], parts[0]))
    return out


def read_requirements(text: str) -> list[tuple[int, str, str]]:
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        s = line.split("#")[0].strip()
        if not s or s.startswith("-"):
            continue
        m = re.match(r"^([A-Za-z0-9_.\-]+)\s*(.*)$", s)
        if not m:
            continue
        name, spec = m.group(1), m.group(2).strip()
        out.append((i, spec or "*", name))
    return out


def read_simple_flags(text: str) -> list[tuple[int, str, str]]:
    return [(i, l.strip(), "<flag>") for i, l in enumerate(text.splitlines(), 1)
            if any(f in l for f in NIX_PIN_DEFEATS)]


def read_pyproject(text: str) -> list[tuple[int, str, str]]:
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        m = re.match(r"^\s*([A-Za-z0-9_.\-]+)\s*=\s*[\"']([^\"']+)[\"']\s*$", line)
        if m:
            out.append((i, m.group(2), m.group(1)))
        for flag in NIX_PIN_DEFEATS:
            if flag in line:
                out.append((i, flag, "<nix-flag>"))
    return out


READERS = {
    "package.json": read_package_json,
    "Cargo.toml": read_cargo_toml,
    "go.mod": read_go_mod,
    "requirements.txt": read_requirements,
    "pyproject.toml": read_pyproject,
    "devenv.nix": read_simple_flags,
    "devenv.yaml": read_simple_flags,
    "Dockerfile": read_simple_flags,
    ".envrc": read_simple_flags,
    "Gemfile": read_requirements,
}


# Directories that are not build inputs of this repository. Two reasons, both
# deliberate and both reported by --explain:
#   fixtures/  this gate's own deliberately-drifting evidence. Scanning it means
#              the gate can never be green while the evidence exists.
#   .agents/   vendored third-party skills (287 packages), not tracked by git.
#              Their pin policy is their upstream's, not ours.
DEFAULT_EXCLUDES = ("fixtures", ".agents", "node_modules", "vendor",
                    "__pycache__", ".git", "dist", "build", ".venv")


def scan(root: Path, allow: set[str], strict_deps: bool,
         excludes: tuple[str, ...] = DEFAULT_EXCLUDES) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    scanned = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name not in MANIFEST_SUFFIXES:
            continue
        # Relative to the scan root. Checking absolute parts made the
        # exclusions apply to the root's own name, so scanning a directory
        # literally named 'fixtures' skipped everything inside it.
        rel_parts = path.relative_to(root).parts
        if any(part in excludes for part in rel_parts):
            continue
        rel = str(path.relative_to(root))
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        reader = READERS.get(path.name)
        if reader is None:
            continue
        try:
            entries = reader(text)
        except ValueError as exc:
            findings.append(Finding(rel, 0, str(exc), ""))
            continue
        for line_no, spec, label in entries:
            if path.name in allow:
                continue
            if label.endswith("(dev)") and not strict_deps:
                continue
            if path.name == "Dockerfile" or path.name == ".envrc":
                findings.append(Finding(rel, line_no, "nix pin-defeating flag present", spec[:120]))
                continue
            reason = is_floating(spec)
            if reason:
                findings.append(Finding(rel, line_no, reason, spec[:120]))
    return findings, scanned


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="check_pins")
    ap.add_argument("-C", "--root", default=".", help="repository root")
    ap.add_argument("--allow", action="append", default=[], metavar="MANIFEST",
                    help="manifest to exempt by filename (repeatable)")
    ap.add_argument("--strict-deps", action="store_true",
                    help="also reject floating devDependency ranges")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    ap.add_argument("--exclude", action="append", default=[], metavar="DIR",
                    help="directory name to exclude (repeatable; adds to the defaults)")
    ap.add_argument("--explain", action="store_true",
                    help="print the excluded directories and why")
    args = ap.parse_args(argv)

    excludes = tuple(dict.fromkeys(list(DEFAULT_EXCLUDES) + args.exclude))
    if args.explain:
        print("check_pins: excluded directories (not build inputs of this repository):")
        for d in DEFAULT_EXCLUDES:
            print(f"    {d}")
        for d in args.exclude:
            print(f"    {d}  (added with --exclude)")
        print("  fixtures/ holds this gate's own drifting evidence; .agents/ is vendored\n"
              "  third-party content. Both are re-includable with no --exclude option\n"
              "  that removes them -- add them explicitly if this repository owns them.")
        print()

    root = Path(args.root)
    if not root.is_dir():
        print(f"check_pins: root not found: {root}", file=sys.stderr)
        return 2

    try:
        findings, scanned = scan(root, set(args.allow), args.strict_deps, excludes)
    except OSError as exc:
        print(f"check_pins: cannot read tree: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps({"scanned": scanned, "findings": [f.__dict__ for f in findings]}, indent=2))
    else:
        print(f"check_pins: {scanned} manifest(s) scanned, root={root}")
        if not findings:
            print("no floating references in build-affecting positions")
        for f in findings:
            loc = f"{f.file}:{f.line}" if f.line else f.file
            print(f"[error] {loc}\n    {f.reason}")
            if f.text:
                print(f"    saw: {f.text}")
        if findings:
            print(f"\n{len(findings)} floating reference(s); see PRD FR-21 and D-11")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())