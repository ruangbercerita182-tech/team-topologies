<!-- check:docs:allow DOC-90 R-SOLID-09, R-MONO-09, R-BUILD-19, R-BUILD-40, R-MFE-21, R-MFE-22, R-MFE-23, R-BE-22, R-BND-11 — named only to state that no citable source exists or that the entry is rejected. Seven of these were inside range expressions in this section until v3.1.0, which was itself a rule-2 violation. -->

# PRD — CMS Platform Architecture

| Field | Value |
|---|---|
| Document ID | PRD-CMS-001 |
| Version | 3.1.0 |
| Status | Approved for implementation |
| Date | 2026-10-14 |
| Accountable | **Solution Architect** (RACI-CMS-001 §2) |
| Scope | Repository architecture, engineering standard, and tooling for a CMS product organisation built on Team Topologies |
| Supersedes | PRD-CMS-001 v2.0.0 |
| Evidence base | `docs/references.md` (REF-CMS-001 v3.1.0) — 405 admissible references, 79 rejected |
| Decision records | `docs/adr/` — the set and its index are generated; see [`adr/README.md`](adr/README.md). No count is asserted here: it changed on every record added, and each change was a chance to be wrong. |

### What changed from v2.0.0, and why

| Change | Reason |
|---|---|
| **§1 replaces the monorepo/multi-repo question entirely.** v2.0.0 asserted DEC-01 (monorepo) with two citations. v3.0.0 shows by full-text evidence that the Team Topologies corpus contains **zero** repository-topology guidance (R-MONO-01 … R-MONO-04), and that the underlying boundaries are formally separable (R-MONO-06, R-MONO-08, R-MONO-10). The decision is now derived, not asserted. |
| **§4 topology is team-scoped, not layer-scoped.** v2.0.0 used `apps/ bff/ teams/ platform/` — four axes, which fragments one team across up to three directories and forces a glob-precedence algorithm (v2.0.0 D-12) to resolve ownership. v3.0.0 gives **one team one top-level directory**, making ownership resolution total and order-free. |
| **§12 and §13 are new and normative.** v2.0.0's nine NFRs covered only tooling latency. v3.0.0 adds 12 performance budgets and 10 resource-efficiency requirements, each with a numeric threshold and a named measurement. |
| **19 factual corrections** carried from the reference catalogue's attribution table (REF-CMS-001, at the version current when v3.0.0 was cut) (e.g. `shareStrategy` options, `turbo boundaries` Experimental, SecretSpec is Cachix, OpenAPI latest is 3.2.1). |
| **SPL-01 … SPL-05 added**: deterministic criteria under which a bounded context *may* leave the repository. v2.0.0 had no exit path from monorepo. |

### Reading convention

Every normative statement carries an identifier. A sentence without one is explanatory context and carries no obligation.

| Prefix | Meaning | Obligation |
|---|---|---|
| `OBS-xx` | Observed condition in the repository as of 2026-10-14 | Informational; not a to-do by itself |
| `D-xx` | Normative definition | Binding; all later requirements use these terms |
| `AC-xx` | Architecture constraint | Binding; a named enforcement mechanism must exist (§15) |
| `FR-xx` | Functional requirement | Binding; the stated verification procedure must be executable |
| `PERF-xx` | Performance requirement | Binding; numeric threshold, named measurement |
| `RES-xx` | Resource-efficiency requirement | Binding; numeric threshold, named measurement |
| `SPL-xx` | Repository split criterion | Binding; a trigger for DEC-01 revision |
| `G-xx` / `NG-xx` | Goal / non-goal | Measured / prohibited |
| `PH-x` | Build phase, ordered | Objective entry and exit criteria |
| `RISK-xx` | Risk | Mitigation and residual assessment |
| `DEC-xx` | Closed decision | Not reopenable without a superseding entry |
| `R-xx` | Reference in `docs/references.md` | Evidence |

There are no open questions. Every question raised during design is closed in §19.

---

## 1. The architecture question

### 1.1 The framing is wrong

The question "monorepo or multi-repo?" is a **tool-selection** question wearing the costume of an architecture question. It has been adopted reflexively because it is binary and easy to argue about. Four independent lines of evidence show it is the wrong axis.

**Line 1 — Team Topologies never made it an architectural force.** The published TT corpus contains no repository guidance at all:

| Corpus artefact | Occurrences of "repo" / "monorepo" | Reference |
|---|---|---|
| *Team Topologies* Part I excerpt (front matter + Ch. 1–2, 3,177 lines) | **0** | R-MONO-01 |
| Independent Service Heuristics checklist (all 10 items) | **0** (one occurrence, in a testimonial) | R-MONO-02 |
| Team Cognitive Load Assessment instrument | **0** | R-MONO-03 |
| Docker fracture-plane case study | **0** | R-MONO-04 |

Team Topologies' own stated replacement axis is explicit: *"Monoliths vs Microservices is missing the point — start with team cognitive load"* (R-MONO-05). Its boundary-finding instrument — the ISH checklist — asks *"would cognitive load be bounded?"* and *"can this act independently of other teams?"*, never *"is this in its own repository?"* (R-MONO-02).

**Line 2 — Martin Fowler does not use repo topology as an axis.** `microservices.html`, `MicroservicePremium.html` and `MonolithFirst.html` each contain **zero** occurrences of "repo". The *Microservice Premium* is paid in **team-level complexity**, not in repository shape (R-MONO-11, R-BFF-12).

**Line 3 — the boundaries are formally separable, and the tooling proves it.**

| Boundary | Question it answers | Mechanism | Independent deployable? |
|---|---|---|---|
| **B1 — Ownership** | *Who must approve this change?* | `CODEOWNERS`, per-directory OWNERS | Yes |
| **B2 — Versioning** | *Who may be at which version, relative to whom?* | package semver, lockfile, registry | Yes |
| **B3 — Deployment** | *What is released independently, and when?* | deployable unit, CI pipeline, release tag | Yes |
| **B4 — Repository** | *What is fetched, versioned as a unit, and access-controlled as a unit?* | Git, package registry, build-tool external fetch | **No — it is a function of B1–B3** |

The decisive technical datum is Bazel: a repository is *"a directory tree with a boundary marker file at its root"*, and **"multiple such files can coexist in a directory"** (R-MONO-08). Repository boundaries are a *dependency-fetch* concern. They are not, and cannot be, a proxy for ownership or deployment. Nx states the deployment half directly: *"A monorepo is not a monolith: each project inside it stays separate and can be built, tested, and deployed on its own"* (R-MONO-06).

Fowler's Feature Toggle is the canonical proof that deploy unit ≠ release unit ≠ codebase unit (R-MONO-10).

**Line 4 — a "hybrid" is a real, first-class answer, not a failure of commitment.** Nx names *Multiple Monorepos* as an option with concrete split criteria, and asserts that *"with modern build tooling, the technical challenges of maintaining a large repository are solvable, so the choice is mostly organizational"* (R-MONO-07). But that organisational choice is a *readiness* question, not a *shape* question: *"Monorepo is great if you're really good, but absolutely terrible if you're not that good"* (R-MONO-26).

### 1.2 What we decide instead

> **DEC-01 — Repository topology is an output, not an input.**

We fix B1 (ownership), B3 (deployment) and B4 (repository) explicitly and separately. B2 (versioning) follows from the package boundary that B1 already fixes. The repository topology is then whatever satisfies all three, evaluated against SPL-01 … SPL-05 (§3.4).

**B1 — Ownership.** One team owns one **top-level directory**. Nothing else in the repository is owned. Ownership resolution is therefore total and order-free: there is no glob-precedence algorithm, no longest-prefix match, and no "no match is an error" edge case, because every path is under exactly one team directory. This is the Chromium model (R-MONO-38): recursive per-directory owners, a change needs positive review from an owner of *each directory touched*.

**B3 — Deployment.** Every deployable unit — a client shell, an aggregator, a bounded-context service, a domain UI artefact — is built, versioned and released independently of every other, and independently of the repository's commit cadence. One commit may produce many releases; one release draws from exactly one commit. Twelve-factor already separated build/release/run in 2011 (R-MONO-35); Nx and Turborepo both ship `apps/*` + `packages/*` first-class for exactly this reason (R-MONO-06, R-BUILD-03).

**B4 — Repository.** A **single monorepo**, with an explicit and gated exit (§3.4, DEC-02).

### 1.3 Why the single repository, given the evidence

The case is stated honestly, including what it costs.

**For.** Microsoft is the strongest datum because it is a **directional decision, not a success report**: their stated strategy was *"the right number of repos based on the character of the code"*, and they then *"back[ed] away from that strategy"*, merging 40+ depots into one (R-MONO-16). Scale is not the constraint: ~3.5M files, ~300 GB, ~4,000 engineers, 1,760 daily lab builds (R-MONO-17), and the scaling problems were solved **with tooling** — clone from 12 hours to minutes, checkout from 2–3 hours to ~30 s (R-MONO-18, R-MONO-19) — not by splitting back. Google's figure is 2B LOC, 35M commits, 86 TB, ~40k commits/workday (R-MONO-14). Polyrepo's structural cost is *named*: building .NET from individual product repos *"requires orchestration infrastructure that is available only to Microsoft"* and destroys reproducibility of the official build in the open (R-MONO-20). Twelve-factor independently reaches the same conclusion: *"Multiple apps sharing the same code is a violation of twelve-factor"* (R-MONO-34).

**Against, stated plainly.** A monorepo is *"a bet on organisational capability you must continuously fund"* — *"monorepos don't maintain themselves… the fraction of budget allocated to maintaining the monorepo, including infrastructure, tools, and people"* (R-MONO-23). Nx names exactly **two** legitimate reasons to prefer polyrepo: hard repository-level access control, or teams sharing no code (R-MONO-07). We hold neither: there is no regulatory perimeter isolation requirement in scope, and by construction the teams *do* share code — the design system, the composition contracts, the generator and the authz format (§7.1) are all shared and all owned by the Platform team.

**The decisive point is B1.** Most monorepo failure is not the repository; it is the absence of ownership enforcement. Chromium needed years, a bespoke Gerrit configuration, and a Large Scale Changes escape hatch before OWNERS became non-bypassable in 2021 (R-MONO-38, R-MONO-39). We get the same property structurally instead: one team, one directory, generated `CODEOWNERS` (§4.3), and a required-reviewers gate. That is exactly what R-MONO-07 calls "the structure of an Nx workspace often reflects the structure of an organization" (R-MONO-13).

**What we explicitly refuse to cite as support.** There is no published, vendor-neutral target for build cache hit ratio (R-BUILD-19); no primary source quantifies Rspack-vs-Vite memory (R-BUILD-40); and the widely-repeated "30–50% of changes cross a project boundary" and "40–80 repositories per team" figures are unsourced folklore (R-MONO-23 note). We do not build this decision on numbers we cannot trace.

### 1.4 The escape hatch, designed in from day one

A monorepo that cannot make cross-cutting changes becomes a bottleneck. We therefore adopt the **Chromium Large Scale Changes** mechanism as a first-class process, not an afterthought (R-MONO-40):

> An **LSC** is a change that necessarily touches directories owned by more than one team. It is proposed as an RFC, requires a second named approver who is not the author, and is merged with a time-boxed `Owners-Override` on every non-owning team touched. The override is recorded in the merge commit trailer and expires on merge.

**FR-01 — LSC is the only way to edit another team's directory.** No exceptions, no "small enough to skip". The `Owners-Override` trailer is what makes an LSC auditable after the fact, which is precisely what the Chromium process does and what a purely advisory escape hatch does not.

This is the single most important structural difference from v2.0.0, which assumed that if boundaries were hard, cross-cutting change would be impossible.

---

## 2. Goals and non-goals

### 2.1 Goals

| ID | Goal | Measurement |
|---|---|---|
| G-01 | Every path in the repository has exactly one owning team, and the assignment is generated, not declared twice | `CODEOWNERS` is 100% generated from `catalog/`; `check:catalog` exits 0. FR-09, FR-11 |
| G-02 | Boundary violations fail the build, via two independent mechanisms | `turbo boundaries` and `dependency-cruiser` each reject a seeded violation. AC-01, FR-14 |
| G-03 | A new bounded context is scaffolded without Platform team intervention | Template output compiles and passes `typecheck`, `lint` and `turbo boundaries` with zero manual edits, in ≤ 60 s. FR-12, RES-05 |
| G-04 | Repository topology is derived from metadata, never hand-maintained in two places | `catalog:generate && git diff --exit-code` is clean. FR-05, FR-10 |
| G-05 | Build output is reproducible from the commit alone | No floating reference in any build-affecting position; `check:pins` exits 0. FR-21, D-11 |
| G-06 | Configuration is validated before the process serves traffic | Every deployable exits non-zero on invalid configuration, before binding a socket. FR-16 |
| G-07 | The paved road reduces cognitive load measurably | Warm environment activation ≤ 10 s; cold ≤ 300 s. RES-03 |
| G-08 | The browser payload of any route stays inside a stated budget | PERF-02 … PERF-05 enforced in CI |
| G-09 | Aggregator latency is bounded by construction | Per-dependency timeout budgets sum below the request budget; p99 SLO declared per route class. PERF-06, PERF-08 |
| G-10 | Build compute is bounded by cache, not by repository size | Affected-based CI; task cache hit ratio ≥ 80 % on `main`. RES-06 |

### 2.2 Non-goals for v3.0.0

