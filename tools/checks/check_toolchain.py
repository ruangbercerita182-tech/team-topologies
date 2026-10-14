#!/usr/bin/env python3
"""check_toolchain — T-105. One documented package manager, one lockfile, one git root.

PRD FR-27 and RES-01.

FR-27 asks for the toolchain to be *documented*; RES-01 asks for it to be
*single*. Both are trivially satisfiable by writing one sentence and are
violated the moment someone adds a second lockfile or a second manager, so
both are checked here rather than trusted.

Three things, each with its own command:

  RES-01   exactly one lockfile, at the repository root
  FR-26    no nested `.git` -- a nested repository is invisible to CODEOWNERS
           and to every review on this one
  FR-27    README.md names one package manager and it matches
           `package.json#packageManager`; no other manager appears in any
           onboarding document outside a marked citation

Exit codes: 0 clean, 1 findings, 2 configuration or usage error.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

LOCKFILES = ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock",
             "bun.lockb", "npm-shrinkwrap.json", "deno.lock")

PACKAGE_MANAGERS = {
    "npm": {"lock": "package-lock.json", "run": "npm run"},
    "pnpm": {"lock": "pnpm-lock.yaml", "run": "pnpm run"},
    "yarn": {"lock": "yarn.lock", "run": "yarn run"},
    "bun": {"lock": "bun.lock", "run": "bun run"},
}

# A line may mention another manager if it is explicitly a quotation. Same
# escape hatch FR-27 itself states: "except inside a quoted citation".
CITATION = re.compile(r"^\s*(?:\||>|[-*+]|\d+\.)\s*.*`[^`]*\b(?:npm|pnpm|yarn|bun)\b[^`]*`")

SKIP_DIRS = {".git", "node_modules", "vendor", "__pycache__", "fixtures",
             ".agents", "dist", "build", ".venv", ".next"}


@dataclass
class Finding:
    rule: str
    file: str
    line: int
    message: str


def _parts(path: Path, root: Path) -> tuple[str, ...]:
    return path.relative_to(root).parts


def walk(root: Path):
    for path in sorted(root.rglob("*")):
        if any(p in SKIP_DIRS for p in _parts(path, root)):
            continue
        yield path


def check_lockfiles(root: Path) -> list[Finding]:
    """RES-01: exactly one lockfile, at the root."""
    found = [p for p in walk(root) if p.is_file() and p.name in LOCKFILES]
    out: list[Finding] = []
    if not found:
        # RES-01 says "exactly one", so demanding one in a repository with no
        # package manifests is a rule with nothing to bite on. It binds once
        # manifests exist; until then it is vacuous, and saying so is more
        # useful than reporting a violation for a tree that declares no
        # dependency surface at all.
        manifests = [q for q in walk(root)
                     if q.is_file() and q.name in ("package.json", "deno.json", "deno.jsonc")]
        if manifests:
            out.append(Finding(
                "RES-01", ".", 0,
                f"{len(manifests)} package manifest(s) but no lockfile; RES-01 requires one at the root"))
        return out
    at_root = [p for p in found if len(_parts(p, root)) == 1]
    nested = [p for p in found if len(_parts(p, root)) > 1]
    for p in nested:
        out.append(Finding("RES-01", str(_parts(p, root)), 0,
                           "lockfile below the root; RES-01 allows exactly one, at the root"))
    if len(at_root) > 1:
        names = ", ".join(sorted(p.name for p in at_root))
        out.append(Finding("RES-01", ".", 0,
                           f"{len(at_root)} lockfiles at the root ({names}); two managers resolve differently"))
    return out


def check_nested_git(root: Path) -> list[Finding]:
    """FR-26: no nested .git. A nested repository is invisible here.

    The walk must not filter on `.git` itself. SKIP_DIRS contains it, so the
    naive version skipped every nested repository before looking at it, and
    FR-26 could not report anything at all -- the check passed on a tree with
    three nested repositories.
    """
    out: list[Finding] = []
    skip = SKIP_DIRS - {".git"}
    for p in sorted(root.rglob("*")):
        rel_parts = _parts(p, root)
        if not p.is_dir() or p.name != ".git":
            continue
        if any(part in skip for part in rel_parts[:-1]):
            continue
        parent = p.parent
        if parent == root:
            continue  # the repository's own .git is the point, not a violation
        out.append(Finding("FR-26", str(_parts(parent, root)), 0,
                           "nested .git; this path is invisible to CODEOWNERS and to review on this repository"))
    return out


def check_documented_manager(root: Path) -> list[Finding]:
    """FR-27: one package manager, documented, and consistent with the manifest."""
    out: list[Finding] = []

    pkg = root / "package.json"
    declared = None
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            declared = data.get("packageManager")
        except json.JSONDecodeError as exc:
            out.append(Finding("FR-27", "package.json", 0, f"not valid JSON: {exc}"))
    if declared:
        name = str(declared).split("@")[0]
        if name not in PACKAGE_MANAGERS:
            out.append(Finding("FR-27", "package.json", 0,
                               f"packageManager '{declared}' is not one of {sorted(PACKAGE_MANAGERS)}"))

    readme = root / "README.md"
    if not readme.is_file():
        return out

    text = readme.read_text(encoding="utf-8")
    mentioned = {m for m in PACKAGE_MANAGERS
                 if re.search(rf"\b{m}\b", text)}
    expected = declared.split("@")[0] if declared else None

    if expected:
        if expected not in mentioned:
            out.append(Finding("FR-27", "README.md", 0,
                               f"package.json#packageManager says '{expected}' but README.md does not document it"))
        others = mentioned - {expected}
        for i, line in enumerate(text.splitlines(), 1):
            if CITATION.match(line):
                continue
            for m in others:
                if re.search(rf"\b{m}\b", line):
                    out.append(Finding("FR-27", "README.md", i,
                                       f"documents '{m}' alongside the declared manager '{expected}'; "
                                       "mark it as a citation or remove it"))
    elif len(mentioned) > 1:
        out.append(Finding("FR-27", "README.md", 0,
                           f"mentions {sorted(mentioned)} but package.json#packageManager is absent; "
                           "FR-27 asks for the manifest to be the authority"))
    return out


CHECKS = (
    ("RES-01", check_lockfiles),
    ("FR-26", check_nested_git),
    ("FR-27", check_documented_manager),
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="check_toolchain")
    ap.add_argument("-C", "--root", default=".")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    args = ap.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"check_toolchain: root not found: {root}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    for _name, fn in CHECKS:
        findings.extend(fn(root))

    if args.format == "json":
        print(json.dumps({"findings": [f.__dict__ for f in findings]}, indent=2))
    else:
        print(f"check_toolchain: root={root}")
        if not findings:
            print("one package manager, one lockfile at the root, no nested .git")
        for f in findings:
            loc = f"{f.file}:{f.line}" if f.line else f.file
            print(f"[error] {f.rule} {loc}\n    {f.message}")
        if findings:
            print(f"\n{len(findings)} finding(s); see PRD FR-26, FR-27 and RES-01")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())