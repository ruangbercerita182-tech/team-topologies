#!/usr/bin/env python3
"""check_lsc — T-107 / FR-01 / AC-11. The only cross-team edit path.

FR-01 states the verification in two sentences, and those sentences are this
check's acceptance:

    "a PR touching two teams' directories with no `Owners-Override` trailer is
     rejected by branch protection. A PR carrying the trailer with only one
     approval is rejected."

Ownership is resolved by the single rule in ADR-0008 rather than by parsing a
CODEOWNERS file: every path under `teams/<slug>/` is owned by the team whose
document declares `metadata.id: <slug>`, and paths outside `teams/` are owned by
platform. That is the rule the generated CODEOWNERS implements, so resolving it
here cannot disagree with the file -- there is nothing to disagree with.

Two ways a change can be legal:

  (a) every touched team's approver approved it -- the ordinary path, where each
      owner simply reviews;
  (b) an `Owners-Override` trailer is present, naming a second approver who is
      not the author. This is the Chromium LSC escape hatch the PRD adopts as a
      first-class process, and it exists precisely because a hard boundary turns
      into a bottleneck otherwise.

The trailer expires on merge by construction: it is read from the commit being
checked, so it cannot outlive its change.

Exit codes: 0 clean, 1 rejected, 2 configuration or usage error.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

TRAILER = re.compile(r"^Owners-Override:\s*(?P<value>.+?)\s*$", re.I | re.M)
TRAILER_COMMA = re.compile(r"[,\s]+")
NON_AUTHOR_APPROVER = re.compile(r"^([A-Za-z0-9._\-]+)(?:\s*\(([^)]*)\))?$")

# Paths that are never a team's working area, whatever they are called.
INFRASTRUCTURE = {"catalog", "docs", "tools", ".github", "node_modules"}


@dataclass
class Decision:
    teams: list[str] = field(default_factory=list)
    non_owning: list[str] = field(default_factory=list)
    cross_team: bool = False
    approvers: list[str] = field(default_factory=list)
    author: str | None = None
    trailers: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    @property
    def approved(self) -> bool:
        return bool(self.approvers)


def load_teams(catalog: Path) -> set[str]:
    """Slugs declared in the catalogue, when it exists.

    Absent catalogue is not an error: the rule itself only needs the directory
    name, and a slug is a slug. Reading the catalogue when present means a
    directory that claims to be a team but declares no document is reported.
    """
    teams_dir = catalog / "teams"
    if not teams_dir.is_dir():
        return set()
    out: set[str] = set()
    for f in sorted(teams_dir.glob("*.yaml")) + sorted(teams_dir.glob("*.yml")):
        m = re.search(r"^\s*id:\s*([A-Za-z0-9._\-]+)\s*$", f.read_text(encoding="utf-8"), re.M)
        if m:
            out.add(m.group(1))
    return out


def owner_of(path: str) -> str:
    """ADR-0008: one rule, no precedence, no fallback."""
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    if len(parts) >= 2 and parts[0] == "teams":
        return f"team:{parts[1]}"
    return "team:platform"


def evaluate(paths: list[str], approvers: list[str], author: str | None,
             author_team: str | None, message: str, team_approvals: list[str],
             catalog_slugs: set[str]) -> Decision:
    d = Decision(approvers=list(approvers), author=author)

    touched: dict[str, list[str]] = {}
    for p in paths:
        touched.setdefault(owner_of(p), []).append(p)

    d.teams = sorted(touched)
    d.cross_team = len(d.teams) > 1

    if not d.cross_team:
        d.reasons.append(
            f"single-owner change ({d.teams[0] if d.teams else 'none'}); FR-01 does not apply")
        return d

    missing_docs = sorted(
        t.removeprefix("team:") for t in d.teams
        if t != "team:platform" and t.removeprefix("team:") not in catalog_slugs
    )
    if missing_docs:
        d.reasons.append(
            f"no catalogue document declares: {', '.join(missing_docs)}. A directory that "
            "looks like a team but declares nothing is not one, and ADR-0008 has no fallback, "
            "so the change cannot be classified at all")

    # Chromium, as quoted in PRD section 1.4: the override is recorded "on every
    # non-owning team touched". A change proposed by one team and reviewed by the
    # others overrides nobody, so it needs no trailer -- which is what makes FR-01
    # path (a) reachable instead of decorative.
    if author_team:
        d.non_owning = [t for t in d.teams if t != f"team:{author_team}"]
    else:
        d.non_owning = list(d.teams)

    d.trailers = TRAILER.findall(message or "")
    if not d.non_owning:
        d.reasons.append(
            f"proposed by {author_team}, which owns every touched path; no override needed")
        return d

    # Path (a): every non-owning team approved. An approver login cannot be
    # mapped to a team here, so CI supplies the set from CODEOWNERS review
    # status. Passing it in rather than guessing is the difference between a
    # check and a guess.
    approved_teams = {s.removeprefix("team:") for s in team_approvals}
    awaiting = [tm for tm in d.non_owning if tm.removeprefix("team:") not in approved_teams]

    if not awaiting:
        d.reasons.append(
            f"FR-01 path (a): every non-owning team ({', '.join(d.non_owning)}) approved; "
            "no override is required because nobody is overridden")
        return d

    if not d.trailers:
        d.reasons.append(
            f"touches non-owning {', '.join(awaiting)} with no Owners-Override trailer and "
            f"no recorded approval from {', '.join(tm.removeprefix('team:') for tm in awaiting)}")
        return d

    named: set[str] = set()
    malformed = False
    for t in d.trailers:
        for raw in TRAILER_COMMA.split(t):
            raw = raw.strip()
            if not raw:
                continue
            m = NON_AUTHOR_APPROVER.match(raw)
            if not m:
                malformed = True
                d.reasons.append(f"malformed Owners-Override entry: {raw!r}")
                continue
            role = (m.group(2) or "").strip()
            named.add(role if role else m.group(1))

    for team in d.non_owning:
        if team.removeprefix("team:") not in named and team not in named:
            d.reasons.append(
                f"Owners-Override does not name {team}; section 1.4 requires one entry per "
                "non-owning team touched")

    approver_set = {a.lower() for a in d.approvers}
    if author and approver_set <= {author.lower()}:
        d.reasons.append(
            f"only the author ({author}) approved; AC-11 requires a second, non-author approver")
    if len(approver_set) < 2:
        # Leading token is AC-11 so the blocking classifier matches on a stable
        # string. Matching on the count was the bug: the reason began with a
        # digit and "approval(s); AC-11" never matched it.
        d.reasons.append(
            f"AC-11: {len(approver_set)} approval(s) recorded; a second approver who is "
            "not the author is required")

    return d


# Reasons that block, as opposed to explanations of why the change is legal.
BLOCKING = ("no catalogue", "touches non-owning", "malformed",
            "Owners-Override does not name", "only the author", "AC-11:")


def rejected(d: Decision) -> bool:
    if not d.cross_team:
        return False
    return any(r.startswith(BLOCKING) for r in d.reasons)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="check_lsc")
    ap.add_argument("-C", "--root", default=".", help="repository root")
    ap.add_argument("--changed", metavar="PATH", action="append", default=[],
                    help="changed path (repeatable). Default: the working diff against the merge base")
    ap.add_argument("--approver", action="append", default=[], metavar="LOGIN")
    ap.add_argument("--author", help="PR author login")
    ap.add_argument("--team-approval", action="append", default=[], metavar="SLUG",
                    help="team whose required review is satisfied (repeatable). CI fills this "
                         "from CODEOWNERS review status; an approver login cannot be mapped "
                         "to a team here")
    ap.add_argument("--author-team",
                    help="slug of the team proposing the change. When given, teams it already "
                         "owns need no Owners-Override (PRD section 1.4: the override is "
                         "recorded on every NON-owning team touched)")
    ap.add_argument("--message", help="commit or PR message carrying the trailer; "
                                      "use --message-file to read it from a file")
    ap.add_argument("--message-file", metavar="PATH",
                    help="file holding the commit or PR message (CI writes the commit body here)")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    args = ap.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"check_lsc: root not found: {root}", file=sys.stderr)
        return 2

    paths = list(args.changed)
    if not paths:
        import subprocess
        try:
            res = subprocess.run(["git", "-C", str(root), "diff", "--name-only", "HEAD"],
                                 capture_output=True, text=True, timeout=15, check=False)
        except (OSError, subprocess.SubprocessError):
            print("check_lsc: no --changed given and git is unavailable", file=sys.stderr)
            return 2
        paths = [p for p in res.stdout.splitlines() if p.strip()]

    message = args.message if args.message is not None else ""
    if args.message_file:
        try:
            message = Path(args.message_file).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"check_lsc: cannot read message file: {exc}", file=sys.stderr)
            return 2

    d = evaluate(paths, args.approver, args.author, args.author_team, message,
                 args.team_approval, load_teams(root / "catalog"))

    if args.format == "json":
        print(json.dumps({"changed": paths, "owners": d.teams, "crossTeam": d.cross_team,
                          "approvers": d.approvers, "trailers": d.trailers,
                          "reasons": d.reasons, "rejected": rejected(d)}, indent=2))
    else:
        print(f"check_lsc: {len(paths)} changed path(s)")
        print(f"  owners   : {', '.join(d.teams) or '(none)'}")
        print(f"  cross-team: {d.cross_team}")
        if d.non_owning:
            print(f"  non-owning: {', '.join(d.non_owning)}")
        print(f"  approvers: {', '.join(d.approvers) or '(none)'}")
        print(f"  trailers : {', '.join(d.trailers) or '(none)'}")
        for r in d.reasons:
            print(f"    - {r}")
        if rejected(d):
            print("\n  REJECTED — see PRD FR-01 and AC-11")
        elif d.cross_team:
            print("\n  allowed: the owning team's approval path (FR-01 (a))")

    return 1 if rejected(d) else 0


if __name__ == "__main__":
    sys.exit(main())