| ID | Excluded | Reason |
|---|---|---|
| NG-01 | Operating a deployed Backstage instance | v3.0.0 produces Backstage-compatible descriptors and a local runner. Operating a portal is a separate initiative with separate ownership (same reasoning as v2.0.0 NG-01, unchanged) |
| NG-02 | Implementing `bff/mobile` and `bff/desktop` | They are declared in the catalog but not implemented. FR-13 defines the declaration; making it a one-file change is the whole point of metadata-driven composition |
| NG-03 | Micro-frontending adopted as an end | "Micro Frontend as the Goal" is a named, empirically-validated anti-pattern at 100 % practitioner agreement (R-MFE-04). Micro-frontends in this architecture exist to satisfy B3 for domain UI artefacts, and nowhere else |
| NG-04 | Infrastructure provisioning (Kubernetes, Terraform, cloud accounts) | The catalog describes deployables; it does not create them. §13 budgets *against* the runtime without provisioning it |
| NG-05 | CI/CD pipeline execution infrastructure | v3.0.0 produces reusable workflow definitions and metadata (FR-24) |
| NG-06 | Identity provider selection | FR-20 defines the claim **format** consumed by bounded contexts, not the provider |
| NG-07 | Content modelling DSL, schema editor, editor UX | Domain product functionality |
| NG-08 | Clean Architecture beyond the reference bounded context | FR-22 scopes it to `banner` as an exemplar. Blanket adoption is speculative (DEC-16) |
| NG-09 | Pact broker deployment | Contracts are produced and verified locally (FR-23). Broker deployment is separate |
| NG-10 | Multi-repo extraction | Reversible, and governed by SPL-01 … SPL-05 rather than pre-optimised (DEC-02) |
| NG-11 | Replacing the JavaScript toolchain | Bun, Turborepo, Rsbuild and NestJS stay. FR-15 makes the choice *singular and documented*, not *different* (v2.0.0 NG-10, unchanged in intent) |

---

## 3. Normative definitions

These definitions are binding. Every later requirement is expressed in these terms.

### D-01 — Client platform

A **client platform** is a deployable product surface consumed by end users through **one specific runtime**: browser, mobile device, or desktop device. A client platform owns its own aggregation tier.

A client platform is **not** a persona, role, tenant, theme, or feature. Organising any axis by persona is prohibited.

> Basis: one aggregation tier per client type — "Enforce the boundary: one BFF per client type" (R-BFFD-01). The aggregation tier exists because different clients have different conventions and payload needs; a shared tier re-creates the coupling it was introduced to remove. Microsoft's guidance is also explicit that a *complex* gateway "risks becoming a bottleneck and eventually a monolith itself" (R-BFF-04).

### D-02 — Aggregator (BFF)

An **aggregator** is a stateless backend service that composes responses from one or more bounded-context services for **exactly one** client platform.

- An aggregator **must not** own a database, execute a migration, or evaluate a business rule.
- An aggregator **must not** be consumed by a client platform other than the one it is declared for.
- An aggregator **may** evaluate no policy at all; all authorisation is delegated upward (D-06).

The complete test set distinguishing an aggregator from a bounded context is normative and appears in §6.3.

> Basis: "A BFF should aggregate and transform. If it starts implementing business rules … those rules need to be tested, maintained, and replicated across BFFs when they change" (R-BFF-01, R-BFFD-03). Gateway duties that are not domain-specific — rate limiting, TLS termination, offloading — stay in the gateway (R-BFF-05, R-BFF-06).

### D-03 — Bounded context

A **bounded context** is a business domain slice with a single owning team, owning its own data store and every business rule within it (R-DDD-01 §2, R-DDD-03).

A bounded context exposes exactly **two** kinds of artefact:

- an **API** (HTTP contract) consumed by aggregators;
- a **UI artefact** — a web micro-frontend remote and/or a native screen bundle — consumed by client platforms.

A bounded context authorises every request for its own resources, regardless of which client initiated it (D-06).

A bounded context is **not** required to correspond one-to-one to a service (R-DDD-01, R-TT-16). The requirement is: one team, one store, one set of rules.

> Basis: "Stream-aligned teams own an entire slice of the business domain end to end" (R-TT-03). The ISH checklist's Dependencies heuristic — "can this act independently of other teams?" — is the operative test, not "is this deployable separately?" (R-MONO-02).

### D-04 — Application composition layer

The composition layer comprises exactly two roles. Conflating them is prohibited. §5 is the normative expansion.

| Role | Definition | Location | Mechanism |
|---|---|---|---|
| **Shell** | The single bootstrap artefact of a client platform. Owns the route map, the remote registry, session bootstrap, layout and chrome, per-remote error boundaries. Holds no business state and no business rule. | `teams/<client>/client/` | Module Federation (web only) |
| **Shared composition contracts** | A dependency providing the federation protocol types, chrome primitives and route primitives consumed by both shells and domain UI artefacts. A package, not a layer; it owns no runtime state. | `teams/platform/composition/` | n/a |

Only the browser client platform implements a shell. Mobile and desktop compose natively; Module Federation is a bundler concern and is not applied to them.

### D-05 — Provider and consumer

A team is the **Provider** of every interface for which it publishes a schema, and a **Consumer** of every interface it invokes. **The roles are properties of interfaces, not of teams**: one team is frequently both, and its two roles appear in different rows of §7.1.

**Provider obligations.** Owns the schema; owns the version number; owns the availability commitment; owns the deprecation notice period; owns backward compatibility of the published contract. A provider may change its internals freely provided the published contract remains satisfied.

**Consumer obligations.** Owns only its own adapter and its own verified expectations; may not hand-author a provider's schema; may not open a pull request against a provider to obtain a fix. If a consumer must change provider source to make its own adapter work, the two parties are co-owners, and that fact must be declared in metadata before the change (AC-07).

> Basis: "The consumer team is responsible for implementing the Pact tests in its consumer codebase that will generate the contract, and for publishing it to a shared location" (R-CDC-03); provider contracts are *derived from* consumer contracts (R-CDC-01). The machine-readable expression of this model in an existing system is Backstage's `providesApi` / `consumesApi` relations (R-META-09), which this repository mirrors in `catalog/`.

### D-06 — Authorisation boundary

Authorisation is enforced by the **bounded-context service**, on **every** request, for the requested operation, resource and tenant (D-03). It is never enforced by the shell, the remote, or any client-side code.

Route guards, hidden controls and client-side role checks in a shell or a domain UI artefact are **presentation only**. They are not security controls and must never be documented as such.

> Basis: OWASP — neither the shell nor a remote can enforce authorisation in client-side code; route guards, hidden controls and client-side role checks affect presentation only and can be bypassed (R-MFE-15, R-MFE-16). Module Federation confers **no** isolation: a remote's JavaScript executes with the host page's privileges. The practical control is a Content Security Policy allow-listing remote origins (R-MFE-16) — which is a mitigation of *supply chain*, not a substitute for server-side authorisation.

### D-07 — Declarative composition

Composition is expressed as data in `catalog/` and realised by generated code. A client platform or bounded context never registers itself imperatively into a runtime host object.

> Basis: Backstage replaced imperative plugin registration with a declarative extension tree (R-META-09, R-META-20). Kubernetes' distinction is the canonical one: you declare desired state, and an imperative reconciler makes it true (R-META-01, R-META-03, R-META-04).

### D-08 — Developer environment division of responsibility

`devenv` is the single source of truth for environment **definition**: packages, language runtimes, services, processes, tasks and pinned inputs (R-DV-03, R-DV-05).
`direnv` is the **activation** mechanism only, via `.envrc` (R-DV-10).
`devenv.local.nix` and `devenv.local.yaml` are gitignored personal overrides (R-DV-08).
Secrets are declared in `secretspec.toml` with values resolved from a pluggable backend (R-SCRT-01, R-SCRT-02). Secret values are never committed and never written into `devenv.nix`.

Activation is fixed by DEC-07: `.envrc` + `use devenv`, **not** `devenv hook`. direnv's authorisation model is the reason: it *"will never run an unknown `.envrc` unless explicitly authorised"*, and authorisations are recorded per file hash (R-DIR-01). A shell hook mutates the environment invisibly to a reviewer. The known weakness — the `[whitelist]` directive, which bypasses the allow-list — is prohibited by FR-19 (R-DIR-03).

### D-09 — Metadata catalog

The catalog (`catalog/`) is the **sole** authoritative description of repository topology: teams, bounded contexts, client platforms, ownership, routes, remote bindings and relations.

Every derived artefact — route map, remote registry, aggregator clients, boundary tags, `CODEOWNERS`, ownership documentation, Team API document, CI templates — is generated from it.

The catalog is a *declaration of desired state* in the Kubernetes sense (R-META-01, R-META-03). One correction to a common shorthand: the catalog is **not** itself the source of truth for a running system — it is a checked-in desired-state document that generators and enforcers reconcile against, and the process it feeds is a *derived index*, not the origin (R-META-19).

### D-10 — Dependency rule

Source-code dependencies point inward. A layer may depend only on layers beneath it, and only through an interface it declares. Concrete implementations bind to interfaces at exactly one place: the composition root.

For a bounded context: `adapters → application → domain`, and `domain → nothing outside itself`. Framework packages are **adapters** (R-CA-02: "the framework is an adapter, not an architecture"). A file whose import graph contradicts this is a defect, not a style preference — see AC-08, FR-19.

### D-11 — Pinned resolution

Every remote, shared or external reference affecting build output resolves to an **immutable version**. `latest`, `^`, unpinned URLs and floating tags are prohibited in any manifest, federation config, lockfile reference or template. Where an artefact must change, the update is a reviewable commit that changes a version string.

> Basis: consequence of G-05. Note that this applies to the *build* environment too — Nix's documented pin-defeating flags `--override-input` and `--no-update-lock-file` (R-NIX-03) are prohibited in CI for the same reason.

### D-12 — Ownership resolution (total by construction)

Ownership resolves by a **single** rule, with no precedence, no specificity comparison and no fallback:

> Every path under `teams/<slug>/` is owned by the team whose document declares `metadata.id: <slug>`.

Paths outside `teams/` (`catalog/`, `docs/`, `tools/`, root configuration) are owned by the **platform** team, and this is stated **explicitly** in `catalog/teams/platform.yaml` as `owns` entries — never implied by a default.

Two teams may not both declare an `owns` entry covering the same path; this is a validation error (FR-06). A path covered by **no** `owns` entry is also a validation error (FR-09). Both are detected at validation time, not at review time.

This is deliberately simpler than v2.0.0's longest-prefix-glob resolution. The simplification is *earned*: by making one team own one top-level directory (§4), the precedence problem does not arise.

---

## 4. Repository topology (normative)

### 4.1 The layout

```
cms/
├── catalog/                       # D-09. Sole topology authority
│   ├── schema/                    # zod schemas, .strict() on every object
│   ├── teams/<slug>.yaml          # one document per owning team
│   ├── contexts/<slug>.yaml       # one document per bounded context
│   ├── clients/<slug>.yaml        # one document per client platform
│   └── relations/<id>.yaml        # provider/consumer edges
├── teams/                         # ONE TOP-LEVEL DIRECTORY PER TEAM
│   ├── platform/                  # the Platform team
│   │   ├── ui/                    # @cms/ui            — design system
│   │   ├── composition/           # @cms/composition   — shell ⇄ remote contracts
│   │   ├── authz/                 # @cms/authz         — claim format only
│   │   ├── generator/             # catalog → generated artefacts
│   │   ├── templates/             # scaffolding skeletons
│   │   └── ci/                    # reusable workflow definitions
│   ├── banner/                    # stream-aligned: the banner bounded context
│   │   ├── client/                # web domain UI artefact (Module Federation remote)
│   │   ├── api/                   # bounded-context service (Clean Architecture, FR-22)
│   │   └── contract/
│   │       └── openapi.yaml       # OpenAPI 3.1 (R-META-12)
│   └── web/                       # stream-aligned: the web client platform
│       ├── client/                # D-04 shell — the only Module Federation host
│       └── bff/                   # D-02 aggregator for the browser client
├── docs/
│   ├── PRD.md
│   ├── references.md
│   ├── ownership.md               # GENERATED (FR-09)
│   └── adr/
├── tools/                         # workspace plumbing: boundary configs, env helpers
├── devenv.nix                     # D-08 environment definition
├── devenv.yaml
├── devenv.lock                    # committed; pins the environment
├── secretspec.toml                # secret declarations only, no values
└── .envrc                         # direnv activation (DEC-07)
```

### 4.2 Why team-scoped, not layer-scoped

The v2.0.0 layout used four top-level axes (`apps/`, `bff/`, `teams/`, `platform/`). That layout has three defects:

1. **A single team is fragmented across up to three directories.** The `web` client platform team owns a shell in `apps/web` *and* an aggregator in `bff/web`. Its "one team, one directory" property is false, so the §4.1 property cannot hold.
2. **Ownership becomes a precedence problem.** With four axes, `catalog/teams/*.yaml` must express `apps/**` and `bff/**` with overlapping globs across teams, and v2.0.0 D-12 was forced to invent a longest-prefix-match algorithm with tie-breaking to resolve it. That algorithm is complexity created purely by the directory layout.
3. **It inverts the TT requirement.** Stream-aligned teams own a slice *end to end* with no hand-offs (R-TT-03). Splitting one team's UI and its aggregation tier into two top-level directories reintroduces a hand-off at the directory boundary — the exact thing the topology is supposed to eliminate.

The team-scoped layout satisfies R-MONO-13 directly: *"the structure of an Nx workspace often reflects the structure of an organization."* It also makes the ownership rule **total and order-free** (D-12), which is where the determinism gain comes from.

The cost is real and is accepted: locating "the shell" is no longer a top-level-directory guess. That question is answered by `catalog/clients/web.yaml`, which is generated into an index (§4.4). One lookup, generated, always correct.

**Prohibited top-level directories.** Any top-level directory or file not listed above is a violation. In particular `apps/`, `bff/`, `packages/` and `composition/` do not exist. **Prohibited nested repositories:** no `.git` directory may exist below the root (FR-26).

### 4.3 Ownership, generated

```
catalog/teams/platform.yaml   owns: catalog/**, docs/**, tools/**, <root config globs>
catalog/teams/banner.yaml     owns: teams/banner/**
catalog/teams/web.yaml        owns: teams/web/**
```

`CODEOWNERS` is generated from exactly these entries, one rule per `owns` entry, so the emitted file remains human-auditable. Generation is from metadata only; no hand-maintained duplicate exists (FR-09, FR-10).

The generated rule set is enforced by GitHub **required reviewers** on protected branches (R-OWN-02) — without that setting, `CODEOWNERS` is advisory only and G-01 is not achieved.

### 4.4 Indexes, generated

| Artefact | Purpose | Derived from |
|---|---|---|
| `docs/ownership.md` | Which team owns what, and who provides/consumes what | all catalog documents |
| `teams/web/client/src/generated/routes.generated.tsx` | Route map | `clients/web.yaml#routes` |
| `teams/web/client/src/generated/remote-registry.generated.ts` | Module Federation remote registry, pinned per D-11 | `clients/web.yaml` + `contexts/*.yaml#provides.ui.web` |
| `teams/web/bff/src/clients/*.generated.ts` | Aggregator → bounded-context adapters | `clients/*.yaml#bff` + `contexts/*.yaml#provides.api` |
| `turbo.json` → `boundaries.tags` | The dependency graph of §4.1 | catalog + AC-01, AC-02, AC-03 |
| `CODEOWNERS` | Review routing | `teams/*.yaml#spec.owns[]` |
| `teamapi.yaml` | Team API document | all catalog documents (R-TTA-01, **third-party — see DEC-13**) |
| `teams/platform/ci/*.yaml` | Per-deployable workflow manifests | `contexts/*.yaml` |

### 4.5 Repository split criteria (SPL)

> **DEC-02 — The single repository is conditional, not permanent.**

SPL-01 … SPL-05 are the *only* triggers that reopen DEC-01. Each is objectively checkable.

| ID | Trigger | Check | Consequence |
|---|---|---|---|
| SPL-01 | A **hard** perimeter-access-control requirement exists — a class of code must not be co-resident with another, per a regulatory or contractual boundary, not a preference | Written requirement referencing repository-level access control | That bounded context moves to its own repository. Nx names this one of exactly two legitimate polyrepo conditions (R-MONO-07) |
| SPL-02 | The **Platform team's** sustained budget for workspace tooling falls below the level at which it can maintain boundary enforcement and caching | Two consecutive quarters of missed `check:*` SLOs attributable to tooling, not to team discipline | Re-evaluate DEC-01 wholesale; do **not** default to splitting |
| SPL-03 | A bounded context becomes **> 40 %** of total build time *and* its change rate is < 1 change/week, i.e. it is not on anyone's critical path | CI timing report + VCS history | That unit may be built outside the workspace (Narrowing principle, R-BFF-15), without a repository split |
| SPL-04 | The workspace contains a **large external codebase** whose boundary is already its own release unit, and which must remain independently syncable and contributable | Upstream import would be required; R-MONO-30 | The external codebase stays a polyrepo member. It is not vendored |
| SPL-05 | An **LSC (§1.4) is denied more than twice** in a rolling quarter for the same structural reason | LSC log | The *boundary* is wrong, not the enforcement. Re-derive the bounded context; do not weaken AC-01 |

**Explicitly not a trigger.** Repository size, clone time, "CI is slow", and "we picked the wrong tool" (R-MONO-24, R-MONO-06, R-MONO-09). The first is decomposed into independent dimensions each with a Git-native fix; the second is a missing-tooling symptom (R-BUILD-09); the third is a false inference — Pants *"works well with (but does not require) a monorepo architecture"* (R-DIR-09), so tooling determines the *cost* of a monorepo, not its correctness. **Acquiring a different build tool is not a reason to change topology.**

---

## 5. Application composition layer vs UI business domain (normative)

This is the distinction most often collapsed in micro-frontend programmes, and collapsing it produces a shell that becomes the real bottleneck — the outcome the thin-shell pattern exists to prevent. The named anti-patterns are *Mega Frontend* and *Lack of Skeleton*, both at 100 % practitioner agreement (R-MFE-04).

### 5.1 The two sides

| Axis | Composition layer (`teams/<client>/client/`) | UI business domain (`teams/<ctx>/client/`) |
|---|---|---|
| Question answered | *Which region of the screen shows what, and who is the user right now?* | *What does a banner mean, and what may this user do with it?* |
| Contains | Route map, remote registry, session bootstrap, layout and chrome, error and fallback boundaries, loading shells | Domain components, form schemas, domain validation, domain state, domain API client |
| Knows about domains | Names only — an opaque route segment string | Its own domain in full |
| Business rules | **None** | All of its own; none of any other |
| Owns persistent state | None | Client-side view state only; never authority |
| Knows the provider's URL or route | Yes (registry) | No |
| Knows the federation protocol | Yes | Only through `@cms/composition` types |
| Deploy cadence | Rarely — treated like an OS kernel | Frequently — independently |
| Owner | Client-platform team | Bounded-context owning team |
| Contract | Generated route map and registry (FR-08) | `mf-manifest.json` + generated types (R-MF-06) |
| Testable in isolation with | A fake remote per route | A fake API adapter |

### 5.2 Rules

- The shell **must** own top-level routing and resolve which domain UI artefact mounts for a given URL.
- The shell **must** provide session bootstrap and an error/fallback boundary per remote.
- The shell **must not** contain a domain rule, a form schema owned by a bounded context, or a call to a bounded-context API.
- The shell **must not** import internals of any domain UI artefact — only the entry declared in `exposes`.
- The shell **must not** require a bounded-context change in order to add a route, because routes are generated from metadata (FR-08).

### 5.3 Disqualifying tests

A module in a shell is domain code, not composition code, if **any** of these is true:

1. **State test.** It holds domain state surviving navigation — an entity, a draft, a selection over domain data.
2. **Rule test.** Removing or changing a bounded context changes this module's *logic*, not one line of its configuration.
3. **Vocabulary test.** Its identifiers come from the ubiquitous language of a specific bounded context rather than from navigation, session or chrome vocabulary (R-DDD-01 §1).

Failing any one test means the module is misplaced: it must move to the owning bounded context, or the rule it encodes must move to that context's service.

### 5.4 Why the split is enforced structurally

A shell holding domain logic acquires the two worst properties simultaneously: it deploys rarely *and* changes often. Every domain change becomes a shell release, serialising all teams behind the slowest deployable in the repository. This is why AC-06 is a lint rule rather than a review convention.

---

## 6. Aggregator vs bounded context (normative)

### 6.1 Responsibility ledger

| Aggregator **may** | Aggregator **must not** |
|---|---|
| Fan out to N bounded-context APIs | Own a database, a schema, or a migration |
| Select, rename, flatten and reshape fields | Evaluate a business rule (eligibility, discount, validation) |
| Apply client-specific formatting (case, dates, units) | Hold authoritative domain state between requests |
| Batch and coalesce loads (PERF-08) | Emit domain events other domains consume |
| Cache derived data with an explicit TTL | Be consumed by a client it was not declared for (AC-04) |
| Return partial results with per-section error status | Authorise anything beyond its own transport identity |
| Enforce transport limits (deadline, size, concurrency) | Depend on a shared mutable cache as a source of truth |

### 6.2 Disqualification test — the aggregator has become a bounded context

An aggregator ceases to be an aggregator the instant **any one** becomes true:

| # | Signal | Required action |
|---|---|---|
| T1 | It declares a database driver, an ORM, or a `migrations/` directory | Extract persistence into a bounded context; the aggregator becomes a client of that API |
| T2 | It encodes a rule a domain expert would recognise as domain policy, not presentation policy | Move the rule into the owning bounded context; consume the resulting decision through the API |
| T3 | It needs state to persist between requests in order to answer a question about the domain | That state is domain state. Extract the owning context; the aggregator composes |
| T4 | A domain team must file changes in the aggregator for domain behaviour | Ownership has already transferred. Re-run §6.3 |
| T5 | A second client platform needs a different answer to the same domain question | The question is not client-specific; it is domain behaviour. Extract it |

**T2 is the one that fails silently.** Its operational symptom is a rule that is tested in the aggregator's suite, changes when the domain changes, and is duplicated into a second aggregator when one is built (R-BFF-01, RISK-06).

### 6.3 Extraction procedure (deterministic)

1. Name the rule or state that triggered T1–T5.
2. Identify the ubiquitous-language term it belongs to; that term names the new bounded context (R-DDD-01).
3. Create the bounded context with a store, an owning team, and an API contract.
4. Move the rule **and its tests**. The test file moves with the rule; it is not rewritten.
5. Replace the aggregator's implementation with a call to the new API. Delete the rule.
6. Re-run `contracts:verify`. The aggregator's consumer test now exercises the new provider.
7. Record the extraction as an ADR. **A rule extracted twice is evidence the boundary was drawn wrong**, not that the extraction failed.

### 6.4 Distinction from adjacent patterns

| Pattern | Purpose | Stores state? | Domain rules? | Relation to the aggregator |
|---|---|---|---|---|
| **API Gateway** (R-BFF-07) | Routing, rate limiting, TLS, cross-cutting transport | No | No | **In front of** the aggregator. Cross-cutting concerns stay there and never migrate down (R-BFF-05, R-BFF-06) |
| **Aggregator / API Composition** (R-BFF-05) | Composing one response from several services | No | No | **This is the aggregator** |
| **BFF** (R-BFF-01) | A composition tier dedicated to one client type | No | No | The same thing, client-scoped by definition. §19 DEC-09 fixes the terminology |
| **GraphQL federation** (R-AGGR-01) | Query-level composition across schemas | No (a resolver may cache) | No | An alternative implementation of the same tier. Not adopted in v3.0.0; DEC-11 |
| **Bounded context** (D-03) | Owns a domain slice, its store and its rules | **Yes** | **Yes** | A different kind of thing. If the aggregator needs one, it is now two bounded contexts |

> **Recorded cost, not waved away.** A composition tier is itself a resource cost. Apollo ships a **Rust-native** query planner as its default (R-AGGR-09) and an incremental planner with explicit `beam_width` / `fuel` / `timeout` knobs because planner cost explodes with `@shareable`/`@key`/`@requires` density (R-AGGR-10). This is why DEC-11 keeps federation out of v3.0.0 and why PERF-06 … PERF-09 budget the aggregator's own compute.

---

## 7. Ownership model (normative)

### 7.1 Interface ownership matrix — authoritative

This table *is* the provider/consumer assignment. FR-09 generates enforcement from it; nothing else may assign ownership.

| # | Interface | Provider | Consumer(s) | Contract artefact | Breaking-change obligation |
|---|---|---|---|---|---|
| 1 | Design system `@cms/ui` | `platform` | all teams, all deployables | exported types, semver | major bump + 2-release deprecation |
| 2 | Composition contracts `@cms/composition` | `platform` | all shells, all domain UI | exported types, semver | major bump |
| 3 | Claim / authorisation format `@cms/authz` | `platform` | all bounded-context APIs | JSON Schema (R-META-15) | major bump; expand/contract |
| 4 | Bounded-context API (e.g. `banner-api`) | owning bounded-context team | aggregators only | OpenAPI **3.1** (R-META-12) | expand/contract; never removal within a major |
| 5 | Domain UI artefact — web remote | owning bounded-context team | the browser shell only | `mf-manifest.json` + generated types (R-MF-06) | major + 2-release deprecation |
| 6 | Domain UI artefact — native bundle | owning bounded-context team | that client platform | native bundle contract | major + 2-release deprecation |
| 7 | Aggregator endpoint (e.g. `web-bff`) | owning client-platform team | that client platform only | OpenAPI 3.1 | versions freely; external consumers prohibited |
| 8 | Runtime configuration schema | owning team of each deployable | platform (emits values) | `config.schema.ts` | strict-mode boot failure |
| 9 | Generated topology artefacts | `platform` (generator) | every consumer reads them | generated file + `@generated` marker | regenerate; hand edits prohibited |

Row 9 is what makes G-04 checkable: because topology artefacts are *provided* by the generator and *consumed* everywhere, editing one by hand is a contract violation, not a style violation.

> **Pin recorded:** row 4 and row 7 cite OpenAPI **3.1.x**, not 3.2.x. The live "latest" is 3.2.1 (R-META-13). This is a deliberate pin, consistent with D-11, so that a spec minor cannot change validation semantics underneath the contract test suite. Moving to 3.2 is a scheduled version-bump PR (RISK-10).

### 7.2 Ownership resolution algorithm

Implemented as `catalog:resolve-owner`, run by FR-09. The v3.0.0 steps 2 and 3 left precedence between the `teams/` segment rule and `owns` globs undefined, which meant the answer depended on evaluation order. **Stated in v3.1.0 by ADR-0016 and ADR-0008**, with the ordering made explicit:

1. For a tracked path, take its top-level directory segment.
2. If it is `teams`, take the **second** segment; the owning team is that slug. **This case is decided first and nothing else is consulted.**
3. Otherwise, look for a matching `owns[].paths` entry across all team documents.
4. No match → **error**, naming the path. There is no default (FR-09).
5. Two teams declaring entries that cover the same path → **error** at validation time, naming both teams (FR-06).
6. Emit one `CODEOWNERS` rule per `owns` entry so the generated file stays auditable.

Two invariants make self-declaration safe without a second ownership map:

- **O-1 — no `owns` entry may match a path under another team's directory.** A team therefore cannot grant itself power over anyone else, and cannot claim a path inside a sibling's directory to win a tie. The restriction is structural, not procedural: it is rejected at validation, so no reviewer has to notice.
- **O-2 — a team's `owns` list is exactly `{ "teams/<slug>/**" }`.** The set of things one may declare about oneself is one directory.

Because O-2 makes step 3 reachable only for paths outside every `teams/` directory, the ordering in steps 2 and 3 is not merely preferred — it is the only order consistent with the invariants. `catalog:validate` rejects an `owns` entry matching `teams/<other-slug>/**` by name (FR-06, FR-09).

### 7.3 Consumer escalation

When a change requires a provider to modify its published contract:

1. Consumer opens an issue on the provider, quoting the contract artefact and the failing expectation.
2. Provider decides: accept, or propose an alternative, or declare a breaking change with a migration window.
3. Provider ships; the consumer's consumer test goes green (FR-23).
4. Consumer migrates. Only after the deprecation window ends may the provider remove the old field.

A consumer may **never** open a pull request against a provider's source to obtain a fix (D-05). If it must, AC-07 requires declaring co-ownership in metadata first — which converts the change into a joint decision rather than an untracked dependency.

---

## 8. Metadata-driven architecture

### 8.1 What is metadata here

Everything whose answer is "what exists and who owns it":

| Concern | Metadata | Mechanism |
|---|---|---|
| Teams and their type | `catalog/teams/*.yaml` | validated by FR-06 |
| Bounded contexts and their provides/consumes | `catalog/contexts/*.yaml` | validated by FR-07 |
| Client platforms, their routes and `dataStrategy` | `catalog/clients/*.yaml` | validated by FR-07, FR-13 |
| Provider/consumer edges | `catalog/relations/*.yaml` | validated by FR-07 |
| Topology | all of the above | generated by FR-08 … FR-11 |
| Build graph | `turbo.json#boundaries` | generated, merged between markers |
| Dependency versions | root lockfile | enforced by FR-21 |
| Environment | `devenv.nix`, `devenv.yaml`, `devenv.lock` | enforced by FR-18 |
| Secrets required | `secretspec.toml` | enforced by FR-20 |
| Deployment manifests | per deployable | enforced by FR-15 |

The governing pattern is Kubernetes': **declare desired state; an imperative reconciler makes it true or fails** (R-META-01, R-META-03, R-META-04). One caveat carried from R-META-19: the catalog is a *checked-in desired-state document*, not the running index — Backstage's catalog is explicitly a derived index built by an ingestion pipeline. We do not claim the catalog is a live system of record.

### 8.2 Catalog document schemas (normative field specification)

**`catalog/teams/<slug>.yaml`**

```yaml
apiVersion: cms.platform/v3
kind: Team
metadata:
  id: banner                       # slug; never renamed once referenced
spec:
  info:
    name: Banner Team              # display label, renameable
    focus: Banner and campaign management end to end
    type: stream-aligned           # stream-aligned | platform | enabling | complicated-subsystem
  channels:
    - { type: slack, name: "#banner" }
  owns:                           # sole input to CODEOWNERS
    - kind: bounded-context
      id: banner
      paths: ["teams/banner/**"]
  cognitiveLoad: { domains: 1, domainsSimple: 0, domainsComplicated: 0, domainsComplex: 1 }
```

`type` maps to the four team types (R-TT-01, R-TT-02). `cognitiveLoad` is the counterweight to unbounded `owns` growth: a team whose load assessment rises above the bounded threshold must split before taking another domain (R-TT-01, R-TT-11).

**`catalog/contexts/<slug>.yaml`**

```yaml
apiVersion: cms.platform/v3
kind: BoundedContext
metadata:
  id: banner
spec:
  team: banner                     # → catalog/teams/banner.yaml
  store: postgres                  # sole writer; aggregators have no store (AC-03)
  language: [banner, placement, rotation]   # ubiquitous language seeds (R-DDD-01)
  provides:                        # provider role (D-05)
    api:
      id: banner-api
      openapi: ./contract/openapi.yaml
    ui:
      web:     { remote: banner-web, mfName: banner }
      mobile:  { module: "@banner/mobile" }
      desktop: { module: "@banner/desktop" }
  consumes: []                     # a bounded context consuming another is a review event
  authorises: every-request        # literal; D-06 permits no other value
```

A non-empty `consumes` is legal but requires a matching `relations` record (FR-07) and an ADR, because it is the first signal of a context-map relationship that may warrant an anti-corruption layer (R-DDD-02, R-DDD-03).

**`catalog/clients/<slug>.yaml`**

```yaml
apiVersion: cms.platform/v3
kind: ClientPlatform
metadata:
  id: web
spec:
  owner: web
  runtime: browser                 # browser | mobile | desktop
  shell: true                      # false for clients that compose natively
  bff:
    id: web-bff                    # exactly one; 1:1 with the client (AC-04)
  routes:                          # consumed by FR-08; valid only when shell: true
    - path: /banners/*
      context: banner
      remote: banner-web
      baseUrl: /_remotes/banner
  errorBoundaries:
    - { remote: banner-web, fallback: "./components/RemoteError.tsx" }
```

**`catalog/relations/<id>.yaml`**

```yaml
apiVersion: cms.platform/v3
kind: Relation
metadata:
  id: web-bff-consumes-banner-api
spec:
  type: consumesApi                 # providesApi | consumesApi | ownedBy | dependsOn | partOf
  from: web-bff
  to: banner-api
  contract: ./teams/banner/contract/openapi.yaml
  breakingChangePolicy: expand-contract
  deprecationWindowReleases: 2
```

kind: Interface
metadata:
  id: banner-api
spec:
  kind: api                       # api | event | ui
  owner: banner                   # always the providing team
  contract: ./teams/banner/contract/openapi.yaml
  digest: sha256:…                # published; the consumer gate verifies against this, not a local copy (ADR-0020)
```

```yaml
kind: Budget
metadata:
  id: BUD-07
spec:
  metric: sharedModuleDuplication
  threshold: 0
  scope: per-route
  owner: each-context-team          # every entry names an owner; an unowned budget is not enforced (AC-13)
  check: check:budgets
  review: quarterly                 # a threshold change is an ADR, never a silent edit (PRD §15)
```

The v3.0.0 schema had no `Interface` kind, so provider/consumer roles had nowhere to attach — ADR-0007 makes the interface the unit of ownership, and the roles were being carried on the relation instead. `relations/` becomes derived: a `consumesApi` relation is not authored, it is computed from the two `Interface` declarations it names. One declaration of each fact.

`Budget` is the kind that makes §12.2a enforceable. A threshold written in a PRD is a sentence; a threshold in `catalog/budgets.yaml` with an owner and a check is a gate. `spec.digest` is likewise load-bearing: the consumer's contract test verifies against the provider's **published** digest, so a consumer cannot be green against a schema the provider has already moved past (ADR-0020).

The vocabulary is Backstage's (R-META-09) so the catalog can be loaded into a catalog without translation. One correction carried from R-META-09: **consume the relation, not `spec.owner`** — the owner may be derived from `CODEOWNERS` rather than authored in YAML. We therefore treat `relations` as the authoritative record and never hand-author `ownedBy` edges into a second place.

---

## 9. Developer environment

| Concern | Owner of the decision | Mechanism | Evidence |
|---|---|---|---|
| What tools exist | Repository (committed) | `devenv.nix` | R-DV-03 |
| Which versions | Repository (committed) | `devenv.lock` | R-DV-05 |
| Personal additions | Individual (gitignored) | `devenv.local.nix`, `devenv.local.yaml` | R-DV-08 |
| Activation | Repository (committed) | `.envrc` → pinned `source_url` + sha256, then `use devenv` — see FR-18 | R-DV-10, R-DIR-01, R-DV-15 |
| Trust decision | Developer | `direnv allow`, recorded per file hash | R-DIR-01 |
| Which secret *names* are needed | Repository (committed) | `secretspec.toml` | R-SCRT-02 |
| Which secret *values* | Per profile, never committed | pluggable provider backend | R-SCRT-01, R-SCRT-03 |
| Local services and processes | Repository (committed) | `services.*`, `processes.*`, `tasks.*` | R-DV-06, R-DV-07 |
| Deployable config validation | Deployable | `config.schema.ts`, strict parse at boot | FR-16 |

**DIR-01 — `direnv`'s `[whitelist]` is prohibited.** It bypasses the entire allow-list, and direnv's own documentation warns it "should be used with great care" (R-DIR-03). Since D-08 makes direnv the trust gate, the bypass is the one thing that must not exist.

**DIR-02 — `require_allowed` is enabled.** It extends the allow-list to lockfiles consumed by the activation script (R-DIR-02), which closes the "trusted lockfile" gap for us automatically.

**DIR-03 — `NODE_ENV=production` is set in every deployed environment.** Node skips expensive per-process safety checks on `process.env` in production (R-BE-15). Free, and citable.

**DIR-04 — configuration values are delivered, secrets are not.** Twelve-factor says store config in the environment (R-CFG-01) and says **nothing about secret storage** (R-SCRT-07). The stronger and more precise argument for not committing a `.env` is SecretSpec's own: *"Eliminate secrets from environment variables and configuration files"* (R-SCRT-01). We cite both and use each correctly. Migration off an existing `.env` uses `secretspec init --from dotenv://` (R-SCRT-03).

---

## 10. SOLID and Clean Architecture (normative mapping)

Each principle gets exactly one enforcement mechanism. A principle with no enforcement is not adopted.

| Principle | How it is honoured here | Enforcement | Failure looks like |
|---|---|---|---|
| **S**ingle Responsibility | A bounded context owns one domain slice; the shell owns routing only; an aggregator owns composition only. "Reason to change" maps to a team (R-SOLID-02, R-SOLID-06) | AC-01, AC-05, AC-06 + generated ownership | Two teams edit the same behaviour |
| **O**pen/Closed | Contracts (OpenAPI, `mf-manifest.json`, JSON Schema) are extended by adding optional fields; providers add behaviour behind the contract (R-SOLID-03) | FR-23 consumer tests; breaking-change check on schema diff | A consumer must change to accept an additive provider change |
| **L**iskov Substitution | Every adapter is substitutable for the port it implements; a fake with no production wiring change proves it (R-SOLID-04) | AC-08; adapter suites run against a shared contract suite | A fake needs production-only behaviour to pass |
| **I**nterface Segregation | Ports are declared by the *consumer* of the port, one capability per interface. An aggregator consumes `BannerApi`, never `BannerRepository` (R-SOLID-05) | FR-19 lint rule: `domain/` declares no interface it does not use | A port grows a method with zero callers |
| **D**ependency Inversion | D-10. The 1996 paper's core claim — *"high-level modules should not depend on low-level modules; both should depend on abstractions"* (R-SOLID-01) — is the reason `domain/` may not import a framework | `dependency-cruiser` + ESLint `no-restricted-imports` | A domain type imports a framework type |

### 10.1 Anti-over-application guard

SOLID is applied **only at layer boundaries** (D-10) and imposes no SOLID-derived pattern inside a single layer.

This guard is stated from two independently verified positions, because the usual citation for it does not exist:

- **R-SOLID-09 is rejected.** *"Solid Considered a Harmful"*, attributed to Brian Foote, does not exist — the URL 404s, no Wayback snapshot resolves, and Foote's blog contains no such post. **It must never be cited.** The substitute for the author-side qualification is R-SOLID-08 (*Solid Relevance*), in which Martin himself limits the principles. The substitute for independent criticism is R-SOLID-10 (*Big Ball of Mud*), which is real and is the actual Patterns-community objection to integration-heavy architecture.
- **The practical test.** A new abstraction is justified only by a port that has (a) a real consumer, and (b) a second implementation — a test fake counts. This is derived from DIP's own mechanism (R-SOLID-01, R-CA-01), not from any commentary about it.

### 10.2 Layer layout for a bounded-context API

```
teams/banner/api/src/
├── domain/            # entities, value objects, domain services, repository *interfaces*
│                      # imports: nothing outside domain/ (D-10, AC-08)
├── application/       # use cases, ports owned by this use case, transaction boundaries
│                      # imports: domain only
├── adapters/
│   ├── inbound/       # HTTP controllers, request/response mapping
│   └── outbound/      # persistence, message bus, external provider clients
│                      # imports: domain + application; framework packages live ONLY here
├── config/            # config.schema.ts (FR-16)
└── main.ts            # composition root; the ONLY file binding a port to an adapter
```

Dependency direction: `main.ts → adapters → application → domain`.

The source tree is named for the domain, not the framework (R-CA-03). NestJS custom providers — `useFactory`, `useExisting` (R-BE-06) — are the mechanism that keeps the composition root free of framework assumptions about domain objects.

### 10.3 Backend framework performance, stated honestly

| Claim | Value | Source | Confidence |
|---|---|---|---|
| Request-scoped DI providers, properly designed, cost | "should not see latency increase by more than **~5 %**" | R-BE-03 | Framework documentation, verbatim |
| Request-scoped DI providers, at 30 k concurrent requests | "there are **30k ephemeral instances of the controller**" | R-BE-03 | Framework documentation, verbatim |
| Fastify vs Express | "nearly twice the benchmark results" | R-BE-01 | **Vendor-originated and not independently replicated** — the figure originates from Fastify's own marketing. Both frameworks now steer you to benchmark *your own application* (R-BE-21). **Directional only; re-measure on our routes** |

Therefore: **NEST-01** — the default provider scope is singleton; a request- or transient-scoped provider requires an ADR naming the reason and the measured cost (PERF-09).

---

## 11. Frontend architecture: micro-frontends (web client platform only)

### 11.1 Adopted for one reason only

> **DEC-06 — Micro-frontends are adopted for deployment independence (B3) and team autonomy. Never for isolation.**

Micro-frontending confers **no** browser security boundary: a remote's JavaScript executes with the host page's privileges (R-MFE-15, R-MFE-16). Isolation must not appear in any design justification. Style and dependency leakage between remotes is accepted and mitigated by contract, not by isolation — Module Federation does not isolate CSS, and Subresource Integrity does **not** apply to remotes, because `remoteEntry` URLs resolve at runtime from a manifest and the fetched script is *evaluated*, not `<script integrity=…>` (R-MFE-17). CSP allow-listing remote origins is the practical control (R-MFE-16); it mitigates supply chain and does not substitute for D-06.

The costs are real and are budgeted, not waved away: increased payload size, code duplication, and monitoring complexity are documented in the peer-reviewed multivocal literature review (R-MFE-06). §12 budgets all three.

Adoption posture, for the record: Thoughtworks moved *Micro frontends* to **Adopt** in April 2019, last updated May 2020, and it is **not on the current Radar edition** (R-MFE-03). The peer-reviewed anti-pattern catalogue names *Micro Frontend as the Goal* at 100 % practitioner agreement (R-MFE-04) — which is NG-03.

### 11.2 Integration mechanism

Runtime integration via JavaScript, Module Federation (R-MFE-01). Build-time integration is **explicitly rejected**: Fowler recommends *"strongly against"* it because of the lockstep-release pain it causes (R-MFE-01). Runtime via Web Components and iframes are recorded alternatives and are not adopted; Web Components' Shadow DOM encapsulation is noted as the strongest isolation story of the three (R-MFE-12) but is incompatible with the shared singleton requirement in PERF-05.

### 11.3 Module Federation configuration decisions (normative)

These are **deviations from upstream defaults**, each with a reason and a measurement.

| # | Option | Decision | Reason |
|---|---|---|---|
| MF-1 | `shareStrategy` | **`'loaded-first'`**, not the default `'version-first'` | The default *"eagerly loads all remote entries at init"*; `'loaded-first'` defers remote loading on demand and is explicitly recommended upstream for performance and offline resilience. Under `'version-first'` the `errorLoadRemote` lifecycle fires `beforeLoadShare` when a remote is offline (R-MF-12) |
| MF-2 | manifest `disableAssetsAnalyze` | **never set** | Upstream warns verbatim *"After setting, the preload function will be disabled!"* (R-MF-08). Disabling it is exactly the waterfall regression PERF-04 forbids |
| MF-3 | `experiments.externalRuntime` | **enabled** | Upstream's own numbers: `remoteEntry.js` gzip **21,437 B** → 17,998 B (`disableSnapshot` + `target: 'web'`) → **5,381 B** (+ `externalRuntime`). This is a vendor publishing numbers that *hurt* its unconfigured default (R-MF-14) |
| MF-4a | `experiments.disableShared` | **never set** (false) | Upstream: use it *"only when the build has no `shared` configuration"*; both the Vite and Rspack surfaces warn when it meets a non-empty `shared` block (R-MF-21, R-MF-23). The v3.0.0 text said **enabled**, which contradicted MF-5 and made PERF-05 false. **Corrected in v3.1.0 by ADR-0013.** |
| MF-4b | `experiments.disableRemote` | **enabled on remotes only** | Legal only for a remote that provably consumes no other remote. Minified `remoteEntry.js` 73,154 B → 52,916 B (−27.66 %) (R-MF-24). Not the flag that buys the budget — see MF-4c/MF-3 |
| MF-4c | `experiments.optimization.disableSnapshot` | **true in production, false in dev** | Required for PERF-03: with `externalRuntime` and `disableSnapshot` **off** the published figure is 8,222 B, over the 8 KB budget; with it, 5,381 B (R-MF-22). It costs HMR and TypeScript type sync, which are dev-time concerns only. Never hand-set — derived from the catalogue with an environment switch |
| MF-4d | `experiments.provideExternalRuntime` | **true on the shell only** | The shell becomes the federation **runtime provider**, not merely a mount point. Legal only because the shell has **no `exposes`**; upstream throws if both are set (R-MF-23). "Exactly one instance" applies to the federation runtime as it does to React (PERF-05) |
| MF-5 | `shared.react`, `shared['react-dom']` | `singleton: true` **and** explicit `requiredVersion` | `singleton` *"ensures that shared modules are only loaded once between different versions"*; if `requiredVersion` is not met the module **is not loaded at all** (R-MF-03). PERF-05 asserts exactly one resolved instance |
| MF-6 | output `filename` | `[name].[contenthash:8].js` | Enables long-lived immutable CDN caching of `remoteEntry` (R-MF-16, R-RES-21) |
| MF-7 | remote URLs | **pinned per D-11**; rewritable at runtime via a runtime plugin | Version pinning is the reproducibility mechanism (`buildInfo.buildVersion`, `buildVersion`); a runtime plugin is the documented way to redirect remotes to a CDN **without a rebuild** (R-MF-07, R-MF-10) |
| MF-8 | `runtimePlugins` | one custom plugin required: fallback on remote load failure | The documented use case is *"add recovery/fallback"* (R-MF-10). Without it, one bad remote takes down a route |
| MF-9 | remote resolution source | the generated registry (§4.4), never hand-edited | D-07, FR-08 |

> **Correction carried:** a widely repeated claim is that `shareStrategy` accepts `'eager'`. It does not. The two values are `'version-first'` and `'loaded-first'`; `eager` is a **per-entry flag inside the `shared` block** (R-MF-12, R-MF-13).

### 11.4 Frontend observability, as a precondition

Before a second remote is added, OpenTelemetry browser instrumentation **must** be present (R-MFE-19). Monitoring complexity is a documented, quantified cost of micro-frontends (R-MFE-06) and cannot be retrofitted cheaply once there are N independently-deployed bundles. This is a gate on PH-6 exit.

---

## 12. Performance requirements (normative)

Every threshold is quoted from a verified source. Where **no** citable source exists for a number, the PRD mandates a **measurement** instead and attributes the number to nobody (R-BUILD-19, R-BUILD-40, R-BE-01).

### 12.1 Browser performance

| ID | Requirement | Threshold | Measurement | Source of the threshold |
|---|---|---|---|---|
| PERF-01 | Core Web Vitals pass on every route of every client platform | LCP ≤ **2.5 s**, INP ≤ **200 ms**, CLS ≤ **0.1**, at the **75th percentile**, segmented mobile/desktop. All three must pass | Field data (RUM), p75, segmented | R-PERF-01 … R-PERF-04 — the canonical pass bar |
| PERF-02 | Total JavaScript transferred for any single route | ≤ **300 KB**; shell-critical ≤ **150 KB**; ≤ **20** JS requests | CI, per-route bundle analysis | Budget shape from R-PERF-11 (`budget.json`: 300 KB total / 150 KB script); **the 558 KB median** is from R-PERF-15 (Web Almanac 2024) and is the number we must beat, not a target |
| PERF-03 | `remoteEntry.js` gzip size, per remote | ≤ **8 KB** | CI on the built artefact | Unconfigured is 21,437 B. With MF-3 + MF-4c it is **5,381 B**. Without MF-4c it is 8,222 B and the budget is **unreachable** — which is why MF-4c is mandatory rather than optional (ADR-0013, R-MF-22). 8 KB leaves headroom without exceeding the tuned figure |
| PERF-04 | Remote load waterfall | No route initiates a remote fetch that is not triggered by navigation to that route. Asset analysis and preload **must** remain enabled | Network trace in CI; `manifest.disableAssetsAnalyze` asserted absent | R-MF-08, R-MF-09, R-MF-16 |
| PERF-05 | Framework instances | Exactly **1** resolved instance of `react` and `react-dom` per page | Runtime assertion in the shell; test fails if a second copy is constructed | R-MF-03. Also asserted by RISK-02's mitigation |
| PERF-06 | Aggregator request latency, per route class | Declared p99 SLO per route class in the OpenAPI description. Per-dependency timeout budgets **must sum below** the request budget | In-process histogram; p99, never the mean | SLO framing R-RES-14, R-RES-15; **p99 not mean** because fan-out multiplies per-hop latency variance (R-RES-09); four golden signals R-RES-13 |
| PERF-07 | Aggregator fan-out graph | A response plan must contain no **gratuitous `Sequence`** node — a dependency only where a later subgraph's result genuinely depends on an earlier one | Query-plan / trace inspection against R-AGGR-06's node taxonomy | `Sequence` is defined as *"one subgraph's response depends on data that first must be returned by another"* (R-AGGR-06). Where a `Sequence` is genuinely required, `@defer` (R-AGGR-11) or a partial response with per-section status (FR-18) is the escape |
| PERF-08 | No N+1 | Load batching with a **per-request** loader. Loader instances are created per request and never shared across requests | Instrumented call count per downstream endpoint per request | R-RES-17: DataLoader *"coalesce[s] all individual loads which occur within a single frame of execution"*. R-RES-18: its cache serves *"only … in the context of a single request"* — sharing a loader across requests is a correctness bug, not a performance win |
| PERF-09 | Aggregator resilience cost, per downstream dependency | Circuit breaker, bulkhead pool and timeout **each** configured. Retry budget summed across the whole call tree must not exceed **10 %** of requests | Config assertion + retry-metric alert | R-RES-01 (retry budgets), R-RES-03 (circuit breaker, *"consider a timeout for each try"*), R-RES-05 (bulkhead), R-RES-11 (*"retries should be a tiny fraction of requests"*) |
| PERF-10 | Runtime health | Event-loop lag p99 **< 50 ms**; monitored with `monitorEventLoopDelay` | In-process histogram, exported as a metric | R-BE-10: default `resolution` is 10 ms and `percentile(n)` is reported in nanoseconds — the threshold is ours; the mechanism is upstream |
| PERF-11 | Caching | Cache-aside for all aggregator reads. **Key-versioning** (short TTL jitter on hot keys) and **request-coalescing / single-flight** enabled on any key with measured read amplification | Config assertion + cache-hit metric | R-RES-06, R-RES-07, and R-RES-08 whose documented mechanisms are exactly key-versioning and request coalescing |
| PERF-12 | Container requests and limits | Every container declares `requests` and `limits` for cpu and memory. CPU limit enforced by CFS quota **throttling**, not rejection | Deployment manifest assertion | R-COST-05: throttling, not rejection, is the right-sizing penalty; the scheduler *"refuses to place a Pod"* on a capacity check failure even when actual usage is low |

### 12.2 Bundler cost as a first-class metric

PERF-01 … PERF-05 measure the *output*. This subsection measures the *cost of producing it*, which is a separate and usually-unmeasured axis.

| ID | Requirement | Threshold | Measurement |
|---|---|---|---|
| PERF-13 | `remoteEntry.js` bundle inspection is a required CI step | Fails when it exceeds PERF-03 | `size-limit` (R-PERF-19), configured per R-PERF-10 / R-PERF-11. `size-limit` is cited because it measures **download-plus-execute time**, not bytes — upstream's stated reason: *"a much more accurate metric compared to the size in bytes"* |

> **Bundler memory is a named measurement, not a cited fact.** R-BUILD-40 records that **no primary source exists** for an Rspack-vs-Vite memory comparison, and R-BUILD-41 confirms Vite's own docs contain no figures. Therefore **RES-07** does not assert a memory advantage. It mandates measuring `process.memoryUsage().rss` of the dev server against a fixed fixture, recorded per release, so the claim is made from our own data or not at all.

### 12.2a Artefact-side budgets

PERF-01 … PERF-13 measure one navigation. They say nothing about what the *artefact* costs: duplicated modules, unbounded remotes per route, repeated CSS, or slow mounting. The v3.0.0 text bounded none of these. **Stated in v3.1.0 by ADR-0019**, as metadata in `catalog/budgets.yaml` with a named owner and a blocking gate per entry — a threshold in prose is not a budget, because nothing refuses to build when it is exceeded (ADR-0022).

| ID | Budget | Threshold | Owner | Why |
|---|---|---|---|---|
| BUD-06 | Aggregate JS emitted for one route across all remotes | ≤ 2× the PERF-02 route budget, and ≤ **3** remotes per route | Platform | Artefact, build and CDN cost, unmeasured before |
| BUD-07 | Shared-module duplication count per route | **0** | each context's own team | A semver mismatch silently bundles a private copy of React, and every test still passes |
| BUD-08 | CSS transferred per route | ≤ **1** design-system stylesheet | Platform | Federation does not isolate CSS; each remote re-sending it is a regression nobody can attribute |
| BUD-09 | Remote mount p95, measured in the field | ≤ **250 ms** after navigation commit | Platform | Core Web Vitals do not attribute a regression to a named remote, so the budget has to |

BUD-07 is the only one set to zero, and the reason is that its failure is silent: everything renders, every test is green, and two Reacts are now in the page. That is the failure mode PERF-05 exists to prevent, and a non-zero threshold would permit the exact case PERF-05 forbids.

### 12.3 Honest limits of this section

| Assertion we are **not** making | Why |
|---|---|
| "Our bundle is smaller than Vite's would be" | No reproducible cross-bundler memory or size benchmark is published by either project (R-BUILD-40) |
| "Fastify gives us 2× Express throughput" | The figure originates from Fastify's own marketing and has not been independently replicated (R-BE-01, R-BE-21) |
| "pnpm/Bun uses N× less disk" | Both are vendor architectural claims with **no published benchmark** (R-BUILD-22, R-BUILD-23). We adopt the mechanism (content-addressable store, hardlinks) and measure the result ourselves (RES-04) |
| "Build cache hit ratio should be 80 % because Google says so" | No vendor-neutral source publishes a target (R-BUILD-19). 80 % is **our** team SLO; the *mechanism* is documented (R-BUILD-16, R-BUILD-02) |
| "Fan-out in Node is I/O-bound, therefore free" | No primary source classifies it so. It is an architectural **assumption** with a named measurement: PERF-10 (event-loop lag) and PERF-06 (p99) exist precisely to falsify it |

---

## 13. Resource-efficiency requirements (normative)

| ID | Requirement | Threshold | Measurement | Note |
|---|---|---|---|---|
| RES-01 | Exactly one dependency lockfile, at the repository root | 1 | `find` for `bun.lock`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` below the root returns nothing | The present repository has **five** |
| RES-02 | Deterministic install in CI | `--frozen-lockfile` | CI config assertion | R-BUILD-25; the `npm ci` principle (R-BUILD-27): require the lockfile, never write it |
| RES-03 | Environment activation, warm binary cache | ≤ **10 s** directory entry → ready shell | Timed `direnv` reload | R-DV-10 |
| RES-04 | Environment activation, cold binary cache | ≤ **300 s**, excluding first population of the binary cache | Timed `devenv shell` | Realisation is fetching-or-building a closure (R-NIX-05); speed is entirely cache-hit-rate dependent against `cache.nixos.org` (R-NIX-06). The exclusion is stated so the number is honest |
| RES-05 | Tooling task latency: `catalog:generate` | ≤ **5 s** | Timed |
| RES-05a | Scaffolding a new bounded context end to end (template execution → passing `typecheck` + `lint` + `turbo boundaries`) | ≤ **60 s** | Timed FR-12 run | |
| RES-06 | Tooling task latency: `turbo boundaries` on a full tree | ≤ **30 s** | Timed | |
| RES-07 | Dev-server memory regression | RSS of the dev server measured against a fixed fixture on every release; **no threshold asserted** until we have 3 data points | `process.memoryUsage().rss` | R-BUILD-40, R-BUILD-41 — a measurement, not a claim |
| RES-08 | CI compute | Affected-based task selection. Task **cache hit ratio ≥ 80 %** on `main` | Structured cache telemetry | R-BUILD-08, R-BUILD-12. 80 % is our SLO (R-BUILD-19). **Note the most common cause of a low ratio:** Nx defaults inputs to `["default","^default"]`, so *any* change in *any* dependent project busts the cache (R-BUILD-09); and under Turborepo `envMode: "strict"`, *"Passthrough values do not contribute to hashes"* — undeclared env vars never invalidate (R-BUILD-02). Both are checked by FR-25 |
| RES-09 | Runtime image size | Multi-stage build; a base image without a shell or package manager | Image size assertion | R-BE-16, R-BE-17, R-BE-18 |
| RES-10 | Cost attribution | Every deployable's cloud cost is attributable to its owning team via tag-based allocation, derived from `catalog/` | FinOps allocation report | R-COST-02, R-COST-01. Unit economics — cost per unit of business value — is the metric that ties infra cost to a product outcome (R-COST-04). Right-sizing is measured against requests/limits (PERF-12), with VPA as the automation (R-COST-07) |

---

## 14. Functional requirements

### Metadata and catalog

**FR-01 — LSC is the only cross-team edit path.**
No change to a directory owned by another team may merge without either (a) the owning team's approval, or (b) an approved LSC carrying an `Owners-Override` trailer and a second non-author approver (AC-11).
*Verification:* `check:lsc` rejects a PR that touches a non-owning team's directory when neither (a) that team approved nor (b) an `Owners-Override` trailer naming it is present. A PR carrying the trailer with only one approval is rejected (AC-11). Every case above is a fixture in `tools/checks/test_check_pins.py`.

**Resolution of an ambiguity in the v3.0.0 text, stated in v3.1.0.** The v3.0.0 verification sentence read "a PR touching two teams' directories with no `Owners-Override` trailer is rejected", while FR-01's own text made "(a) the owning team's approval" a sufficient alternative to the trailer. Read together they cannot both hold: the first rejects a change the second permits. The second is now normative and the first is read as assuming the proposer owns none of the touched paths.

The rule that reconciles them is §1.4's own quotation of Chromium — the override is recorded **on every non-owning team touched**. So a change proposed by a team that already owns every path it touches overrides nobody, needs no trailer, and is judged only on whether the other owners approved. A change touching any directory the proposer does not own needs either that owner's approval or a trailer naming it. `check:lsc` implements exactly this and takes `--author-team` and `--team-approval` from CI; an approver login cannot be mapped to a team inside the check, so it is passed in rather than guessed.

**FR-02 — Strict catalog schema authority.**
`catalog/schema/*.schema.ts` defines every catalog document with zod, `.strict()` on every object so unknown keys are rejected (R-CFG-03).
*Verification:* a document with an unrecognised key makes `catalog:validate` exit non-zero and print the offending key path on stderr.

**FR-03 — Catalog documents are self-describing.**
Every document carries `apiVersion: cms.platform/v3`, `kind`, and a `metadata.id` matching `^[a-z0-9]+(-[a-z0-9]+)*$`.
*Verification:* a document missing any of the three fails validation.

**FR-04 — Team type is declared and validated.**
`spec.info.type` ∈ {`stream-aligned`, `platform`, `enabling`, `complicated-subsystem`} (R-TT-01).
*Verification:* any other value fails validation with the permitted set printed.

**FR-05 — The catalog is the sole topology input.**
Route maps, remote registries, aggregator clients, boundary tags, `CODEOWNERS`, ownership docs, Team API document and CI manifests derive **exclusively** from `catalog/`.
*Verification:* `catalog:generate && git diff --exit-code` is clean.

**FR-06 — Exactly one owner; no overlap.**
Each catalog document declares `owner`/`team` as a slug resolving to an existing team document. Two teams may not both cover the same path.
*Verification:* validation fails naming both slugs when globs overlap; fails when a referenced slug has no document.

**FR-07 — Relations are declared, not inferred.**
Provider/consumer edges are explicit `relations` records modelled on Backstage's `providesApi`/`consumesApi` (R-META-09). A relation targeting a non-existent entity fails validation. A non-empty `contexts.*.consumes` requires a matching relation.
*Verification:* a relation with an absent target fails; a `consumes` entry without a relation fails.

**FR-08 — Generated route map and remote registry.**
For each client platform with `shell: true`, the generator emits the route map and the Module Federation remote registry, every remote pinned per D-11.
*Verification:* adding a route to `catalog/clients/web.yaml` and regenerating produces a new entry with no manual edit, and the emitted remote entry contains no `latest` or unpinned URL.

**FR-09 — Generated ownership enforcement, total coverage.**
`CODEOWNERS` and `docs/ownership.md` are emitted from `catalog/teams/*.yaml#spec.owns[]` via §7.2, covering 100 % of tracked paths.
*Verification:* `check:catalog` exits non-zero naming every unmatched path, and naming both teams when two entries cover the same path. On a correct tree it exits zero.

**FR-10 — Generated-file markers.**
Every generated file opens with a comment containing the literals `@generated` and `do not edit`.
*Verification:* `catalog:generate && git diff --exit-code` in CI; plus a grep asserting both markers on line 1 of every generated file.

**FR-11 — `CODEOWNERS` is enforced, not advisory.**
Branch protection on `main` requires approval from the owning team for every touched team directory.
*Verification:* a PR touching only `teams/banner/**` from a non-member cannot merge without a banner approval.

### Scaffolding and templates

**FR-12 — Self-service scaffolding.**
`teams/platform/templates/` contains one template per scaffoldable unit type. Parameters are declared as JSON Schema (R-META-15). Each template's skeleton produces a unit that passes `typecheck`, `lint` and `turbo boundaries` immediately after generation with zero manual edits. A local runner applies the same skeletons in-repository, so NG-01 does not block self-service.
*Verification:* a clean run of each template followed by `typecheck && lint && turbo boundaries` exits zero; a dry-run mode executes without side effects.

**FR-13 — Client/aggregator cardinality in metadata.**
Each `catalog/clients/*.yaml` declares exactly one `bff.id` (AC-04). Each route additionally declares a `dataStrategy`, and the aggregator's participation in the request path is derived from it rather than decided per route by whoever wrote it.
*Verification:* a document declaring two aggregators, or an aggregator claimed by two clients, fails validation.

**`dataStrategy` — when the aggregator participates.** The v3.0.0 text left this unspecified. With the shell forbidden to call a context API and a remote forbidden to call an aggregator, three designs were equally compliant, so the first real decision about request flow would have been made by accident. **Stated in v3.1.0 by ADR-0014.**

| Value | Legal iff | Data path |
|---|---|---|
| `none` | the route declares no `context` | shell → aggregator for chrome and session only; no context is called |
| `direct` | **exactly one** `context` | remote → **its own** context API. The aggregator is not in the request path |
| `composed` | **≥ 2** contexts, or an explicit `clientShape` | shell → aggregator → N context APIs; each remote receives its own section as a prop |

Validation rejects `direct` with a count other than one, and `composed` with fewer than two contexts and no `clientShape`. The value is generated into the composed client by ADR-0006, so it cannot drift from the composition it describes.

Two properties follow, and both are the point. The aggregator is never speculative: a product with one context has no composed routes and a correspondingly small aggregation tier. And one route speaks one vocabulary — `direct` the context DTO, `composed` the page DTO — so a single domain is never re-serialised twice (D-04).

**FR-14 — Boundary enforcement, two independent mechanisms.**
`turbo.json` carries a `boundaries.tags` block encoding AC-01, AC-02 and AC-04. `turbo boundaries` is a non-cached required check. Because the feature carries an **Experimental** label (R-BND-01), a second, non-experimental path (`dependency-cruiser`) enforces the same constraints, so correctness does not rest on one feature (RISK-11, DEC-14).
*Verification:* an intentional illegal import (shell → bounded-context API) fails **both** tools; the change is reverted in the same commit.

**FR-15 — Deployable package declarations.**
No deployable declares a database driver, an ORM, or a `migrations/` directory (AC-03); every deployable defines `build`, `lint`, `typecheck`; no package contains its own lockfile (RES-01); all package names are namespace-qualified (`@cms/<unit>-<artefact>`).
*Verification:* a `dependency-cruiser` forbidden-dependency rule over `**/bff/**`; a `find` for lockfiles below the root returning nothing; a check asserting no two workspace packages share a `name`.

**FR-16 — Strict runtime configuration validation.**
Each deployable has a `config.schema.ts` defining its environment contract, validated at process start with strict object parsing so unknown keys are rejected (R-CFG-03). A validation failure terminates the process **before** it binds a listening socket.
*Verification:* starting with an unrecognised env key exits non-zero and logs the key; starting with a valid key exits zero and binds.

**FR-17 — Declarative developer environment.**
`devenv.nix`/`devenv.yaml` define the toolchain, local services, processes and tasks (R-DV-03, R-DV-06, R-DV-07). All scaffold/example content is removed. `devenv.lock` is committed (R-DV-05). `devenv.local.*` stay gitignored (R-DV-08).
*Verification:* `devenv shell` on a clean checkout provides every binary referenced by any `package.json` script; `git check-ignore devenv.local.nix devenv.local.yaml` returns true for both; `devenv.lock` is tracked.

**FR-18 — Automatic, reviewable activation.**
`.envrc` resolves `direnvrc` through devenv's **pinned `source_url` plus sha256**, then runs `use devenv` (R-DV-10, R-DV-15). The v3.0.0 form `eval "$(devenv direnvrc)"` computed that path at run time and was unpinned against D-11 — the same defect class as a floating dependency, and invisible to `check:pins` precisely because it was not a package reference. **Corrected in v3.1.0 by ADR-0018.** `devenv hook` is not used (DEC-07): devenv 2.0 provides native shell reloading and states direnv is no longer needed, but the reason to keep it here is reviewability — `direnv allow` is a human trust decision recorded in version control — not capability. The `[whitelist]` bypass is absent (DIR-01); `require_allowed` is set (DIR-02).
*Verification:* after `direnv allow`, a new shell in the root reports the toolchain on `PATH`; leaving the directory unloads it; `.envrc` installs no shell hook; `.envrc` contains no `[whitelist]`.

**FR-19 — Layer enforcement inside a bounded context.**
`dependency-cruiser` (R-BND-04) and ESLint `no-restricted-imports` enforce D-10 in every `teams/*/api`: `adapters → application → domain`; `domain` imports nothing outside `domain`; no `domain` file imports a framework package; no aggregator file imports a database driver or ORM (AC-03).
*Verification:* `teams/banner/api/src/domain/**` importing `@nestjs/common` fails both tools; `teams/web/bff/src/**` importing `pg` fails both tools.

**FR-20 — Shared authorisation format.**
`teams/platform/authz` exports a JSON Schema for authorisation claims and an interface for a policy evaluator (R-META-15). It defines **format only**: no decision logic, no organisation-specific condition expression.
*Verification:* no file in `teams/platform/authz/` contains an organisation-specific condition string; a check asserts the package exports zero executable policy functions.

**FR-21 — Pinned resolution.**
No tracked file contains a floating reference in a build-affecting position: no `latest`, no `^`, no unpinned `http(s)://…` in a federation remote, manifest or lockfile reference (D-11). CI must additionally reject the documented Nix pin-defeating flags `--override-input` and `--no-update-lock-file` (R-NIX-03).
*Verification:* `check:pins` fails on a fixture containing `@latest` and passes on the pinned form. The current tree fails this check; that is the point.

**FR-22 — Reference bounded-context implementation.**
`teams/banner/api` implements the §10.2 layers, with `main.ts` as the only place concrete implementations bind to ports — enforced structurally by the "only `main.ts` may import both a port and its adapter" rule.
*Verification:* the FR-19 rule set passes; a `dependency-cruiser` orphan rule confirms no layer other than `main.ts` imports a port *and* an adapter in the same file.

**FR-23 — Contract production and verification.**
Each bounded context publishes an OpenAPI **3.1** document at `teams/<ctx>/contract/openapi.yaml` (R-META-12). Each aggregator holds a consumer test verifying its provider adapter against the consumer's expectations (R-CDC-01, R-CDC-03). The aggregator may not hand-author the provider schema (D-05).
*Verification:* `contracts:verify` exits zero; an intentional divergence between an adapter expectation and a provider response exits non-zero; a check asserts no file under any aggregator contains a hand-written copy of a provider DTO.

**FR-24 — Reusable CI definitions.**
`teams/platform/ci/` provides versioned reusable workflow definitions referenced by pinned version, never copied (R-OWN-06).
*Verification:* no tracked workflow duplicates the body of a reusable definition.

**FR-25 — Cache-key hygiene.**
Every workspace package declares `outputs` for cacheable tasks (R-BUILD-10). Every environment variable that must invalidate a cache is declared in the task's `env`/`globalEnv` (R-BUILD-02). Where Nx is used, `inputs` are narrowed from the default `["default","^default"]` (R-BUILD-09).
*Verification:* a config checker asserts every cacheable task declares `outputs`, and that no task reads an undeclared env var. Changing a declared var busts the cache in a test run; changing an undeclared one does not — and that test is the regression guard.

**FR-26 — No nested repositories.**
No `.git` directory exists below the repository root.
*Verification:* `find . -mindepth 2 -name .git -not -path './node_modules/*'` returns nothing.

**FR-27 — Single documented toolchain.**
`README.md` documents exactly one package manager, matching `package.json#packageManager`. No second package manager appears in any onboarding document except inside a quoted citation.
*Verification:* repository-wide search for `pnpm`, `npm run`, `yarn` across `*.md` returns matches only on lines marked as citations.

**FR-28 — Task existence.**
Every task declared in `turbo.json` must exist as a script in at least one workspace package, and every deployable package must define `build`, `lint` and `typecheck`.
*Verification:* a checker walks the workspace graph and fails when a declared task resolves to zero packages, or when a deployable lacks a required script. This closes the vacuous-pass hole: a green pipeline must not mean *nothing ran*.

---

## 15. Architecture constraints and their enforcement

An AC with no executable mechanism is a wish.

| ID | Constraint | Enforcement | Blocking check |
|---|---|---|---|
| AC-01 | Permitted dependency graph (§16) | `turbo boundaries` tags (R-BND-01) **and** `dependency-cruiser` (R-BND-04) | `check:boundaries` |
| AC-02 | No bounded context imports another bounded context | `dependency-cruiser` forbidden path | `check:boundaries` |
| AC-03 | No aggregator declares a store, ORM or migration | `dependency-cruiser` forbidden dependency + path rule | `check:bff-purity` |
| AC-04 | One aggregator per client platform, 1:1 | catalog schema (FR-13) | `catalog:validate` |
| AC-05 | Shell thinness (§5.3 disqualifying tests) | ESLint `no-restricted-imports` over `**/client/**` + vocabulary lint | `check:shell-purity` |
| AC-06 | Shell contains no domain rule or API call | ESLint `no-restricted-imports` + `madge` cycle check (R-BND-09) | `check:shell-purity` |
| AC-07 | No cross-team PRs to obtain a fix | metadata co-ownership declaration (D-05) + branch protection | review gate |
| AC-08 | Dependency rule inside a bounded context (D-10) | `dependency-cruiser` layer rules + ESLint (FR-19) | `check:layers` |
| AC-09 | Every deployable refuses to boot on invalid configuration | strict parse at process start (FR-16) | `check:config-strict` |
| AC-10 | No nested Git repository | filesystem check (FR-26) | `check:repo-shape` |
| AC-11 | Cross-team change only via LSC | branch protection + `Owners-Override` trailer check | `check:lsc` |
| AC-12 | Authorisation only in bounded contexts, per request | `spec.authorises: every-request` is a literal; aggregator client-side role checks prohibited by lint | `check:authz-placement` |
| AC-13 | Artefact-side budgets BUD-06 … BUD-09 (§12.2a) | every entry in `catalog/budgets.yaml` names an owner and a blocking check; `check:budgets` reads the YAML and fails with the entry id | `check:budgets` |
| AC-14 | A budget threshold is never asserted in prose | the threshold appears in `catalog/budgets.yaml`; §12.2a states it for reading only | `check:budgets` + quarterly budget review |

**AC-01 is enforced twice on purpose.** `turbo boundaries` is labelled **Experimental** (R-BND-01). Relying on an experimental feature as the single gate for a critical constraint is an unacceptable single point of failure (DEC-14, RISK-11).

---

## 16. Dependency graph (normative)

```
                         ┌───────────────────────────┐
                         │  platform team            │
                         │  @cms/ui  @cms/composition│
                         │  @cms/authz  generator ci │
                         └─────────────┬─────────────┘
                                       │ provides (interfaces 1, 2, 3, 9)
          ┌────────────────────────────┼────────────────────────────┐
          │                            │                            │
┌─────────▼──────────┐      ┌──────────▼─────────┐      ┌───────────▼──────────┐
│ teams/web          │      │ teams/web          │      │ teams/banner         │
│   client/  (shell) │      │   bff/  (aggregator)│      │   client/ (remote)   │
│                    │      │                     │      │   api/    (service)  │
│ consumes 1, 2      │      │ consumes 1,2,3,4    │      │   contract/          │
│                    │      │                     │      │                      │
│ provider 7         │      │ provider 7         │      │ provider 4, 5        │
└─────────┬──────────┘      └──────────┬─────────┘      │ consumes 1, 2, 3, 4  │
          │                            │                └───────────┬──────────┘
          │ consumes 5 (remote)       │ consumes 4 (API)            │
          └────────────────────────────┴─────────────────────────────┘

  PROHIBITED EDGES (each is a `dependency-cruiser` rule, AC-01):
    any client  → any teams/*/api                    (shell must not call a domain API)
    any client  → any aggregator other than its own   (AC-04)
    any bff     → any database driver / ORM / migrations (AC-03)
    teams/X/*   → teams/Y/*          for X ≠ Y        (AC-02)
    domain/     → any framework package                (AC-08)
    any teams/* → any other teams/* directory path   (team-scoped topology, §4.2)
```

The single most consequential edge is `teams/banner/client → banner-api`. A domain UI artefact must call its own context's API and no other context's, and must **never** call an aggregator — otherwise the client becomes a second, unenforced composition tier with no owner (D-06, RISK-01).

### 16.1 Provider/consumer by unit, restated for auditability

| Unit | Provides | Consumes | Never consumes |
|---|---|---|---|
| `teams/web/client` | composition mechanics, chrome, session (rows 7-consumer) | `@cms/ui`, `@cms/composition`, `banner-web` remote | any `teams/*/api`, any other aggregator, any other team's directory |
| `teams/web/bff` | `web-bff` OpenAPI (row 7) | `@cms/ui`, `@cms/composition`, `@cms/authz`, `banner-api` | any database, any `teams/*/client`, any other aggregator |
| `teams/banner/client` | `banner-web` remote (row 5) | `@cms/ui`, `@cms/composition`, `banner-api` | any other `teams/*`, any aggregator |
| `teams/banner/api` | `banner-api` OpenAPI (row 4) | `@cms/authz` | any `client/`, any `bff/`, any other team |
| `teams/platform/*` | rows 1, 2, 3, 9 | nothing | every deployable |

---

## 17. Requirement → enforcement → phase traceability

| Requirement | Enforced by | Phase |
|---|---|---|
| FR-01 | branch protection + `Owners-Override` trailer | PH-1 |
| FR-02, FR-03, FR-04, FR-06, FR-07 | zod strict schemas | PH-2 |
| FR-05, FR-08, FR-09, FR-10 | generator + `git diff --exit-code` | PH-3 |
| FR-11 | branch protection required reviewers | PH-3 |
| FR-12 | templates + local runner | PH-4 |
| FR-13 | catalog schema | PH-2 |
| FR-14 | `turbo boundaries` + `dependency-cruiser` | PH-5 |
| FR-15 | dependency-cruiser + workspace checks | PH-1 |
| FR-16 | strict parse at boot | PH-5 |
| FR-17, FR-18 | devenv + direnv | PH-5 |
| FR-19, FR-22 | dependency-cruiser layer rules | PH-6 |
| FR-20 | lint over `teams/platform/authz` | PH-4 |
| FR-21 | `check:pins` | PH-1 |
| FR-23 | OpenAPI + consumer tests | PH-6 |
| FR-24 | platform CI reuse check | PH-4 |
| FR-25 | cache-config checker | PH-5 |
| FR-26, FR-27, FR-28 | workspace and doc checks | PH-1 |
| AC-01 … AC-12 | §15 | PH-5, PH-7 |
| PERF-01 … PERF-13 | budgets in CI | PH-7, PH-8 |
| RES-01 … RES-10 | timings + telemetry | PH-5, PH-7, PH-8 |

---

## 18. Build phases

**A unit of work may start when the exit criteria of its *declared prerequisites* hold — not when the preceding phase completes.** The phase numbering below documents a dependency graph; it is not a serialisation rule.

The v3.0.0 text was *"Phases are ordered. A phase starts only when the previous phase's exit criterion objectively holds."* Strictly applied that serialises all ten phases, costing roughly four weeks and delaying the first mechanically-caught violation from week ~12 to week 18 — which inverts the programme's own premise. **Corrected in v3.1.0 by ADR-0027**, which is the normative statement of the rule below.

Three constraints make the relaxation safe rather than merely convenient:

1. **PH-1 is a hard serial gate.** No phase starts before PH-1's exit criterion holds (one lockfile, no nested `.git`, no duplicate package names). Workspace truth is the one thing every later phase assumes and cannot independently establish.
2. **The overlap set is closed.** Exactly these four pairs may run concurrently: PH-4 ∥ PH-3 (templates consume the catalogue, not the generator's output); PH-5 ∥ PH-3 and PH-4 (environment work touches `devenv.nix`, not `catalog/`); PH-7 ∥ PH-6 (checks are static analysis; the reference implementation is merely what they analyse); PH-10 drafting ∥ PH-9 (documentation describes artefacts that exist from PH-3 onward). Anything not listed is serial by default, and **adding a pair is an amendment to ADR-0027, not a scheduling decision.**
3. **Two exclusions are decisions, not omissions.** PH-9 may not precede PH-3 — the generator emits the `CODEOWNERS` and boundary configuration for the new topology, so relocating first means hand-maintaining both. PH-8 may not precede PH-7 — a budget with no enforcement gate is a wish (§15).

The prerequisite edges themselves are declared in `IMPLEMENTATION-PLAN.md` §5 as `D-1 … D-7`. That list is load-bearing: an entry that is wrong is a scheduling defect, not a documentation typo, and editing it requires the ADR-0027 amendment path.

### PH-1 — Workspace truth
**Work:** extend `workspaces` to `teams/*/*` per FR-15; delete per-package lockfiles (RES-01) and any nested `.git` (FR-26); namespace-qualify every package name; consolidate to the root lockfile; correct `README.md` per FR-27; add missing `lint`/`typecheck` scripts (FR-28); remove scaffold content; establish branch protection with required reviewers (FR-11) and the LSC rule (FR-01, AC-11).
**Exit:** exactly one lockfile at the root; `find . -mindepth 2 -name .git` returns nothing; no two workspace packages share a name; `turbo run typecheck` executes in every package (count > 0, asserted by the checker); a cross-team PR without `Owners-Override` is rejected.

### PH-2 — Metadata layer
**Work:** `catalog/schema/*.schema.ts` (FR-02); `apiVersion`/`kind`/`id` discipline (FR-03); team types (FR-04); relations (FR-07); seed `platform`, `banner`, `web` teams; `banner` context; `web`, `mobile`, `desktop` clients; cardinality (FR-13).
**Exit:** `catalog:validate` exits zero; an unknown key, a dangling relation, two overlapping ownership entries and a two-aggregator client each exit non-zero with a precise message.

### PH-3 — Generator
**Work:** `teams/platform/generator` emitting all §4.4 outputs including §7.2 ownership resolution.
**Exit:** `catalog:generate && git diff --exit-code` is clean; the FR-05, FR-08, FR-09 and FR-10 verifications pass.

### PH-4 — Scaffolding and platform contracts
**Work:** `teams/platform/templates/` (FR-12); `teams/platform/ci/` (FR-24); `teams/platform/authz` (FR-20).
**Exit:** each template yields a unit passing `typecheck`, `lint` and `turbo boundaries` with zero manual edits; the authz package exports zero policy functions.

### PH-5 — Environment, configuration and cache hygiene
**Work:** real `devenv.nix`/`devenv.yaml` with pinned inputs and committed `devenv.lock` (FR-17); `.envrc` per DEC-07 with `require_allowed` and no `[whitelist]` (FR-18); `secretspec.toml` (FR-19 analogue); per-deployable `config.schema.ts` (FR-16); cache-key hygiene (FR-25).
**Exit:** `devenv shell` boots the full local stack in ≤ 300 s cold and ≤ 10 s warm; `direnv allow` then entering the directory yields a ready shell; an invalid env var terminates the process at startup non-zero; a cache-bust test proves a declared env var invalidates and an undeclared one does not.

### PH-6 — Reference bounded context and aggregator
**Work:** layer `teams/banner/api` per §10.2 with FR-19 rules; `teams/banner/contract/openapi.yaml`; consumer tests (FR-23); implement `teams/web/bff` per D-02 with AC-03 purity; **frontend observability must be in place before a second remote exists** (§11.4).
**Exit:** FR-19 and FR-22 verifications pass; `contracts:verify` exits zero; the aggregator declares no database dependency and no `migrations/`; OpenTelemetry browser instrumentation is present.

### PH-7 — Boundary and shell purity enforcement
**Work:** wire `dependency-cruiser`, the shell-purity `no-restricted-imports` rule, `madge`, the authz-placement rule, and the generated `turbo.json` boundaries block.
**Exit:** every `check:*` script in §15 passes; four seeded violations — shell→API, domain→framework, aggregator→`pg`, cross-team import — each fail and are reverted in the same commit.

### PH-8 — Performance and resource enforcement
**Work:** wire `size-limit`/Lighthouse budgets (PERF-02, PERF-13); assert `remoteEntry.js` size (PERF-03); assert `shareStrategy: 'loaded-first'` and `disableAssetsAnalyze` absent (MF-1, MF-2, PERF-04); singleton instance assertion (PERF-05); aggregator timeout budgets, circuit breakers, bulkheads, retry budget (PERF-06, PERF-09); per-request loaders (PERF-08); cache key-versioning and request coalescing (PERF-11); event-loop lag metric (PERF-10); container requests/limits (PERF-12); CI cache-key checks (FR-25); dev-server RSS baseline collection (RES-07).
**Exit:** a deliberately oversized route fails PERF-02; a deliberately un-pinned remote fails FR-21; a shared-module duplication fails PERF-05; the dev-server RSS baseline exists with 3 recorded data points.

### PH-9 — Relocation to the team-scoped topology
**Work:** move each deployable under its owning team's directory per §4.1; fold duplicate Module Federation hosts into the single shell; relocate the design system to `teams/platform/ui`; pin all federation remotes (D-11); wire `teams/web/bff` into `teams/web/client`.
**Exit:** `apps/`, `bff/`, `packages/` and `composition/` do not exist; exactly one Module Federation host exists in the repository; `check:pins` exits zero; `check:catalog` exits zero.

### PH-10 — Documentation and decision records
**Work:** `docs/adr/0001`–`0012`; `docs/getting-started.md`; generated `docs/ownership.md`.
**Exit:** a developer with no prior context completes a local run using only `docs/getting-started.md`, with no clarification from the author; every ADR cites at least one `R-xx` from `docs/references.md`; `docs/references.md` contains no URL that 404s.

---

## 19. Risks

| ID | Risk | Impact | Mitigation | Residual |
|---|---|---|---|---|
| RISK-01 | Micro-frontending confers no browser security boundary; a remote executes with host privileges | Compromise of one domain UI artefact compromises the whole admin session | D-06 per-request authorisation in every bounded context; AC-05/AC-12 keep shells and aggregators free of domain code; CSP allow-listing remote origins (R-MFE-16) as supply-chain control | Accepted and documented |
| RISK-02 | Shared React singleton across independently deployed remotes causes version skew | Progressive breakage as remote count and deploy frequency grow | MF-5 (`singleton` + `requiredVersion`, R-MF-03); PERF-05 asserts exactly one instance | Accepted; revisit at 5+ remotes |
| RISK-03 | Aggregator accumulates business rules and becomes an unowned domain | Duplicate ownership of rules; two teams editing the same behaviour | §6.2 disqualification tests are mechanical; AC-03 purity checks | Low |
| RISK-04 | Generated files hand-edited, silently diverging from metadata | Metadata stops being authoritative; G-04 lost | FR-10 CI diff + `@generated` markers; §7.1 row 9 makes this a contract violation | Low |
| RISK-05 | `turbo boundaries` is Experimental and its semantics change | Silent enforcement gap | FR-14 + FR-19 give two independent mechanisms (R-BND-01); DEC-14 | Low |
| RISK-06 | An aggregator accumulates rules that are then duplicated into a second aggregator | Two implementations of one domain rule, drifting | T2 detection in §6.2; §6.3 step 7 requires an ADR, and a rule extracted **twice** is flagged as a boundary error | Low |
| RISK-07 | An aggregator exists with no client consuming it, or three aggregators before a second client | Unmaintained surface | NG-02 limits implementation to `teams/web/bff`; FR-13 makes the others a one-file metadata change | Low |
| RISK-08 | `devenv` package availability lags a language release | Blocked onboarding | `devenv.local.yaml` permits per-developer pinning without forking `devenv.yaml` (R-DV-08) | Low |
| RISK-09 | Three client platforms declared, one implemented | Discovery assumes parity | NG-02 and §8.2 make `shell`/`bff` presence declarative rather than directory-derived | Low |
| RISK-10 | A pinned version goes stale and never gets upgraded | Missed security patch | Pinning is paired with scheduled Dependabot/Renovate runs opening version-bump PRs (R-BUILD-32, R-BUILD-33). This also covers the deliberate OpenAPI 3.1.x pin | Low |
| RISK-11 | `dependency-cruiser` rules are bypassed by an unlisted alias or path form | Enforcement gap | FR-19 pairs dependency-cruiser with ESLint `no-restricted-imports`, which resolves through the module resolver rather than raw paths | Low |
| RISK-12 | Ownership entries overlap after a directory move; the conflict surfaces only at review | Ambiguous accountability | FR-06 fails validation at merge time, naming both teams | Low |
| RISK-13 | **The monorepo fails for organisational reasons, not technical ones** | Platform team becomes the bottleneck; boundary enforcement decays | SPL-02 makes tooling-budget loss an explicit re-evaluation trigger rather than a slow slide. The "monorepo is terrible if you're not good at it" failure is silent (R-MONO-26), so SPL-02's trigger is deliberately leading-indicator-based (missed SLOs), not lag-based | Medium — accepted with a named trigger |
| RISK-14 | **LSC is used to erode boundaries** — every cross-team change becomes an LSC | AC-01 becomes nominal | AC-11 requires a non-author approver and a merge-commit trailer; SPL-05 treats >2 denials in a quarter as a *boundary* problem, not an enforcement problem | Medium — accepted with a named trigger |
| RISK-15 | **Performance budgets become stale relative to the Web Almanac baseline** | Budgets drift from reality; either too loose to catch regressions or too tight to ship | RES-10's unit-economics metric and a scheduled review of R-PERF-15/R-PERF-16 each quarter. Budgets are re-baselined deliberately, never silently | Low |
| RISK-16 | **A claimed performance improvement is asserted without a measurement** | False confidence; the number is repeated until it becomes folklore | §12.3 lists explicitly what this PRD does *not* claim, and RES-07 mandates measurement instead of assertion (R-BUILD-19, R-BUILD-40, R-BE-01) | Low |
| RISK-17 | **Node fan-out turns out to be CPU-bound, not I/O-bound** | Aggregator latency degrades non-linearly under real traffic | PERF-06 (p99) and PERF-10 (event-loop lag) exist to falsify the assumption early. Worker threads (R-BE-11) are the recorded remedy | Low |

---

## 20. Decision log

Every question raised during design is closed here. A decision is not reopenable without a superseding entry.

| ID | Question | Decision | Basis |
|---|---|---|---|
| DEC-01 | Is the repository boundary an architectural input? | **No.** Ownership, versioning, deployment and repository are four separable boundaries (R-MONO-06, R-MONO-08, R-MONO-10). Team Topologies never made repo topology an architectural force (R-MONO-01 … R-MONO-05). Repository topology is derived from B1 and B3 | §1 |
| DEC-02 | One repository, or many? | **One**, as the default output of B1+B3, **conditional** on SPL-01 … SPL-05. Not permanent; exit is designed, not improvised | §1.3, §4.5 |
| DEC-03 | Layer-scoped or team-scoped top-level directories? | **Team-scoped.** One team, one top-level directory. This makes ownership resolution total and order-free, and eliminates v2.0.0's glob-precedence algorithm | §4.2, R-MONO-13 |
| DEC-04 | Is `apps/web/customer` a second client platform? | **No.** "customer" is a persona, not a runtime. Any persona axis is prohibited | D-01 |
| DEC-05 | Which bounded context receives Clean Architecture? | `banner` only, as a reference implementation. Blanket adoption is speculative | NG-08; §10.1 |
| DEC-06 | Are micro-frontends adopted for isolation? | **No.** For deployment independence and team autonomy only. Isolation is never claimed and must not appear in any design justification | R-MFE-15, R-MFE-16 |
| DEC-07 | `direnv` or `devenv hook` for activation? | **direnv** (`.envrc` + `use devenv`). direnv's explicit `direnv allow` step is a reviewable trust decision; a shell hook mutates the environment invisibly. Upstream now recommends `devenv hook` for most workflows (R-DV-10); it is rejected here on reviewability grounds and revisited only if onboarding friction is measured to exceed RISK-08's tolerance | D-08, R-DIR-01 |
| DEC-08 | Can a shell hold domain logic? | **No.** AC-05 and AC-06 enforce §5.3's three disqualifying tests mechanically | §5 |
| DEC-09 | "Aggregator" or "BFF"? | **`aggregator` is normative**; "BFF" is retained only in §7.1 and in citations. One term per concept, so §6.2's tests stay testable | D-02 |
| DEC-10 | Floating remote versions? | **Prohibited.** Every build-affecting reference is pinned, paired with a scheduled upgrade PR | D-11, G-05, RISK-10 |
| DEC-11 | GraphQL federation instead of a hand-rolled aggregator? | **Not in v3.0.0.** The aggregation tier is required regardless; federation is one implementation. A composition tier is itself a resource cost — Apollo ships a Rust-native planner and bounded incremental-planning knobs for exactly that reason (R-AGGR-09, R-AGGR-10) | §6.4 |
| DEC-12 | Where does authorisation live? | In every bounded-context service, on every request. Never in a shell or aggregator | D-06, R-MFE-15 |
| DEC-13 | Is the Team API normative? | **No.** There is no official Team API specification. `teamapi.dev` is third-party and unaffiliated (R-TTA-01). The catalog is Backstage-*compatible* (R-META-07, R-META-09), not Backstage-*governed* | R-TTA-01, R-TT-02 |
| DEC-14 | Gate on one boundary tool or two? | **Two.** `turbo boundaries` + `dependency-cruiser`/ESLint. Gating a critical constraint on a feature labelled **Experimental** is an unacceptable single point of failure | RISK-05, R-BND-01 |
| DEC-15 | Imperative or declarative composition registration? | **Declarative**, generated from `catalog/` | D-07, R-META-03 |
| DEC-16 | Is SOLID enforced inside a layer? | **No.** Only at layer boundaries. §10.1's guard is grounded in Martin's own qualification (R-SOLID-08) and in Big Ball of Mud (R-SOLID-10) — **not** in the widely-circulated and non-existent "SOLID Considered a Harmful" (R-SOLID-09) | §10.1 |
| DEC-17 | Do green tasks prove correctness? | **No.** FR-28 asserts every declared task resolves to at least one package, closing the vacuous-pass hole | FR-28 |
| DEC-18 | Which Module Federation defaults do we override? | MF-1 … MF-5 and MF-4a … MF-4d in §11.3: `shareStrategy: 'loaded-first'`, `externalRuntime`, **`disableShared` off**, `disableRemote` on remotes, **`disableSnapshot` true in prod**, **`provideExternalRuntime` on the shell**, `contenthash` filenames, pinned remotes, a fallback runtime plugin, and a generated registry | R-MF-08, R-MF-12, R-MF-14, R-MF-15 |
| DEC-19 | What is the default provider scope? | **Singleton.** Request/transient scope requires an ADR naming the reason and the measured cost | NEST-01, R-BE-03 |
| DEC-20 | Do we assert bundler memory or build cache numbers? | **No.** We assert only measured values. RES-07 and RES-08 mandate measurement; §12.3 lists what this PRD explicitly does not claim | R-BUILD-19, R-BUILD-40, R-BE-01 |
| DEC-21 | How does a cross-cutting change get made? | **LSC** (FR-01, AC-11), modelled on Chromium's Large Scale Changes process, with a second non-author approver and an `Owners-Override` trailer | R-MONO-40, RISK-14 |
| DEC-22 | Which OpenAPI version? | **3.1.x**, pinned deliberately. The live latest is 3.2.1 (R-META-13); tracking latest would let a spec minor change validation semantics under the contract suite | D-11, RISK-10 |
| DEC-23 | Where does the design system live? | `teams/platform/ui`, owned by the Platform team, semver with a two-release deprecation window | §7.1 row 1 |
| DEC-24 | Do we adopt CUE for the catalog? | **No.** CUE's unification of schema and instance is attractive (R-META-17, R-META-18), but zod gives static type inference into the generator at no extra tool, and JSON Schema remains the portable fallback (R-CFG-04). Revisit if a second consumer needs the catalog without a JS runtime | R-META-17 |
| DEC-25 | Are bounded contexts integrated asynchronously (event streams, sagas, scheduled jobs)? | **No, in v3.0.0 and v3.1.0.** Synchronous request/response only; the aggregator composes at request time. Recorded as a decision rather than left implicit, because "no asynchronous integration" is a constraint someone will otherwise read past. **Revisit trigger:** a second bounded context exists *and* a declared requirement needs decoupling the aggregator from request latency. Until both hold, adding it is out of scope (ADR-0025) | §2.2 NG-01 |

---

## 21. Definition of done

v3.1.0 is complete when all of the following are objectively true:

1. PH-1 through PH-10 exit criteria all hold.
2. Every FR-01 … FR-28 verification procedure executes and passes.
3. Every PERF-01 … PERF-13 threshold is met and measured in CI.
4. Every RES-01 … RES-10 threshold is met and measured.
5. Every AC-01 … AC-12 has a named mechanism present in the `check:*` scripts **and** a seeded violation proving it fails.
6. `catalog:validate && catalog:generate && git diff --exit-code && turbo boundaries && dependency-cruiser && check:docs` exits zero on a clean tree.
7. Every record in `docs/adr/` exists and each cites at least one `R-xx` from `docs/references.md`. The set's size and membership are read from [`adr/README.md`](adr/README.md), not restated here.
8. No item in §2.2 (non-goals) has been implemented.
9. `docs/references.md` contains no URL that 404s; §12.3's "honest limits" table is still accurate — any claim added since must have a measurement behind it.
10. Every SPL-01 … SPL-05 trigger has been evaluated at least once, in writing, and the result recorded.
11. **Every `TDD.md` §14 `GAP-nn` is closed by an accepted ADR, or appears in this section as an explicitly unresolved entry with a named owner.** A gap that is neither is a defect in this document, not in `TDD.md`.
12. **Where an accepted ADR supersedes text in this PRD, the ADR wins**, and this PRD carries the amendment at its next version. Superseded text is corrected forward; it is not left in place for the ADR to contradict.
13. `check:docs` reports no error-severity finding, and **every check it implements has a fixture that makes it fail**, committed in the same change that adds the check.

### 21.1 Why items 11–13 exist

v3.0.0 was written against a twelve-record ADR scope and its ten completion criteria contained no clause for the `GAP-01 … GAP-14` closures. An implementer working this section's own acceptance gate therefore had **no signal that fourteen accepted corrections existed** — three of which change shipped configuration defaults (`MF-4`, `PERF-03`, `externalRuntime`) and one of which invalidates an unpinned snippet in §9. The same defect recurred inside the ADR set itself: the amendment proposed to fix the ADR range named `0026` when the set had already reached `0027`.

Item 11 prevents the first. Item 12 prevents the second by fixing precedence rather than relying on every future correction being written carefully. Item 13 (ADR-0028) is the mechanism: a fact that can be computed from another file has one owner, and every other mention of it is generated or mechanically checked.

---

## 22. Key references

The complete, fetch-verified catalogue is `docs/references.md` (REF-CMS-001 v3.1.0) — **405** admissible references (381 clean VERIFIED, 24 PARTIAL with a stated limitation), **79** rejected URLs that must never be cited, and 15 attribution corrections that must be carried wherever they appear.

| Used for | References |
|---|---|
| Team types, interaction modes, cognitive load, platform as a product | R-TT-01 … R-TT-16, R-TTA-01, R-TTA-02 |
| **"Repo topology is not a TT architectural force"** | R-MONO-01 … R-MONO-05 |
| **Repository / deployment / ownership boundaries are separable** | R-MONO-06 … R-MONO-08, R-MONO-10, R-MONO-11, R-MONO-13 |
| Evidence for monorepo (Microsoft, Google, peer-reviewed) | R-MONO-14 … R-MONO-25 |
| Evidence for polyrepo and the organisational-readiness risk | R-MONO-26 … R-MONO-37 |
| **Monorepo + hard ownership + escape hatch (Chromium)** | R-MONO-38 … R-MONO-43 |
| Monorepo adoption data (and its limits) | R-MONO-44 |
| Bounded context, aggregate, ubiquitous language, context map | R-DDD-01 … R-DDD-04 |
| SOLID, primary sources | R-SOLID-01 … R-SOLID-08, R-SOLID-10 |
| **Rejected and never citable** | R-SOLID-09 · R-MONO-09 · R-MFE-21 · R-MFE-22 · R-MFE-23 · R-BE-22 · R-BND-11 · R-BUILD-19 · R-BUILD-40 |
| Clean Architecture, hexagonal, layering | R-CA-01 … R-CA-06 |
| Metadata-driven composition, catalog, relations, OpenAPI/AsyncAPI | R-META-01 … R-META-25 |
| Developer environment (devenv, Nix, direnv, alternatives) | R-DV-01 … R-DV-14, R-NIX-01 … R-NIX-08, R-DIR-01 … R-DIR-09 |
| Secrets | R-SCRT-01 … R-SCRT-07 |
| Aggregator / BFF / gateway / anti-patterns | R-BFF-01 … R-BFF-27 |
| GraphQL federation (recorded, not adopted) | R-AGGR-01 … R-AGGR-11 |
| Contract testing and provider/consumer contracts | R-CDC-01 … R-CDC-10 |
| Resilience, caching, aggregation latency, N+1 | R-RES-01 … R-RES-28 |
| Micro-frontends, container application, anti-patterns, security | R-MFE-01 … R-MFE-20 (R-MFE-21, R-MFE-22 and R-MFE-23 are rejected) |
| Module Federation configuration and its performance numbers | R-MF-01 … R-MF-20 |
| Web performance budgets and metrics | R-PERF-01 … R-PERF-23 |
| Backend resource efficiency (Node.js, NestJS) | R-BE-01 … R-BE-21 (R-BE-22 is rejected) |
| Build and CI resource efficiency | R-BUILD-01 … R-BUILD-44 |
| Boundary enforcement | R-BND-01 … R-BND-10 (R-BND-11 is rejected) |
| Configuration validation | R-CFG-01 … R-CFG-04 |
| Ownership and governance | R-OWN-01 … R-OWN-06 |
| Cost allocation and runtime resource management | R-COST-01 … R-COST-09 |
