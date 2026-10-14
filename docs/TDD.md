# TDD — Technical Design for PRD-CMS-001

| Field | Value |
|---|---|
| Document ID | TDD-CMS-001 |
| Version | 1.0.0 |
| Status | Proposed — supersedes nothing; normative detail *under* PRD-CMS-001 v3.0.0 |
| Date | 2026-10-14 |
| Consumed by | `docs/PRD.md` (PRD-CMS-001 v3.0.0), `docs/references.md` (REF-CMS-001 v3.0.0 + R-25 addendum) |
| Scope | The *design* layer the PRD deliberately leaves open: concrete artefacts, algorithms, contracts, resource budgets and the mechanical separation of **application composition** from **UI business domain** and of **aggregator** from **bounded context**. |

### 1. Relationship to the PRD — and what this document may and may not do

The PRD is a **requirements** artefact. It states *what* must be true and *why*, each claim tied to a verified reference. It deliberately does not specify *how*, because "how" is what a design must fix, deterministically, before PH-1 begins.

| Layer | Owns | Change requires |
|---|---|---|
| **PRD** (`PRD.md`) | Goals, constraints, requirements, budgets, risks, decisions | A superseding version + re-verified evidence |
| **TDD** (this document) | Artefacts, schemas, algorithms, contracts, ownership ledger, budget ledger, check inventory | A superseding version; may not contradict the PRD |
| **ADR** (`docs/adr/`) | One irreversible choice + its reversal cost | Two named approvers |

**This document may not weaken a PRD requirement.** Where the PRD is silent, this document decides. Where the PRD is *self-inconsistent*, this document records the inconsistency in §14 (Gaps), proposes the minimal resolution, and marks the resolution as **requiring an ADR**. Nothing here silently overrides the PRD.

### 2. Reading convention

Every normative statement carries an identifier. A sentence without one is explanatory and binds nothing.

| Prefix | Meaning | Obligation |
|---|---|---|
| `D-nn` | Design definition — a term fixed for the rest of the document | Binding |
| `ALG-n` | Algorithm — total, terminating, side-effect-free specification | Binding; must be executable as written |
| `SCH-n` | Schema / contract artefact specification | Binding |
| `BND-n` | **Plane** separation rule | Binding; one mechanical check each |
| `ROW-n` | Ownership-ledger row (refines PRD §7.1) | Binding |
| `BUD-n` | Budget ledger entry (refines PRD §12–13) | Binding |
| `CHK-n` | Verification gate | Binding; exit code + seeded fixture |
| `GAP-n` | Inconsistency or hole found in the PRD | Requires ADR |
| `ADR-nn` | Decision record this document requires | Must exist before the cited phase exits |
| `R-xx` | Evidence in `docs/references.md` | Evidence |

**There are no open questions in this document.** Every design question is answered here or listed in §14 with a decision attached.

### 2.1 Coverage map — the seven architecture views

The standard architecture views, mapped to where each is specified. The right-hand column records the state **at v1.0.0 before §18–§24 were added**, because a coverage claim that has never been audited is not a claim.

| # | View | Specified in | State before §18–§24 | Now |
|---|---|---|---|---|
| 1 | **Solution architecture** — components and how they relate | §4 planes, §5, §6, §7 ledger | **Covered** — planes, boundary rules, ownership | §18 adds the component catalogue, runtime topology and the three end-to-end request walks |
| 2 | **Integration design** — communication flows, APIs, data exchange | §5.4, §6.4, §8, §10.5 | **Partial** — aggregator lifecycle, federation, tracing; no protocol/envelope/contract-lifecycle spec | §19 |
| 3 | **Data design** — structures, models, processing flows | §7 only ("one store per bounded context") | **Missing** — no logical model, no schema-evolution rules, no PII/retention, no write/read path | §20 |
| 4 | **Technology stack** — framework, platform, technology choices | scattered (NG-11, MF-*, R-*) | **Missing as a view** — choices existed only as citations, with no pin, no rejected alternative, no revisit trigger | §21 |
| 5 | **Security design** — authN, authZ, encryption, controls | §5.5 (D-05), §10.1–10.2 (CSP note) | **Partial** — authorisation boundary and identity forwarding were solid; authentication flow, encryption, threat model and controls were not | §22 |
| 6 | **Deployment architecture** — environments, infrastructure, scalability, availability | §11.3 cost centres only | **Missing** — NG-04 excludes *provisioning*, which was mistaken for excluding the deployment design itself | §23 |
| 7 | **Detailed technical design** — module specs as implementation guides | §9 (BC internals), §8.2 (pipeline), §13 (checks) | **Partial** — the bounded context and the generator were specified; the shell, federation builder, aggregator pipeline and check harness were not | §24 |

Two of these omissions were substantive, not cosmetic:

- **Deployment design is not provisioning.** PRD NG-04 excludes creating infrastructure; it does not exclude deciding what is deployed, in what order, with what availability target, scaled on what axis. Without §23 the budgets in §11 have nothing to attach to.
- **Security design is not authorisation placement.** The PRD places authorisation correctly (D-06) but never specifies how a session is established, how a bounded context verifies a caller, or what happens when a remote is compromised. §22 closes that.

---

## 3. Design determinism

The PRD's stated ambition is that the architecture be *derived*, not chosen. This section makes "deterministic" a checkable property rather than an adjective.

### D-01 — Four determinism classes

| Class | Property | Falsifier | Verified by |
|---|---|---|---|
| **D1 — Schema** | The same catalog bytes always produce the same generated bytes | `catalog:generate` twice in a row leaves a diff | CHK-07 |
| **D2 — Validation** | Validation is total, terminating, and reports every violation, sorted | Two runs produce byte-identical stderr; exit code is always 0 or 1 | CHK-08 |
| **D3 — Build** | Build output is a function of the commit alone | `pins:check` fails on any floating reference | CHK-10 |
| **D4 — Runtime** | Runtime behaviour is *budgeted*, not byte-reproducible | p99 latency, event-loop lag and retry rate stay inside BUD entries | CHK-20, CHK-21 |

D1–D3 are hard: a violation is a defect. D4 is a budget: exceeding it opens an incident, it does not break a build. Conflating the two is how performance requirements decay into aspirations.

### 3.1 The byte-stability rules that make D1 true

Generated artefacts are committed to the repository, so their content is diffable. That makes byte-stability a design obligation, not a nicety:

- **S1.** All emitted files use LF endings, UTF-8, no BOM, final newline.
- **S2.** Object keys are emitted in a fixed order (schema declaration order, never alphabetical-by-accident and never insertion order of a hash map). Maps are sorted by key wherever the schema has no declared order.
- **S3.** No generated file contains a timestamp, hostname, absolute path, user name, process id, or run duration.
- **S4.** Every emitted path is repository-relative and POSIX-normalised.
- **S5.** Every generated file begins with exactly one marker line containing the literals `@generated` and `do not edit` (extends PRD FR-10 from "a comment" to "exactly one line, first line").
- **S6.** The generator writes files atomically (temp file + rename) and never rewrites a file whose content is unchanged (mtime stability — this keeps `turbo` inputs from being invalidated by a no-op regeneration).
- **S7.** The generator is a pure function of `catalog/**` plus the checked-in templates. It reads no network, no clock, no environment.

> S3+S4 are what make `catalog:generate && git diff --exit-code` (PRD FR-05) a meaningful gate. Without them the gate fails on every run for reasons unrelated to drift.

### 3.2 Error reporting contract

```
catalog:validate   exit 0  clean
                   exit 1  one or more violations
                   exit 2  internal error (schema missing, unparseable YAML, I/O)
```

- Human form goes to stderr; machine form (`--format=json`) to stdout. The JSON is an array of `{ code, file, keyPath, message, docs }`, sorted by `(file, keyPath)`, `docs` naming the PRD clause it enforces.
- Violations are **never** fail-fast: all are reported in one run. A developer must not discover ten schema errors one run at a time.
- Exit code 2 is reserved for "the tool could not judge", which is operationally distinct from "your metadata is wrong". A pipeline must not treat exit 2 as pass.

---

## 4. Solution overview — three planes

The PRD names four unit kinds (shell, aggregator, bounded-context service, domain UI artefact). This design arranges them into **three planes** with a strictly one-way interaction order. This is the single organising idea of the design, and it is what makes both of the user's requested separations mechanical instead of rhetorical.

```
   ┌──────────────────────────────────────────────────────────────────┐
   │ PLANE A — PRESENTATION COMPOSITION            owner: web team     │
   │                                                                  │
   │   teams/web/client/   (shell: route map, remote registry,        │
   │                              session bootstrap, chrome,           │
   │                              per-remote error boundary)          │
   │        │  mounts only                                          │
   │        ▼                                                       │
   │   domain UI artefacts — owned by bounded-context teams          │
   │        (these are PLANE B, but are *mounted* by Plane A)         │
   └──────────────────────────────────────────────────────────────────┘
                    │ Plane A may never call Plane B's APIs.
                    │ Plane B may never call Plane A.
                    │ (except: a domain UI artefact may call *its own*
                    │  context's API — that is intra-Plane-B)
   ┌──────────────────────────────────────────────────────────────────┐
   │ PLANE B — BUSINESS DOMAIN                     owner: each CT team │
   │                                                                  │
   │   teams/<ctx>/client/  ──consumes──▶  teams/<ctx>/api           │
   │   teams/<ctx>/api       ──provides──▶ OpenAPI 3.1 (contract/)    │
   └──────────────────────────────────────────────────────────────────┘
                    │
                    ▼  consumed by
   ┌──────────────────────────────────────────────────────────────────┐
   │ PLANE C — RESPONSE COMPOSITION               owner: web team      │
   │   teams/web/bff/   (fan-out, shaping, deadlines, partials)       │
   │   owns no store, no rules, no state between requests             │
   └──────────────────────────────────────────────────────────────────┘
```

### BND-1 — Plane order is total

Plane A → Plane C → Plane B is permitted **only** where the route is declared `composed` (§6). Plane A → Plane B directly is **prohibited** (PRD §16). Plane C → Plane B is the aggregator's only outbound direction. Plane B → Plane B (context-to-context) is prohibited by AC-02.

### BND-2 — No plane may be silently merged into another

Merging Plane A into Plane B produces a shell with domain logic (PRD DEC-08 / RISK-01). Merging Plane C into Plane B produces the unowned domain of RISK-03 / T2. Merging Plane C into Plane A produces a client-side composition tier with no owner. Each merge is caught by a named check, listed in §13.

### D-02 — Why planes and not "layers"

A *layer* is a property of a source tree. A *plane* is a property of an ownership boundary plus a runtime boundary. The PRD's `D-10` dependency rule governs layers; this document adds that planes must also be separately ownable, separately deployable (PRD B3) and separately enforceable. A unit that straddles two planes fails the architecture, not the style guide.

---

## 5. Application composition layer vs UI business domain

The PRD (§5) states the distinction and gives three disqualifying tests. This section makes them **executable** and closes two holes: what data each side may fetch, and how a name crosses the boundary without leaking vocabulary.

### 5.1 The capability matrix, restated as typed capability

Each side gets a *type* in `@cms/composition`. The matrix below is simultaneously documentation and a compile-time contract.

| Capability | Composition layer (`teams/<client>/client/`) | UI business domain (`teams/<ctx>/client/`) | Enforced by |
|---|---|---|---|
| `RouteSegment` | **owns** the opaque string | receives it, cannot construct one | `OpaqueRouteSegment` branded type |
| `RemoteHandle` | **owns** the registry entry | receives a mounted element | `MountedRemote` branded type |
| `SessionSummary` | **owns** (`who am I, what may I see as chrome`) | receives display fields only | DTO shape in `@cms/composition` |
| Domain entity, aggregate, rule | never | **owns** | AC-05, §5.3 tests |
| Domain API client | never | **owns**, for its own context only | AC-05 + generated client |
| Business validation | never | **owns** | vocabulary lint |
| Persistent client state | never | view state only | not enforceable; review |
| Provider URL / remote id | **owns** | never knows | generator: remotes registry only in shell |
| Federation protocol types | via `@cms/composition` | via `@cms/composition` | AC-02 on package graph |
| Error boundary | **owns**, one per remote | may own sub-boundaries *inside* its own area | generated from `errorBoundaries` |

### 5.2 D-03 — The three disqualifying tests, as an executable rule

PRD §5.3 gives three tests. They are re-expressed here as an ordered procedure with a single outcome, because a module must be placed exactly once, not "probably".

```
ALG-1  place-module(module M, owningTeam T)
 1  if M imports any package tagged `ctx-api`          → FAIL  (rule 2)
 2  if M imports any package tagged `client-peer`      → FAIL  (rule 3)
 3  if M contains an identifier drawn from a domain's ubiquitous language
      (catalog/contexts/<ctx>.spec.language ∩ M's exported identifiers) ≠ ∅
                                                           → FAIL  (rule 4)
 4  if M holds state that survives navigation of the domain's entity set
                                                           → FAIL  (rule 1)
 5  if M's behaviour changes when a bounded context is removed
      (i.e. deleting contexts/<ctx>.yaml changes M's logic, not its config)
                                                           → FAIL  (rule 2')
 6  return the owning bounded context named by the intersecting language
```

Step 3 is the only one that is *mechanical* and it is the load-bearing one: the ubiquitous language is already declared in `catalog/contexts/*.yaml#spec.language` (PRD §8.2). A shell module that exports `Banner`, `BannerPlacement`, `rotationWindow`, or any other seeded term has crossed the line, regardless of intent. This turns a review convention into a lint.

Rule 4 is enforced as: every identifier exported from `**/client/**` must appear in exactly one of three vocabularies — the composition vocabulary (`RouteSegment`, `RemoteHandle`, `SessionSummary`, `ChromeSlot`, `ErrorBoundary`, …) or a bounded context's declared language. An identifier in neither list fails the check and must be added to exactly one list. **This makes the vocabulary total**: there is no place for a new word to hide.

### 5.3 D-04 — The data-access question the PRD does not answer

The PRD forbids the shell from calling any bounded-context API (AC-05) and forbids a domain UI artefact from calling an aggregator (RISK-01). It never states **when the aggregator is in the request path at all**. Left open, three outcomes are all "compliant", and teams will pick differently:

1. every read goes direct remote → context API, and the aggregator is dead code;
2. every read goes through the aggregator, and each domain UI artefact now talks a DTO shaped for a page rather than for its domain;
3. a mix, decided per pull request.

Outcome 3 is the expensive one: two serialisation vocabularies for the same data, and a rule that depends on who wrote the route.

> **D-04 — Every route declares a data strategy, and the strategy is constrained by the route's own metadata.**

| `route.dataStrategy` | Legal iff | Data path | Aggregator involved |
|---|---|---|---|
| `none` | route has no `context` | shell → aggregator for chrome/session only | yes, chrome endpoints only |
| `direct` | route declares **exactly one** `context` | domain UI artefact → **its own** context API | **no** |
| `composed` | route declares **≥ 2** contexts, **or** declares `clientShape` | shell → aggregator → N context APIs; each domain UI artefact receives its section as props | yes |

Validation rules, all enforced by `catalog:validate`:

- `direct` with `contexts.length ≠ 1` → **error**.
- `composed` with `contexts.length < 2` and no `clientShape` → **error** (a one-context "composition" is a rename, and renames belong in the client's own DTO).
- `composed` without an aggregator declared for the client platform → **error** (AC-04 already guarantees one exists).
- `none` with a `context` → **error**.

This yields three properties the PRD wanted but did not have:

- **The aggregator is never speculative.** It exists only for routes that genuinely need N sources. A CMS with one bounded context has zero composed routes and a correspondingly tiny aggregator.
- **One vocabulary per data shape.** `direct` routes speak the context's own DTO. `composed` routes speak the aggregator's page DTO. A single domain is never re-serialised twice on one request path.
- **The choice is reviewable in one line of YAML**, not in a design discussion.

### 5.4 D-05 — Identity propagation across a composed read

A composed read is `browser → shell session → aggregator → context API ×N`. The aggregator must not acquire privilege on the user's behalf.

> **D-05 — The aggregator forwards the end-user subject; it never substitutes a service identity.**

- The aggregator forwards the end-user subject, tenant and session reference as **opaque, forwarded claims** — it does not read, evaluate or re-issue them (`@cms/authz` supplies the claim *format* only, PRD FR-20).
- The bounded context evaluates authorisation against the forwarded subject on **every** request (D-06). If a context receives a request whose subject it cannot verify, the request is **denied**, not downgraded to a service identity.
- A context that genuinely needs a *delegated* call (context A asking context B) does not go through the aggregator. It is a context-to-context edge, which AC-02 forbids and which therefore requires the §6.3 extraction procedure — that is the intended pressure.

**Consequence, stated plainly:** the aggregator is not a trusted tier. It is a trusted *transport*, and it can be wrong or slow without becoming an authorisation hole. This is the property that keeps D-06 enforceable.

### 5.5 D-06 — Loading strategy is per-route and generated

The shell's route map (§4.4) is generated. The generation rule is fixed so it is not re-litigated per feature:

- A route's remote is **never** imported in the shell's static graph. It is reached by a dynamic import whose specifier comes from the generated registry, resolved at navigation time.
- Prefetch of a remote is permitted **only** for the route the user is navigating to, or from an explicit in-app intent signal (`Intent`-like hover/focus), never speculatively for all routes. This is the mechanism behind PRD PERF-04.
- The shell's own bootstrap chunk contains: router, registry, chrome, session bootstrap, `@cms/ui`. Nothing else. This is what the `shell-critical ≤ 150 KB` budget (PERF-02) is measuring.

---

## 6. Aggregator (Plane C) vs bounded context (Plane B)

### 6.1 The test set, made total

The PRD gives five disqualification signals (§6.2). They are necessary but not sufficient, because three of them fail *late*. This design adds three early tests and states the decision procedure.

| # | Test | Kind | Check |
|---|---|---|---|
| T1 | Declares a DB driver, ORM, or `migrations/` | static | `dependency-cruiser` forbidden dependency + forbidden path (AC-03) |
| T2 | Encodes a rule a domain expert would name as policy | **review + vocabulary** | the language check of ALG-1 step 3 applied to `**/bff/**` |
| T3 | Needs state across requests to answer a domain question | structural | no durable store allowed in the package ⇒ T1; any in-process cache is TTL-bound and derived-only |
| T4 | A domain team files changes in the aggregator for domain behaviour | process | required-reviewers + `CODEOWNERS` (PRD FR-11) |
| T5 | A second client needs a different answer to the same question | behavioural | route `dataStrategy` review + ADR |
| **T6** | **Its output DTO contains a term from a bounded context's language that is not being transported** | static + vocabulary | `teams/web/bff/src/**` may only reference domain terms in files under `src/clients/<ctx>.generated/` |
| **T7** | **It branches on a domain condition** (`if banner.status === …`) | static | rule: a `switch`/`if` whose discriminant type is declared in a context's language fails the check |
| **T8** | **It re-derives a value the provider already returns** | review | contract test assertion (FR-23): a field present in the provider schema and re-implemented locally is a finding |

T6–T8 are new and they matter because T2 "fails silently" (PRD §6.2). T7 is the mechanical core of T2: **an aggregator may read a domain value and place it in the payload; it may not branch on it.** A `formatter` may format a date it was given; it may not decide whether the date is valid.

### 6.2 ALG-2 — decision procedure

```
ALG-2  classify-a-unit(U)
 1  if U declares no store and no rule primitives          → COMPOSITION (done)
 2  run T1..T8
 3  if T1 or T2 or T3 or T6 or T7 or T8 is true:
       name the rule-or-state that triggered it                     (PRD §6.3 step 1)
       map it to a ubiquitous-language term                         (PRD §6.3 step 2)
       → BOUNDED CONTEXT, extract via PRD §6.3 steps 3–7
 4  if only T4 or T5 is true                                   → BOUNDED CONTEXT, no code move
 5  if nothing is true                                         → COMPOSITION
```

Step 3 has an ordering property the PRD relies on: **the first failing test determines the outcome**, so two teams cannot reach opposite conclusions about the same unit. T4 and T5 are checked last because they are the most expensive and the least certain.

### 6.3 D-07 — What the aggregator owns, precisely

The aggregator owns **transport-shaped decisions only**. The complete list; anything not on it is prohibited:

| Concern | Rule |
|---|---|
| Fan-out | Build a plan; execute independent nodes in parallel. No gratuitous `Sequence` node (PRD PERF-07) |
| Deadline | One request budget; per-dependency budgets **sum below** it; the sum is generated from `catalog` and asserted at boot |
| Partial results | Per-section status; a failed section degrades, the response still returns |
| Client shaping | Field selection, renaming, unit/date/case formatting — **no branching on domain values** (T7) |
| Batching | Per-request loader (PRD PERF-08); a loader crossing requests is a correctness bug |
| Caching | Cache-aside, TTL, key-versioning, single-flight (PRD PERF-11); never a source of truth |
| Resilience | Breaker + bulkhead + timeout per dependency; global retry budget ≤ 10 % (PRD PERF-09) |
| Transport identity | Bound, then forward (D-05) |

### 6.4 D-08 — Aggregator request lifecycle (deterministic)

```
ALG-3  aggregator-request(R, route r)
 1  validate config strictly; refuse to bind on failure              (FR-16)
 2  plan := plan(r)                  # from generated route descriptor
 3  budget := remaining(request budget)
 4  for each node n in plan, in dependency order:
      budget_n := min(n.declaredBudget, budget * n.share)
      if budget_n <= 0            → node status = SKIPPED(reason=deadline)
 5  execute nodes; independent nodes concurrently, one loader per request
 6  on node failure: breaker(state) → CIRCUIT_OPEN → node status = FAILED(reason)
 7  assemble response = { section_i : { status_i, data_i | error_i } }
 8  record: one histogram sample per node, one per request
 9  emit trace with one span per node; propagate context to every call
```

Steps 4 and 8 are what turn "aggregator latency is bounded by construction" (G-09) from a claim into a mechanism: the deadline is *computed before* the calls, and the histogram is per-node so a regression is attributable to a named dependency.

### 6.5 Row-7 enforcement — making "external consumers prohibited" real

PRD §7.1 row 7 says the aggregator "versions freely; external consumers prohibited", and AC-04 enforces the *code* rule. A prohibition with no runtime control is a convention. D-09 adds the control.

> **D-09 — The aggregator accepts only shell-attested sessions.**

- Session bootstrap (Plane A) issues an opaque, short-lived session reference bound to the client platform's transport identity.
- The aggregator rejects any request lacking a valid session reference from *its own* client platform with `401`, before any downstream call is planned.
- Consequence: an aggregator endpoint cannot be used by a second consumer, a script, or another client platform without first forging a shell session — which is exactly the threat the row-7 prohibition names.
- The aggregator **still** authorises nothing about the domain (D-02, D-05); it only validates *transport provenance*.

---

## 7. Ownership ledger

### 7.1 ROW-01 … ROW-11 — the authoritative interface table

This refines PRD §7.1. It adds the two columns that make the table *enforceable*: **artefact kind** (what kind of thing is published, which determines the change policy) and **generated-consumer-linkage** (whether a violation is catchable statically).

| # | Interface | Kind | Provider | Consumer(s) | Contract artefact | Change policy | Catches misuse via |
|---|---|---|---|---|---|---|---|
| 1 | `@cms/ui` | package | platform | all deployables | exported types + semver | major + 2-release deprecation | package-graph tag rules |
| 2 | `@cms/composition` | package | platform | all shells + all domain UI | exported types + semver | major | package-graph tag rules |
| 3 | `@cms/authz` | package (schema only) | platform | all `teams/*/api` | JSON Schema | major; expand/contract | forbidden-dependency rule |
| 4 | `<ctx>-api` | HTTP API | owning CT team | **aggregators only** | OpenAPI 3.1 (pinned) | expand/contract | contract test + tag rules |
| 5 | `<ctx>-web` | UI artefact (MF remote) | owning CT team | the browser shell only | `mf-manifest.json` + generated types | major + 2-release deprecation | registry is generated; unknown remote = runtime error |
| 6 | `<ctx>-{mobile,desktop}` | native bundle | owning CT team | that client platform | bundle contract | major + 2-release deprecation | catalog cardinality |
| 7 | `<client>-bff` | HTTP API | owning client team | **that client platform only** | OpenAPI 3.1 | free | **runtime**: D-09 session attestation |
| 8 | runtime config schema | package | each deployable's team | platform (value emitter) | `config.schema.ts` | strict boot failure | AC-09 |
| 9 | generated topology artefacts | package/files | platform (generator) | every consumer | generated file + `@generated` marker | regenerate only | **D1 byte-stability + FR-05 diff gate** |
| 10 | **package dependency lists** | manifest | platform (generator) | the package manager | `package.json#dependencies` | regenerate only | makes "undeclared dependency" structurally impossible |
| 11 | **budget ledger** | metadata | each budget's owner | platform (aggregator), CI (gate) | `catalog/budgets.yaml` | ADR per change | CHK-19 |

**ROW-10 is a structural change with a large payoff.** If `package.json` `dependencies`/`devDependencies` are *generated from the catalog's relation rows*, then:

- a team cannot import an interface it did not declare as a consumer — the manifest is rewritten by `catalog:generate`, and the diff gate (FR-05) fails the PR;
- Turborepo's "imports a package not specified in dependencies" check (R-BND-12) becomes a no-op rather than a gate, and the *tag* rules — the ones that carry the actual architecture — carry the whole load;
- the provider/consumer table stops being documentation and becomes the build graph's source of truth.

### 7.2 ALG-4 — ownership resolution, total and order-free

PRD §7.2 has a gap: step 2 (segment rule for `teams/`) and step 3 (`owns` glob matching) are both applicable to a path under `teams/`, and the PRD does not say which wins. Worse, nothing forbids a team from declaring `owns: ["teams/other/**"]`, which would silently make ownership *ambiguous by declaration*. ALG-4 closes both.

```
ALG-4  resolve-owner(path p, catalogue C)
 0  normalise p to repo-relative POSIX; reject p containing ".."
 1  if p is untracked (absent from `git ls-files`)     → SKIP, not an error
 2  let s = segments(p)
 3  if s[0] == "teams":
       require s.length ≥ 2                              else → ERROR E-OWN-SHAPE
       T := s[1]
       require C.team(T) exists                          else → ERROR E-OWN-UNKNOWN-TEAM
       # INVARIANT O-1: no team may own another team's directory.
       for each team U in C.teams, U != T:
            if U.owns contains any glob matching p       → ERROR E-OWN-INTRUSION
                                       (names U, T and p)
       # INVARIANT O-2: self-ownership is declared, complete, and minimal.
       require C.team(T).owns == exactly { "teams/<T>/**" }
                                       else → ERROR E-OWN-SELF-SHAPE
       return T
 4  matches := [ (team, entry) for team in C.teams
                          for entry in team.owns
                          if any(entry.paths glob matches p) ]
 5  if |matches| == 0  → ERROR E-OWN-UNCOVERED, naming p
 6  if |matches| >  1  → ERROR E-OWN-OVERLAP, naming every matching team and entry
 7  return the single matching team
```

Three consequences worth stating, because they are the point:

- **O-1** makes the rule *safe under self-declaration*. A team's own document declares its own ownership, and that document is reviewed by… itself. O-1 removes the only dangerous power that grants: it cannot claim a path outside its directory. So a self-declared ownership model becomes safe, and no second, human-maintained ownership map is needed.
- **O-2** makes the resolution *total*: every path under `teams/` has exactly one owner with no glob evaluation at all.
- Step 5 is why `catalog/teams/platform.yaml` must enumerate root-level files explicitly (`README.md`, `package.json`, `devenv.nix`, `devenv.lock`, `.envrc`, `turbo.json`, `secretspec.toml`, `CODEOWNERS`, …). A forgotten file is a hard error, not an unowned file. This is the intended ergonomics: **the cost of adding a new root file is one line of YAML.**

### 7.3 D-10 — Ownership of generated artefacts inside another team's directory

The generator writes into `teams/web/client/src/generated/…` and at the repository root (`CODEOWNERS`, `turbo.json` boundaries block). Those are writes by one team's tooling into another team's directory — which FR-01/LSC would otherwise forbid.

> **D-10 — Generated artefacts are tamper-evident, not exempt.**

- `CODEOWNERS` still assigns the *consuming* team as reviewer of a generated file inside its directory. Review remains human; the content is machine-verified.
- The guarantee is mechanical, not social: any hand edit diverges from the generator's output and fails `catalog:generate && git diff --exit-code` (FR-05) in CI, before review even matters.
- **`CODEOWNERS` itself is owned by platform and a change to it requires a platform approval plus the O-1/O-2 invariants still hold.** This is the meta-rule that stops ownership tampering: you may change the ownership map only through the ownership map, and the invariants are re-evaluated on every change.
- No `exclusions`, no suppressions, no "checked in, we edit it by hand" exceptions exist for generated artefacts. If the generator cannot express something, the fix is in the generator (Platform team's directory), never in the output file.

### 7.4 ALG-5 — provider/consumer consistency

```
ALG-5  verify-relations(catalogue C, repository R)
 1  for each interface I in C.interfaces:
       require I.provider ∈ C.teams                                else E-REL-PROVIDER
       for each consumer U of I: require U ∈ C.units               else E-REL-CONSUMER
 2  for each unit U, for each declared dependency d in manifest(U):
       require ∃ I with provider(I)=d.provider or provider(I) ∪ {…} ∋ d
                                       else E-REL-UNDECLARED (U, d)
 3  for each import of d found in U's source:
       require d ∈ manifest(U).dependencies                         else E-REL-SMUGGLED
 4  require: no unit consumes an interface whose provider it also is, unless declared
       `coOwned: true` with an ADR reference                        else E-REL-COOWN
 5  return
```

Step 4 implements PRD AC-07 as data: co-ownership is *declared with an ADR reference*, so the LSC log and the catalog cannot diverge.

### 7.5 D-11 — The consumer escalation path is an interface, too

PRD §7.3 describes a process. A process that is not an artefact does not get enforced. D-11 makes the escalation produce a record:

- A consumer needing a provider change opens an issue **quoting the interface id and the failing contract test name**. Both are machine-readable strings that exist in the repository.
- The provider's response is one of: additive (ships), alternative (ships a documented alternative), breaking (opens a deprecation window recorded in the interface row).
- **A consumer may never patch a provider's source to make its own test pass.** If it does, the change is an LSC (PRD FR-01) and requires an ADR *and* a `coOwned` declaration (ALG-5 step 4). There is no third option.

---

## 8. Metadata model and generator pipeline

### 8.1 SCH-1 — Catalog document kinds and invariants

| Kind | File | Required fields | Invariant |
|---|---|---|---|
| `Team` | `catalog/teams/<slug>.yaml` | `apiVersion`, `kind`, `metadata.id`, `spec.info.type`, `spec.owns` | O-1, O-2 |
| `BoundedContext` | `catalog/contexts/<slug>.yaml` | + `spec.team`, `spec.store`, `spec.provides.api`, `spec.provides.ui`, `spec.authorises` | `authorises` is a literal; store ≠ null |
| `ClientPlatform` | `catalog/clients/<slug>.yaml` | + `spec.owner`, `spec.runtime`, `spec.shell`, `spec.bff.id`, `spec.routes[]` | exactly one `bff.id` (AC-04); `routes[].dataStrategy` per D-04 |
| `Interface` | `catalog/interfaces/<id>.yaml` | + `spec.kind`, `spec.provider`, `spec.consumers[]`, `spec.contract`, `spec.breakingChangePolicy` | ROW-01…ROW-11 |
| `Relation` | `catalog/relations/<id>.yaml` | `spec.type`, `spec.from`, `spec.to` | target must exist |
| `Budget` | `catalog/budgets.yaml` | `id`, `owner`, `measurement`, `threshold`, `gate` | every PRD PERF/RES id present exactly once |

Two additions relative to the PRD's §8.2:

- **`Interface` becomes a first-class kind.** The PRD declares provider/consumer edges in `relations/` and separately in `contexts.*.provides/consumes`; that duplication is exactly the "declared twice" failure mode G-04 exists to prevent. `relations/` becomes the *derived* index of `interfaces/`, never hand-authored.
- **`Budget` becomes metadata.** A budget with no owner and no gate is a wish; a budget in a YAML file with an `owner` and a `gate` is a §15 architecture constraint. This is how §12/§13 stop being prose.

### 8.2 D-12 — Generator pipeline

```
catalog/ ──▶ load ──▶ validate (ALG-2/4/5 + schema) ──▶ plan ──▶ emit ──▶ verify
              │            │ fail: exit 1, all violations, sorted
              │            └──▶ exit 2 on unparseable input
              ▼
        single in-memory graph: nodes = units, interfaces, teams, budgets
```

The pipeline is a **single pass with one graph**. No generator stage re-reads the filesystem. This is what makes D1 true and is why the emitted ordering is stable.

| Stage | Produces | Determinism note |
|---|---|---|
| validate | nothing | sorted diagnostics |
| plan | the graph | sorted nodes, then sorted interfaces, then sorted routes |
| emit: ownership | `CODEOWNERS`, `docs/ownership.md` | one rule per `owns` entry (PRD §4.3) |
| emit: routes | `teams/<c>/client/src/generated/routes.generated.tsx` | sorted by route path |
| emit: registry | `teams/<c>/client/src/generated/remote-registry.generated.ts` | sorted by remote id; every URL pinned (D-11/PRD D-11) |
| emit: adapters | `teams/<c>/bff/src/clients/*.generated.ts` | sorted by interface id |
| emit: manifests | every `package.json#dependencies` (ROW-10) | sorted keys |
| emit: budgets | `teams/web/bff/src/generated/deadlines.generated.ts`, `catalog/budgets.resolved.json` | per D-07 step 4 |
| emit: boundaries | `turbo.json#boundaries.tags` (merged between markers) | sorted tags |
| emit: ci | `teams/platform/ci/*.yaml` | per deployable |
| verify | re-read emitted files, assert S1–S7 | failure ⇒ exit 1 |

**The `verify` stage is not optional.** A generator that writes and does not re-read has not demonstrated D1.

### 8.3 D-13 — Change protocol for the catalog

- The catalog is written **in the same PR** as the code it describes. A PR that changes `catalog/` without changing or explaining the affected code is a review finding, and CI flags it by printing the affected units in the PR description.
- The catalog is a **single-writer-per-domain** artefact: `catalog/teams/<slug>.yaml` and `catalog/contexts/<slug>.yaml` are written only by that team; `catalog/interfaces/<provider-id>.yaml` is written by the provider. A PR touching a document you do not own is an LSC.
- Merge ordering is irrelevant: the catalog is not consumed at merge time; it is consumed at build time. A PR may add a relation and the consuming code together.

---

## 9. Bounded-context internals — Clean Architecture as designed, not as decorated

PRD FR-22 scopes Clean Architecture to `banner` as an exemplar (NG-08). This section specifies what that exemplar actually *is*, so it can be copied deterministically.

### 9.1 D-14 — Layer contracts

```
teams/<ctx>/api/src/
  domain/          entities, value objects, domain services, repository *interfaces*
                   IMPORTS: nothing outside domain/. No framework. No clock, no uuid,
                   no randomness, no I/O.  (functional core — §9.2)
  application/     use cases; each use case declares the ports IT needs; transaction
                   boundaries live here; no HTTP types
  adapters/
    inbound/       HTTP controllers, request→command mapping, error translation
    outbound/      persistence, message bus, external provider clients, clock, ids
  config/          config.schema.ts (FR-16)
  main.ts          composition root — the ONLY file binding a port to an adapter
```

**D-14 extends PRD D-10 with one clause: `domain/` is a functional core.** It is pure — deterministic given its inputs, free of I/O, free of the clock, free of randomness. This is not decoration: it is the cheapest possible test strategy and the only way a bounded context's rules can be moved into or out of an aggregator without a rewrite (PRD §6.3 step 4 requires moving the rule *and its test*). Evidence: the functional-core/imperative-shell split (R-CA-08, R-CA-09) is the same dependency rule as D-10, expressed as a property of the inner layer rather than as a drawing of lines.

### 9.2 ALG-6 — port declaration (consumer-owned, per use case)

```
ALG-6  ports-for-use-case(U)
 1  ports(U) := { p : p is referenced by U's source }
 2  each p is declared in U's own module, not in a shared "ports" package
 3  a port may not declare a method with zero call sites in U        (PRD §10, ISP)
 4  a port's parameter and return types are domain types or primitives
       — never framework types, never transport types               (PRD §10, DIP)
 5  main.ts is the only module permitted to import both a port and an adapter
```

Rule 2 is what makes ISP enforceable rather than aspirational: a shared `Ports` package is, structurally, a module whose owner is nobody. Rule 3 is machine-checkable (`dependency-cruiser` orphan rule) and is the concrete form of "a port grows a method with zero callers".

### 9.3 Test strategy matrix

| Layer | Test type | Real dependencies? | Budget |
|---|---|---|---|
| `domain/` | unit | **none** — no mocks at all | fast, parallel, order-independent |
| `application/` | unit + in-memory port fakes | none | fast |
| `adapters/inbound` | HTTP slice | in-process app, real router | medium |
| `adapters/outbound` | integration against the real store | yes, containerised by `devenv up` | slow, serial, tagged |
| `contracts` | consumer-driven, against the provider's published schema | yes | gated in CI |
| `main.ts` | smoke — boots with a valid config, refuses with an invalid one | yes | one test, because it is the composition root |

The composition root gets exactly one test. Its correctness is structural (ALG-6 rule 5); testing it exhaustively is the "big ball of mud" reaction to an architecture that made it small.

---

## 10. Frontend architecture

### 10.1 D-15 — Final Module Federation configuration, per unit kind

The PRD §11.3 gives nine decisions. Two of them conflict with upstream's stated constraints and one is incomplete against the published size table (see GAP-01 … GAP-03). The configuration below is the resolved one.

| Setting | Domain UI artefact (remote) | Shell (host) |
|---|---|---|
| `name` | `<ctx>-web` | `shell-web` |
| `exposes` | `{'./App': './src/App.tsx'}` | **none** |
| `filename` | `[name].[contenthash:8].js` | n/a |
| `remotes` | none | generated registry, pinned (D-11) |
| `shared` | `react`, `react-dom` as **singleton** + exact `requiredVersion`; `eager: false` | same list, resolved first |
| `shareStrategy` | `loaded-first` | `loaded-first` |
| `experiments.externalRuntime` | **`true`** | n/a |
| `provideExternalRuntime` | n/a | **`true`** (legal only because the shell has no `exposes`) |
| `experiments.optimization.target` | `web` | `web` |
| `experiments.optimization.disableSnapshot` | **`true`** (production builds only) | `true` |
| `experiments.optimization.disableRemote` | **`true`** — a remote never consumes another remote | n/a |
| `experiments.optimization.disableShared` | **`false`** — see GAP-01 | `false` |
| `manifest.disableAssetsAnalyze` | **never set** (MF-2) | never set |
| `runtimePlugins` | fallback-on-load-failure (MF-8) | fallback-on-load-failure |

Two of these are load-bearing and neither appears in the PRD as written:

- **`externalRuntime` + `provideExternalRuntime`.** With `externalRuntime`, a remote reads its runtime from the host-provided global `_FEDERATION_RUNTIME_CORE` (R-MF-22). Without the host providing it, **every remote fails at load**. The shell is therefore not just a mount point; it is the runtime provider, and "exactly one instance" applies to the federation runtime exactly as it applies to React. This becomes a second PERF-05 assertion.
- **`disableRemote: true` on remotes** is both a size win and a *correctness* expression: a domain UI artefact has no business consuming another remote, so the capability is provably unused. Upstream's guidance is explicit that these flags are for capabilities a build "will definitely not use".

### 10.2 D-16 — Why `disableShared` must be off, and what replaces it

The size benefit the PRD attributes to `disableShared` (73,154 B → 50,008 B, R-MF-24) is real, and it is also incompatible with the PRD's own PERF-05. Upstream states the constraint plainly: use `disableShared` **only when the build has no `shared` configuration**, and the Vite/Rspack surfaces emit a warning when `disableShared: true` is combined with a non-empty `shared` (R-MF-23). Disabling shared in a build that consumes `react` from the host share scope is not a size optimisation; it is the removal of the mechanism that makes PERF-05 true.

The size budget is still reachable without it. From upstream's published table (R-MF-22), gzip `remoteEntry.js`:

| Configuration | gzip | vs 8 KB budget (PERF-03) |
|---|---|---|
| no flags | 21,437 B | ✗ |
| `disableSnapshot` | 20,096 B | ✗ |
| `target: 'web'` | 19,314 B | ✗ |
| both | 17,998 B | ✗ |
| both + `externalRuntime` | **5,381 B** | ✓ |
| `disableSnapshot` **off** + `externalRuntime` | 8,222 B | ✗ |

So PERF-03 (≤ 8 KB) is reachable **only** with `disableSnapshot` + `target: 'web'` + `externalRuntime` together. `disableShared` is not required for the budget; it is only required for the last 2 KB, and it costs the singleton guarantee. **The trade is therefore settled: `disableShared` off, `disableSnapshot` on, `externalRuntime` on.** This is GAP-02.

### 10.3 D-17 — Error and degradation model

- One error boundary **per remote**, generated from `clients/<slug>.yaml#errorBoundaries`. A boundary is a route-region boundary, not a component boundary: one failed remote must not blank the page.
- The fallback component is **owned by the shell** and is chrome-only (a retry affordance + an error id). It may not render domain vocabulary (ALG-1 step 3 applies to `components/RemoteError.tsx` too).
- A remote that fails to *load* (network, 404, CSP rejection) is distinguishable from a remote that throws while rendering. They get different fallbacks: the first is retryable, the second is a bug report. The runtime plugin (MF-8) handles the first; the boundary handles the second.
- **A remote's failure never removes the shell.** The shell is the only thing that can be globally unavailable, and that is the point of a thin shell.

### 10.4 D-18 — Theme, styles and duplication

Module Federation does not isolate CSS, and every remote that imports `@cms/ui` may ship its own copy of the stylesheet. Three named controls, because this is the largest *unmeasured* duplication in the design:

| Control | Rule |
|---|---|
| Style ownership | Exactly **one** place ships the design system's CSS: the shell's bootstrap chunk. `@cms/ui` is published as tokens + components; its stylesheet is emitted once, by the shell. |
| Token contract | Remotes consume tokens through `@cms/ui` only. A remote that injects its own global stylesheet fails the shell-purity check (it is chrome logic living in Plane B). |
| Duplication budget | BUD-06 (§11.3) bounds the aggregate JS emitted by one route across all its remotes — the metric PERF-02 does **not** cover, because PERF-02 measures transfer, not artifact size. |

### 10.5 D-19 — Frontend observability, structural

PRD §11.4 makes OpenTelemetry a gate on PH-6. It does not say how a federated page produces one trace. It must:

- The **shell** creates the tracer provider once, before any remote loads, and publishes it on a well-known global guarded against double registration.
- Remotes **never** construct a provider; they obtain the tracer through `@cms/composition`.
- `propagateTraceHeaderCorsUrls` must list every remote and API origin, or `traceparent` is silently dropped at exactly the boundary you are trying to observe (R-MFE-25).
- The CORS failure mode is the single most common one: OTLP-over-HTTP from a browser needs the host origin in the collector's allowed origins, and the symptom is "no spans, no error".
- The remote mount is wrapped in a child span of the shell's navigation span, so a slow remote is attributable to a named remote, not hidden inside a route average.
- `@opentelemetry/api` is a **shared singleton**, exactly like React. Two copies means two root spans (R-MFE-25).

---

## 11. Budget ledger

Every PRD PERF/RES id appears exactly once in `catalog/budgets.yaml` with an owner and a gate. This section states the ledger's schema and adds the four budgets the PRD does not have.

### 11.1 BUD schema

```yaml
id: PERF-03
title: remoteEntry.js gzip size, per remote
owner: banner            # team accountable for the number
measurement: size-limit against the built remoteEntry artefact
threshold: { value: 8192, unit: bytes }
gate: check:perf         # a check:* / perf:* script; a budget with no gate is invalid
rebaseline: quarterly    # cadence at which the threshold may be revisited
adr: null                # required if re-baselined
```

### 11.2 The four missing budgets

| ID | Budget | Threshold | Why it is missing from the PRD |
|---|---|---|---|
| **BUD-06** | Aggregate JS emitted for one route **across all its remotes** | ≤ 2× the PERF-02 route budget, and ≤ 3 remotes per route | PERF-02 measures what a browser downloads on one navigation. Nothing bounded the *artifact* — which is what CI stores, the CDN serves and each pipeline rebuilds. Measured micro-frontend studies report ~50 MiB of emitted JS for an 8-remote shell versus ~1.85 MiB for the equivalent modular build, with a build time of 113.8 s versus 10.65 s (R-MFE-26, `PARTIAL`: thesis-grade, cited only as a magnitude, never as a target) |
| **BUD-07** | Shared-module duplication count per route | 0 | The classic silent failure: a semver-range mismatch makes the federation runtime fall back to bundling a private copy, and everything still renders. PERF-05 catches *two React instances*; nothing catches a duplicated `lodash`/`date-fns` |
| **BUD-08** | CSS transferred for one route | ≤ 1 design-system stylesheet | CSS is not isolated and is not in PERF-02 |
| **BUD-09** | Remote mount p95, per route, measured in the field (RUM) | ≤ 250 ms after navigation commit | PERF-01 measures the route's Core Web Vitals; it does not attribute a regression to a *named remote* |

### 11.3 Cost centres and their owners

| Cost centre | Metric | Owner | Lever |
|---|---|---|---|
| CI compute | cache hit ratio ≥ 80 % on `main`; task graph runtime | platform | affected-based selection, narrowed `inputs`, declared `env` (PRD FR-25) |
| Local environment | warm ≤ 10 s, cold ≤ 300 s | platform | eval cache + binary cache (R-DV-15, R-DV-16) |
| Browser | BUD-06, PERF-02, PERF-03, BUD-07, BUD-08, PERF-05 | each remote's team | generated budgets, per-remote gate in that team's pipeline |
| Aggregator | p99 per route class, event-loop lag, retry rate | client-platform team | deadline plan, loaders, breakers, caching |
| Runtime fleet | requests/limits, image size, cost per team | each owning team | PERF-12, RES-09, RES-10 |
| Store | one writer per context | each context team | single store per bounded context is a *design* constraint, not an optimisation |

---

## 12. What the aggregator is *for*, and when it is deleted

A design that cannot say when a component should be **removed** has not decided what it is for. D-20 states the deletion conditions, derived from D-04:

| Condition | Action |
|---|---|
| A client platform has **zero** routes with `dataStrategy: composed` | the aggregator is retained but reduced to shell/chrome endpoints; it is not deleted while the client platform exists |
| A second client platform appears | a *second*, separate aggregator is created — never a shared one (D-01, PRD AC-04) |
| All routes of a client become `direct` **and** chrome is served from a static/config endpoint | the aggregator is deleted by an ADR; its OpenAPI is deprecated with a 2-release window |
| A T2 test fires twice for the same term | the **boundary** is wrong (PRD §6.3 step 7); the boundary is re-derived, not the rule |

---

## 13. Check inventory

Every gate is named, has an exit code, and has a **seeded violation fixture** that proves it fails. A check without a fixture is a check that has never been observed to work (PRD §21 item 5).

| CHK | Command | Input | Fails on | Seeded fixture |
|---|---|---|---|---|
| 01 | `check:catalog` | `catalog/**` | FR-02/03/04/06/07/13, D-04 route rules, O-1/O-2 | unknown key; dangling relation; two aggregators; `direct` route with 2 contexts |
| 02 | `check:ownership` | git index + catalog | ALG-4: uncovered path, overlap, intrusion | a team doc claiming `teams/other/**` |
| 03 | `check:relations` | catalog + manifests + source | ALG-5: undeclared, smuggled, undeclared co-ownership | an import of a package not in the generated manifest |
| 04 | `check:boundaries` | package graph | AC-01, AC-02 (Turbo tags) | cross-team import |
| 05 | `check:layers` | file graph | AC-08, D-10, D-14 | `domain/` importing `@nestjs/common` |
| 06 | `check:bff-purity` | file graph + deps | AC-03, T1 | `bff/` importing `pg` |
| 07 | `check:shell-purity` | file graph + vocabulary | AC-05, AC-06, ALG-1 | a shell module exporting `Banner` |
| 08 | `check:generated-fresh` | generator | FR-05, FR-10, D1 | a hand-edited generated file |
| 09 | `check:pins` | tracked text | FR-21, D-11 | `@latest` in a manifest |
| 10 | `check:tasks` | `turbo.json` + manifests | FR-28 (no vacuous pass) | a task resolving to zero packages |
| 11 | `check:repo-shape` | filesystem | AC-10, FR-26 | a nested `.git` |
| 12 | `check:lsc` | PR metadata | FR-01, AC-11 | a cross-team PR without `Owners-Override` |
| 13 | `check:authz-placement` | routes + source | AC-12, D-13 (§14 GAP-13) | a BC route with no authorisation evaluation and no `public: true` |
| 14 | `check:config-strict` | deployable boot | AC-09, FR-16 | an unknown env key |
| 15 | `check:contracts` | published schemas + consumer tests | FR-23 | an adapter expectation diverging from the provider |
| 16 | `check:deps-duplicate` | federation manifests | BUD-07 | a remote bundling a shared singleton |
| 17 | `perf:budgets` | built artefacts | PERF-02/03, BUD-06/08 | a deliberately oversized route |
| 18 | `res:timings` | timings | RES-05, RES-05a, RES-06 | n/a (measurement) |
| 19 | `check:budgets` | `catalog/budgets.yaml` | BUD schema validity | a budget with no `gate` |
| 20 | `perf:runtime` | in-process metrics | PERF-06/09/10 | a retry storm |
| 21 | `res:telemetry` | CI + cloud | RES-06, RES-08, RES-10 | n/a (measurement) |

**Exit-code discipline.** Every `check:*` exits 0 or 1 on a judgement, and 2 on an internal failure. A pipeline must treat 2 as failure.

### 13.1 Correcting AC-01's "enforced twice"

The PRD (FR-14, AC-01) holds `turbo boundaries` and `dependency-cruiser` as two mechanisms for the same constraint. They do not cover the same ground, and the PRD overstates the redundancy:

- **Turborepo boundaries operate on the workspace *package* graph.** It detects imports that leave a package directory, imports of undeclared dependencies, and (newer versions) package-graph cycles; tag rules constrain which package may depend on which, transitively (R-BND-12). Its tags are package tags; **npm-package deny lists are an open feature request, not a shipped capability** (R-BND-13).
- **Consequence.** AC-03 ("no aggregator declares a store, ORM or migration") and AC-08 ("dependency rule *inside* a bounded context") are **file-graph and third-party-dependency** rules. They cannot be expressed in Turbo boundaries at all. `dependency-cruiser` carries them alone.

So the correct statement is: *package-graph boundaries are enforced twice (Turbo + dependency-cruiser); file-graph and npm-dependency rules are enforced once (dependency-cruiser + ESLint, paired per RISK-11).* This is a correction of scope, not of intent, and it is why `check:bff-purity`, `check:layers` and `check:shell-purity` remain mandatory even if `turbo boundaries` ships as GA. See GAP-07.

---

## 14. Gaps and contradictions found in the PRD

Each requires an ADR. None may be resolved silently.

| GAP | Finding | Evidence | Proposed resolution | ADR / phase |
|---|---|---|---|---|
| **GAP-01** | MF-4 (`disableShared` enabled) contradicts MF-5/PERF-05 (exactly one React instance). Upstream: use `disableShared` only when the build has no `shared`. | R-MF-22, R-MF-23, R-MF-24 | `disableShared: false` everywhere; keep the singleton guarantee; budget met via `externalRuntime` (D-16) | ADR-0013 / PH-6 |
| **GAP-02** | PERF-03 (≤ 8 KB) is unreachable without `disableSnapshot: true`, which §11.3 never states. Upstream table: `externalRuntime` with `disableSnapshot` **off** = 8,222 B gzip. | R-MF-22 | Add `experiments.optimization.disableSnapshot: true` for production builds only (it costs HMR and TS type sync, which are dev-time concerns) | ADR-0013 / PH-8 |
| **GAP-03** | `externalRuntime` requires the host to publish `_FEDERATION_RUNTIME_CORE`; with no `provideExternalRuntime`, every remote fails at load. §11.3 states neither the requirement nor the constraint that the shell must have no `exposes`. | R-MF-22, R-MF-23 | Shell sets `provideExternalRuntime: true` and exposes nothing; add a PERF-05 sibling assertion: exactly one federation runtime | ADR-0013 / PH-6 |
| **GAP-04** | The data path is unspecified. With the shell forbidden from calling context APIs and a remote forbidden from calling an aggregator, nothing states when the aggregator participates. Three compliant designs exist. | PRD §5.2, §16, RISK-01 | Introduce `route.dataStrategy ∈ {none, direct, composed}` with the validation rules of D-04 | ADR-0014 / PH-2 |
| **GAP-05** | Identity propagation across the aggregator is unspecified. A service identity would turn D-06's per-request authorisation into delegated privilege and make the aggregator an authorisation hole. | PRD D-06, D-02 | D-05: forward the end-user subject; deny unverifiable subjects; forbid a delegated-call shortcut | ADR-0015 / PH-6 |
| **GAP-06** | §7.2 leaves precedence between the `teams/` segment rule and `owns` globs undefined, and nothing forbids a team claiming another team's directory under self-declaration. | PRD §7.2, FR-06 | ALG-4 invariants O-1/O-2, which make self-declaration safe without a second ownership map | ADR-0016 / PH-2 |
| **GAP-07** | "AC-01 enforced twice" overstates redundancy: Turbo boundaries cannot express AC-03/AC-08 today. | R-BND-12, R-BND-13 | Restate the gate matrix per §13.1; keep `dependency-cruiser` mandatory regardless of Turbo's maturity | ADR-0017 / PH-7 |
| **GAP-08** | DEC-07 cites `devenv hook` guidance that has since changed: devenv 2.0 provides native shell reloading and states direnv is no longer needed; it also changed `devenv build` output to JSON, made the native process manager default, and removed `git-hooks` from defaults. Separately, §9's `.envrc` snippet (`eval "$(devenv direnvrc)"`) is not upstream's canonical form — upstream pins `direnvrc` by **URL + sha256** via `source_url`, which satisfies D-11 better than the unpinned form and interacts with DIR-02. | R-DV-15, R-DV-17 | Keep direnv, but for the *stated* reason (reviewability, not capability); adopt the pinned `source_url` form; re-verify FR-17/FR-18 against devenv 2.x | ADR-0018 / PH-5 |
| **GAP-09** | Nothing bounds aggregate artefact duplication, remote count per route, CSS duplication, or remote mount latency — only what a single navigation transfers. | §12.1, R-MFE-24, R-MFE-26 | BUD-06 … BUD-09, as metadata with owners and gates | ADR-0019 / PH-8 |
| **GAP-10** | FR-23 verifies contracts locally. A consumer's expectation can be green while a provider version has already shipped an incompatible field. | PRD FR-23, D-05 | Provider publishes a **contract digest**; the consumer gate runs against the provider's *published* schema and fails on a semantic-version jump; no hand-authored DTO copies (already FR-23) | ADR-0020 / PH-6 |
| **GAP-11** | `spec.authorises: every-request` is decorative: AC-12 checks *placement*, not that every inbound route evaluates authorisation. A newly added public route is compliant today. | PRD §8.2, AC-12 | Deny-by-default route coverage test (`check:authz-placement` CHK-13): every inbound route references an authz port or declares `public: true` with an ADR | ADR-0021 / PH-6 |
| **GAP-12** | The generator (platform team) writes into other teams' directories and at the repository root. Without a stated rule this is an undeclared cross-team write. | PRD FR-01, FR-05, §4.4 | D-10: tamper-evident, not exempt; invariants re-evaluated on every ownership change; no exclusions | ADR-0022 / PH-3 |
| **GAP-13** | `ROW-7`'s "external consumers prohibited" has only a code-level check (AC-04). | PRD §7.1 row 7 | D-09: shell-attested session; the aggregator refuses requests without one, before planning any downstream call | ADR-0023 / PH-6 |

**Also recorded, not requiring an ADR:** the PRD's evidence base is strong and its rejections (R-SOLID-09, R-MONO-09, R-BFF-24 …) are maintained honestly. The corrections in this document are *additions of mechanism*, not corrections of fact — except GAP-01/02/03, which are corrections of **configuration**, and GAP-08, which is a **staleness** correction.

---

## 15. Requirement → design → check traceability

| Requirement | Design element | Check | Phase |
|---|---|---|---|
| D-04, D-07, D-10, AC-01 … AC-12 | ALG-1, ALG-2, ALG-4, ALG-5, ALG-6 | CHK-01 … CHK-14 | PH-2 → PH-7 |
| D-02, D-06, PERF-06 … PERF-09 | ALG-3, D-07, D-09 | CHK-06, CHK-13, CHK-20 | PH-6, PH-8 |
| D-14, FR-19, FR-22 | D-14, ALG-6, §9.3 | CHK-05 | PH-6 |
| MF-1 … MF-9, PERF-02 … PERF-05 | D-15, D-16, D-18, BUD-06 … BUD-09 | CHK-16, CHK-17 | PH-6, PH-8 |
| FR-05, FR-08 … FR-11, G-04 | §3.1 (S1–S7), D-12, D-13 | CHK-08 | PH-3 |
| FR-17, FR-18, DEC-07 | GAP-08 resolution | CHK-14 + manual | PH-5 |
| FR-21, FR-25, RES-01 … RES-10 | §8.2 emit stages, CHK-09, CHK-10 | CHK-18, CHK-21 | PH-1, PH-5, PH-8 |
| §12, §13 budgets | §11 BUD ledger in metadata | CHK-19, CHK-17, CHK-20, CHK-21 | PH-8 |

---

## 16. Consequences a reader should notice

1. **The metadata gets bigger; the arguing gets smaller.** `interfaces/`, `budgets.yaml` and `route.dataStrategy` are three new kinds of metadata. Each replaces a class of human decision that previously happened per pull request.
2. **Most enforcement is static, not procedural.** Every check in §13 is a lint, a graph walk or a schema parse. The only runtime control added is D-09's session attestation, because that one cannot be made static.
3. **The aggregator is now conditional, not constitutive.** Under D-04 a client platform with no composed route has almost no aggregator. That is the intended consequence of an honest look at what a composition tier costs (PRD §6.4).
4. **The performance story is now attributable.** BUD-09 and §6.4's per-node histograms mean a regression names the remote or the dependency that caused it, rather than degrading a global average.
5. **The frontend has three singletons, not one.** React, the federation runtime, and the tracer. PERF-05 asserts the first; D-15 and D-19 assert the other two. Any design that adds a fourth shared singleton should be expected to justify it against these three.

---

## 17. New references introduced by this document

All are recorded in `docs/references.md` §R-25 before being cited here, per that document's verification rule.

| Used for | References |
|---|---|
| Module Federation optimisation flags and the published size table | R-MF-21, R-MF-22, R-MF-23, R-MF-24 |
| Micro-frontend cost, budgets, and shared-tracer discipline | R-MFE-24, R-MFE-25, R-MFE-26 |
| Turbo boundaries scope and limits | R-BND-12, R-BND-13 |
| Functional core / imperative shell (the inner layer as a property) | R-CA-08, R-CA-09 |
| Catalog as desired state, relations as authoritative, API as first-class entity | R-META-26, R-META-27, R-META-28, R-META-29 |
| Constraint unification as the alternative to schema+instance (recorded for DEC-24) | R-META-30, R-META-31 |
| devenv 2.x, binary caching, pinned `direnvrc` | R-DV-15, R-DV-16, R-DV-17 |
---

# Part II — The seven architecture views

Sections 1–17 above specify *how the architecture holds together*. Sections 18–24 below state the same design in the seven standard views, so that a reader can enter through any one of them and arrive at the same system.

---

## 18. Solution architecture

### 18.1 Component catalogue

Every component in the system, with the four facts that determine its design: who owns it, what it provides, what it may scale on, and which availability class it belongs to. A component not in this table does not exist.

| Component | Owner | Provides | Consumes | Owns state? | Scale axis | Avail class |
|---|---|---|---|---|---|---|
| **CDN / edge** | platform | static asset delivery for shell + remotes | build artefacts | no | request volume | A (critical, multi-region) |
| **Gateway** | platform | TLS termination, routing, rate limit, WAF | all deployables | no | request volume | A |
| **Shell** `teams/web/client` | web | route map, remote registry, session bootstrap, chrome, error boundaries | `@cms/ui`, `@cms/composition`, remotes, **aggregator (chrome endpoints only)** | no (view state) | deploy count, not traffic | B (shell asset on CDN; shell failure = total outage for the client) |
| **Remote** `teams/<ctx>/client` | context team | `<ctx>-web` UI artefact | `@cms/ui`, `@cms/composition`, **own context API only** | view state only | deploy count | C (per-route degradation, isolated by D-17) |
| **Aggregator** `teams/web/bff` | web | `web-bff` OpenAPI, page DTOs | `@cms/authz`, `@cms/ui`, context APIs | **no** (derived cache only) | QPS / concurrency | B |
| **Context service** `teams/<ctx>/api` | context team | `<ctx>-api` OpenAPI | `@cms/authz`, its own store | **yes — sole writer** | domain load | B |
| **Store** (per context) | context team | durable state | — | yes | storage / IOPS | B |
| **Generator** `teams/platform/generator` | platform | all generated topology artefacts | `catalog/**` | no | not runtime | build-time only |
| **Check harness** `tools/` | platform | 21 exit-code-bearing gates | repository + build outputs | no | build-time only | build-time only |
| **Observability pipeline** | platform | traces, metrics, budgets | every component | no (sampled) | ingestion | B (non-blocking by design: a collector outage must not fail a request) |
| **Identity provider** | platform | authentication | shell, BC services | yes | — | A (external dependency, NG-06: format contracted, provider not selected) |

### 18.2 Runtime topology

```
                     ┌─────────────── CDN / edge ────────────────┐
   browser  ────────▶│ shell bootstrap (immutable, content-hashed) │
                     │ remoteEntry[banner] … remoteEntry[n]       │
                     └────────────────────────────────────────────┘
                                   │  (1) shell bootstrap → aggregator /chrome/session
                                   ▼
                             ┌───────────┐
   gateway ──(TLS, WAF, rate-limit) ──▶│ aggregator │  (2) composed routes only
                             └─────┬─────┘
                                   │  (3) fan-out, N context APIs
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              ┌──────────┐   ┌──────────┐   ┌──────────┐
  (4) direct  │ context │   │ context │   │ context │      session
  remote ────▶│ API  A   │   │ API  B  │   │ API  C  │      verified at
              └────┬─────┘   └────┬─────┘   └────┬─────┘      every call
                   ▼              ▼              ▼
               store A        store B        store C
```

Four numbered flows, each specified in §19:

| Flow | Trigger | Participants | Spec |
|---|---|---|---|
| (1) | shell boot | CDN → shell → gateway → aggregator | §19.2 |
| (2) | navigation to a `composed` route | shell → aggregator → N contexts | §19.3 |
| (3) | navigation to a `direct` route | remote → **own** context API | §19.4 |
| (4) | mutation from any route | remote → **own** context API | §19.5 |

### 18.3 One walkthrough, three outcomes

The same user action — opening `/banners` — resolves differently depending on declared metadata, and **only** on declared metadata (D-04):

| Route metadata | What the browser does | What the aggregator does | Round trips to a context API |
|---|---|---|---|
| `dataStrategy: direct`, one context | loads `banner-web`, remote fetches its own data | **nothing** | 1 |
| `dataStrategy: composed`, 2 contexts | loads both remotes; data arrives as section props in one response | one plan, two parallel calls, per-section status | 1 browser-visible, 2 server-side |
| `dataStrategy: none` | shell renders chrome only | chrome/session endpoints only | 0 |

This table is the single most useful artefact in the document: it is what makes the composition question answerable without reading the code.

---

## 19. Integration design

### 19.1 Integration taxonomy — and what is deliberately absent

| Integration | Mechanism | In v3.0.0? | Rationale |
|---|---|---|---|
| browser → aggregator | HTTPS/JSON, session cookie | **yes** | client-specific composition (D-02) |
| aggregator → context API | HTTPS/JSON, forwarded subject | **yes** | the only aggregator egress (D-07) |
| remote → own context API | HTTPS/JSON, session cookie | **yes** | the `direct` path (D-04) |
| shell → context API | — | **prohibited** | AC-05 |
| remote → aggregator | — | **prohibited** | RISK-01 |
| remote → remote | — | **prohibited** | `disableRemote: true` (D-15) |
| context → context (sync) | — | **prohibited** | AC-02; requires §6.3 extraction |
| context → context (async events) | — | **not in v3.0.0** | see below |
| third-party API | outbound adapter | only when a context declares it | adapter is infrastructure (D-14) |

> **D-25 — No asynchronous inter-context integration in v3.0.0.** PRD D-03 states a bounded context exposes exactly two artefacts: an API and a UI artefact. An event stream is a third. Adopting it would require a decision about schema-registry ownership, delivery semantics, ordering, replay and idempotency that no requirement in the PRD currently justifies. **Revisit trigger:** the first context-to-context requirement that cannot be met by an extract-and-expose (§6.3) — typically a real-time projection. When it is adopted it is a **new artefact kind in `catalog/interfaces/`**, an ADR, and a schema-registry owner; it is not a library a team adds.

### 19.2 INT-01 — Request envelope

Every cross-boundary request carries the same four things. Nothing else crosses a boundary; correlation data is not optional.

| Element | Header / field | Produced by | Consumed by | Rule |
|---|---|---|---|---|
| Correlation | `X-Correlation-Id` (UUIDv7) | gateway (or shell bootstrap) | every hop, logged | the aggregator **forwards** it; it never mints a second one |
| Trace | `traceparent` / `tracestate` (W3C) | instrumentation | every hop | R-MFE-25, D-19; CORS must allow it on cross-origin hops |
| Deadline | `X-Deadline-Ms` (relative ms) | aggregator | each context API | strictly decreasing; a context that receives a budget it cannot meet returns `503`+`Retry-After`, never a partial lie |
| Subject | session cookie (opaque) or bearer token | browser / IdP | the **context service** | opaque to the aggregator (D-05); the context verifies it locally (§22.2) |

`X-Deadline-Ms` is the load-bearing one: it is what makes PERF-06 enforceable end to end rather than only at the aggregator, because a context that would overrun the remaining budget can decline early instead of consuming the request budget silently.

### 19.3 INT-02 — The composed flow

```
1  browser → aggregator   GET /pages/{route}            (session cookie)
2  aggregator             validate config (already booted), assert session attestation (D-09)
3                         plan = generated route descriptor; budget = route budget
4  for each node n in plan (parallel):  GET /{ctx}/{resource}?ids=…   X-Deadline-Ms
5  context                 verify session → authorise every request (D-06) → execute → respond
6  aggregator             assemble { section_i: { status_i, data_i | problem_i } }
7  browser                hand each section to the remote as props
```

- **Errors** use RFC 9457 `application/problem+json` (R-INT-01) uniformly, so a client renders one error shape whether the failure came from the gateway, the aggregator or a context.
- **Partial success is normal, not exceptional.** A failed section carries `status: "failed"` with a problem object; the response is still `200`. The shell shows the region-level fallback (D-17).
- **Batching** is the caller's choice expressed in the request (`?ids=`), and coalescing happens in a per-request loader (PERF-08).

### 19.4 INT-03 — The direct flow

```
1  remote   GET {ctxApiOrigin}/{resource}              (session cookie, same-origin via gateway)
2  context  verify session → authorise → execute       (same contract as the aggregator's call)
3  remote   renders from the domain DTO — no page DTO, no field renaming (D-04)
```

The direct flow is *byte-identical in shape* to what the aggregator would send. That is deliberate: it means a route can migrate from `direct` to `composed` without the context changing anything.

### 19.5 INT-04 — Writes

| Rule | Reason |
|---|---|
| A write always targets the context API directly, never the aggregator | the aggregator is not an authority (D-07) |
| Every mutating request carries an idempotency key (client-generated UUIDv7, unique per intent) | retries are automatic at the gateway and in the client; without a key a retry duplicates the effect |
| Idempotency keys are stored by the context, scoped to `(subject, key)`, with the response | makes a retry free and makes a duplicate observable |
| Writes are single-context, single-transaction | no cross-context transaction exists in v3.0.0 (D-25); a workflow spanning contexts is a §6.3 extraction, not a distributed transaction |

### 19.6 INT-05 — Contract lifecycle

```
ADD   provider adds an optional field or a new operation
      → consumer CI runs against the provider's PUBLISHED schema; green; no consumer change
CHANGE provider changes an existing field's meaning or removes it
      → contract digest changes → consumer gate fails → provider opens a deprecation window
      → consumers migrate → provider removes only after the window (2 releases)
BREAK  the only way out is the window; a consumer may not patch provider source (D-11)
```

The mechanism the PRD lacks is the **contract digest**: FR-23 verifies locally, so a consumer can be green against yesterday's provider while the provider has already shipped. TDD §14 GAP-10 proposes publishing a digest of the resolved OpenAPI document and failing the consumer gate on an unconsumed change.

---

## 20. Data design

### 20.1 D-26 — Data ownership

| Rule | Statement |
|---|---|
| **OD-1** | Exactly one bounded context writes each fact. A store is never shared, never read by another context, never joined across contexts |
| **OD-2** | An aggregator holds **no** store. Its caches are derived, TTL-bounded, and never authoritative (AC-03, D-07) |
| **OD-3** | A shell holds **no** persistent client state; a remote holds view state only |
| **OD-4** | Cross-context data movement happens through an API call in a request, or through a user's explicit action. There is no batch, no replica, no shared read model in v3.0.0 |

OD-4 is the one that gets argued about, so its cost is stated: **a page that genuinely needs data from four contexts pays four context round trips inside one aggregator request.** That is the deliberate trade of D-25 (no events, no projections). The aggregator's job is to make those four calls *parallel and budgeted* (ALG-3), not to avoid them.

### 20.2 Logical model — the `banner` exemplar

NG-08 scopes Clean Architecture to one context; the data model needs the same discipline, so exactly one context is modelled, as a worked example for templates (FR-12).

```
Aggregate root:  BannerPlacement
  identity       placementId (UUIDv7)
  invariant 1    a placement has exactly one banner and one slot
  invariant 2    (slot, window) is unique per placement        ← enforced in the aggregate, not the schema alone
  invariant 3    a placement cannot be active outside its window
  state          status: draft | scheduled | active | archived     ← derived from window + now(), never stored twice

Value objects:   BannerRef(id, revision)   Slot(name)   TimeWindow(start, end, tz)
  TimeWindow is the only place time is interpreted; `tz` is stored, never assumed
  BannerRef is a reference, not a copy — a banner's text belongs to another aggregate

Entities (same context, separate aggregates)
  Banner(id, name, contentDocument, revision, status)
  Channel(id, name)
  RotationPolicy(id, strategy, cadence)

Repositories (interfaces in domain/, implementations in adapters/outbound/)
  BannerPlacementRepository   findById / save (optimistic lock on version) / queryOverlaps(window, slot)
  BannerRepository            findById / save
```

Three modelling rules, stated because they are what the exemplar is teaching:

1. **`status` is derived, not duplicated.** `active = now ∈ window ∧ status ≠ archived`. Storing it would create two sources of truth and a nightly repair job. Deriving it costs one comparison and removes an entire class of bug.
2. **References stay references.** `BannerRef` carries an id and a revision, not a title. Copying display data into a placement is the most common way a bounded context quietly becomes a reporting database.
3. **Uniqueness that spans aggregates is not a database constraint.** `(slot, window)` uniqueness is a rule of the placement aggregate and is checked in the domain; a unique index is a *second* enforcement for race safety, not the definition. If the two ever disagree, the PRD's dependency rule applies to data as well as code: the aggregate decides.

### 20.3 Schema evolution

| Change | Allowed | Mechanism |
|---|---|---|
| Add a nullable column | yes | deploy before any writer emits it |
| Add a NOT NULL column | yes, in two steps | (1) add nullable + backfill, (2) add the constraint after all writers are updated |
| Rename | no | expand (`old_name` + `new_name`), dual-write, contract (drop `old_name`) |
| Drop | no, directly | expand/contract with the deprecation window of ROW-04 |
| Change a type | no, directly | new column, dual-write, backfill, cut over, drop |
| Add an index concurrently | yes | must not take a write lock on a live table |

**Migrations run only inside a context service** — AC-03 makes an aggregator migration-free by construction, so there is exactly one place in the system where schema changes happen, and it belongs to the team that owns the data.

**Backward-compatible readers are mandatory.** An API must be able to serve a client that is N releases old. A context that breaks its own old readers has broken ROW-04's deprecation promise, which is the same violation as removing a field early.

### 20.4 Read and write paths

```
WRITE   remote → context API → authz → aggregate (invariant check) → repository → store
                                                     │ transaction boundary (application/)
                                                     └ optimistic version check; conflict → 409

READ (direct)    remote → context API → authz → repository → store → DTO (domain DTO, unmodified)
READ (composed)  aggregator → context API ×N → DTO → page section
                        └ cache-aside at the aggregator: key = (context, resource, ids, subject-scope)
                                                     TTL from BUD ledger; single-flight on hot keys

DERIVED          nothing is persisted outside its owning context. The aggregator's cache is the only
                 derived store in the system, and it is reconstructible by definition.
```

**Cache correctness rules:** the cache key includes everything that can change the answer — including the tenant and the subject's scope, never just the resource id; TTLs come from `catalog/budgets.yaml`, not from code constants; single-flight (request coalescing) is enabled only on keys with measured read amplification (PERF-11).

### 20.5 Data classification and lifecycle

| Class | Examples | Rule |
|---|---|---|
| **Public** | banner copy, channel names, rotation policy | cacheable, no TTL floor |
| **Internal** | schedules, drafts, audit counters | never in client-visible cache keys |
| **Personal** | user identity, session references, viewing history | never in logs, never in a shared cache key, never in an analytics payload without a decision record |

**Erasure across contexts is per context and explicit.** A right-to-delete request becomes N context operations, one per context that holds personal data about the subject, each authorised and each audited. There is no cross-context delete transaction (D-25); the coordination is an operational job with a completion criterion, and pretending otherwise would be the worse error.

**Retention** is declared per field in `catalog/budgets.yaml` alongside the other budgets, so it is reviewed on the same cadence as a performance threshold rather than being set once in a document nobody re-reads.

### 20.6 Data observability

- Every context emits: query-count and p99 per operation, N+1 detector (PERF-08), and slow-query logging with the correlation id.
- **The aggregation layer emits the most and is the most likely to be ignored** — which is why BUD-05 exists as a *number* rather than as a principle.
- Data-quality invariants (uniqueness, referential completeness) are asserted where they are enforced, and their violation is an alert, not a log line.

---

## 21. Technology stack

### 21.1 D-27 — Every technology choice carries five fields

A choice without all five is not a decision; it is an inherited default. `{choice, pin, why (cited), rejected alternative, revisit trigger}`.

| Concern | Choice | Pin | Why | Rejected | Revisit trigger |
|---|---|---|---|---|---|
| Language runtime | Node.js LTS | `devenv.lock` + `devenv.yaml` `inputs` | single runtime across shell, remotes, aggregator and services; `NODE_ENV=production` in every deployed env (DIR-03, R-BE-15) | Deno/Bun as runtime | a measured startup or memory win on our routes (RES-07 methodology) |
| Package manager | Bun | `packageManager` field + single root lockfile (RES-01) | one lockfile, fast deterministic install | npm/pnpm/yarn — a second lockfile is a violation, not a preference | install time SLO missed two quarters running |
| Task graph + cache | Turborepo | `turbo.lock` | affected-based selection; `boundaries` tags (R-BND-12) | Nx (adds a second graph) | cache-hit SLO missed two consecutive quarters (RES-08) |
| Bundler | Rsbuild / Rspack | `packageManager` | MF support with the published optimisation flags; RES-07 mandates *measuring* memory, not asserting it | Vite (equivalent MF surface exists, R-MF-23; chosen only on measured build time) | two consecutive quarters of build-time regression with no cache explanation |
| Module composition | Module Federation 2.x | exact version in the shared manifest | runtime integration; build-time integration explicitly rejected (R-MFE-01) | qiankun / single-spa / Web Components | ≥ 5 remotes and PERF-05 fails |
| UI framework | React | exact version in the generated `shared` manifest | required `singleton` semantics (MF-5, R-MF-03) | any second framework (two singletons in one page is a defect, not a preference) | never, absent a new client platform |
| Backend framework | NestJS on Fastify | `packageManager` | DI for port binding; singleton default scope with ADR-gated exceptions (NEST-01, R-BE-03) | Express (R-BE-01's 2× claim is vendor-originated and **not** adopted as a number) | measured p99 regression attributable to the framework |
| Schema validation | zod, `.strict()` | `packageManager` | static type inference into the generator; JSON Schema export for portability (DEC-24, R-META-31) | CUE (recorded, not adopted — R-META-30) | a second consumer needs the catalogue without a JS runtime |
| Store | PostgreSQL, one per context | image tag pin | one writer, one owner, one migration site (OD-1, §20.3) | a shared multi-tenant database (violates OD-1 outright) | a context's write pattern outgrows a relational model, with an ADR |
| API contract | OpenAPI **3.1.x** | deliberate pin (DEC-22) | a spec minor must not change validation semantics under the contract suite | tracking 3.2.x | scheduled version-bump PR (RISK-10) |
| Errors | RFC 9457 problem+json | n/a (a standard) | one error shape across gateway, aggregator and contexts | per-team ad-hoc error envelopes | never |
| Observability | OpenTelemetry (web + Node) | `packageManager` | one tracer across the federation boundary (D-19, R-MFE-25) | vendor SDK | never |
| Boundary enforcement | dependency-cruiser + ESLint | `packageManager` | file-graph and npm-dependency rules Turborepo cannot express (§13.1) | Turborepo boundaries alone | R-BND-13 ships npm deny lists **and** is verified non-experimental |
| Budget enforcement | size-limit + Lighthouse CI | `packageManager` | measures download-plus-execute, not bytes (R-PERF-19) | byte counting alone | never |
| Environment | devenv on Nix, activated by direnv | `devenv.lock` + pinned `direnvrc` sha256 | reproducible, reviewable trust decision (D-08, DEC-07, R-DV-15, R-DV-17) | `devenv hook` (invisible mutation), devbox, mise | onboarding friction measured above RISK-08's tolerance |
| Secrets | SecretSpec, pluggable backend | `secretspec.toml` | "eliminate secrets from environment variables and configuration files" (R-SCRT-01) | committed `.env` | never |
| CI | versioned reusable workflows | `@` a pinned version (R-OWN-06) | one definition per check, referenced not copied | per-repo workflow copies | never |

### 21.2 D-28 — The singleton list is closed

React, `react-dom`, the federation runtime, and `@opentelemetry/api` are the only permitted shared singletons (D-16, D-15, D-19). Adding a fifth requires:

1. a written justification naming what breaks with two instances;
2. an assertion in the shell's startup test, exactly as PERF-05 asserts React;
3. an ADR.

This is the mechanism that keeps micro-frontending from quietly becoming "share everything", which is how payload budgets die.

### 21.3 D-29 — New-dependency rule

A dependency may enter a deployable without an ADR if it is (a) transitively required by an existing one, or (b) a devDependency of a single deployable. It requires an **ADR** if it enters `shared` (runtime-wide), if it touches `domain/` (D-14), or if it is a database driver or ORM outside a context service (AC-03). Rationale: those three are the only cases where one team's choice becomes everyone's runtime cost.

---

## 22. Security design

### 22.1 D-30 — Threat model (abridged to the threats this architecture creates)

| # | Threat | Why it is specific to this design | Control | Enforced by |
|---|---|---|---|---|
| T-1 | A remote is compromised and runs with host privileges | Module Federation confers **no** isolation (R-MFE-15, R-MFE-16); RISK-01 | CSP allow-listing remote origins; remotes have no secrets, no storage authority, no privileged fetches; authorisation never depends on the client | CSP config + D-05 |
| T-2 | UI-level authorisation bypass | shell route guards and hidden controls are presentation only (D-06) | authorisation enforced per request in the context service; deny-by-default | CHK-13, ALG-5 |
| T-3 | Aggregator becomes an authorisation hole | it sits in front of every read | forwards the end-user subject opaquely; a context denies an unverifiable subject (D-05) | contract test + ADR |
| T-4 | Aggregator used by a second consumer | row 7 forbids it; AC-04 checks only code | shell-attested session; `401` before any downstream call (D-09) | integration test |
| T-5 | Cross-tenant data access | one store per context, but reads are multi-tenant | tenant in the verified claims; per-object authorisation, never tenant-from-path | contract tests |
| T-6 | Object-level over-fetch (BOLA) | aggregator reshapes payloads and can over-request | contexts authorise **per object**, not per route; consumer tests assert denial cases (R-SEC-01) | contract test suite |
| T-7 | Secret leakage | `.env` tradition, build logs, CI | SecretSpec; secrets never in `devenv.nix`, never in images, never in generated files | lint + D-08 |
| T-8 | Supply chain via a remote | `remoteEntry` is *evaluated*, so Subresource Integrity does not apply (R-MFE-17) | exact version pins (D-11); generated registry; reviewed `mf-manifest.json`; CSP origin allow-list | `pins:check`, CSP |
| T-9 | Dependency compromise | 400+ transitive packages | single lockfile, `--frozen-lockfile`, scheduled reviewable bump PRs | RES-01/02, RISK-10 |
| T-10 | Untraceable incident across remotes | N independently deployed bundles | one tracer (D-19), correlation id forwarded (INT-01) | §10.5 |

The honest statement of residual risk, repeated from RISK-01: **micro-frontending provides no browser security boundary.** T-1's controls reduce blast radius; they do not create isolation. Isolation would require iframes, which the PRD records and does not adopt (Shadow DOM is the strongest of the three, R-MFE-12, and is incompatible with the shared-singleton requirement).

### 22.2 Authentication flow

NG-06 leaves the identity provider unselected; the *contract* is specified so provider choice is a one-line change.

```
1  shell      GET /session → 401 { authenticate: "<idp-url>/authorize?…" }
2  browser    authenticates at the IdP (provider-agnostic; OIDC-shaped redirect)
3  IdP        issues an id_token / code → shell exchanges at the token endpoint
4  shell      validates signature, issuer, audience, nonce; mints an OPaque session reference
5  shell      sets Secure; HttpOnly; SameSite=Lax; Path=/ session cookie
6  browser    subsequent requests carry only the cookie; no token in localStorage, no token in JS memory
7  context    verifies the session **locally** (JWKS from the configured issuer, cached with a bounded TTL)
              → no call back to the shell, no aggregator in the auth path
```

Step 7 is the design decision that matters: **the context service verifies the caller itself.** The alternative — contexts asking the shell or aggregator who the user is — would put the composition tier in the authorisation path, which D-02 and D-05 exist to prevent. Access tokens follow RFC 9068 (R-INT-02) so a resource server can validate without bespoke code.

| Property | Design |
|---|---|
| Session storage | server-side, opaque reference; cookie holds no claims |
| Token lifetime | access short (minutes), refresh rotated on use; revocation list checked with a bounded TTL |
| CSRF | `SameSite=Lax` + a double-submit token on mutating requests, because the aggregator and contexts are cookie-authenticated |
| Storage | nothing sensitive in `localStorage` or `sessionStorage`; a remote compromised by XSS gains a *session*, not a token it can exfiltrate and replay elsewhere |
| Logout | clears the server-side session; every context denies on next verification |

### 22.3 Authorisation

- `@cms/authz` provides the **claim format and an evaluator interface only** — no decision logic, no organisation-specific conditions (FR-20, ROW-03). A lint asserts the package exports zero executable policy functions.
- Decisions are made **in the context service, per request, per operation, per object, per tenant** (D-06). "Per request" is what CHK-13 asserts: every inbound route either references an authz port or declares `public: true` with an ADR (GAP-11).
- The decision is **deny-by-default** and **fail-closed**: an unreachable policy engine is a denial, not an allow.
- Decisions are logged with correlation id, subject, operation, resource, outcome — an audit trail, not a debug log.

### 22.4 Encryption and key handling

| Layer | Control |
|---|---|
| In transit, browser → edge → gateway → services | TLS 1.3; HSTS; internal hops mTLS where the platform provides it |
| Cross-origin telemetry | `traceparent` requires explicit CORS allow-listing (R-MFE-25) — treated as a data egress decision, not a debugging convenience |
| At rest, stores | provider-managed encryption; backups encrypted with separate keys |
| Secrets | resolved by SecretSpec at run time from a pluggable backend; never committed, never in an image layer, never in a generated file (D-08) |
| Key rotation | platform-owned, on a declared cadence; rotation is a deployable event, not a manual step |
| Client storage | no persistent client-side storage of domain data beyond view state; nothing cached in `localStorage` that a remote could read cross-route |

### 22.5 Security controls that are *not* claimed

Stated explicitly so no document repeats them later: no isolation between remotes (RISK-01); no SRI on remotes (R-MFE-17); no route guard as a control (D-06); no ownership relation used for runtime authorisation (R-META-27 — ownership exists for routing review and display, explicitly "not to be used by automated processes … to assign authorization in runtime systems").

---

## 23. Deployment architecture

### 23.1 D-31 — Environments and what varies between them

| Environment | Provisioned by | Config source | Secret source | Purpose |
|---|---|---|---|---|
| Local | `devenv up` (devenv.nix) | `devenv.local.*`, gitignored | SecretSpec, developer profile | full stack, reproducible |
| CI | devenv shell + workflows | committed defaults | CI provider's store, injected once | checks, budgets, contract verification |
| Preview | **generated from the catalogue**, one deployable set per PR | per-deployable preview values | ephemeral, single-use | review a change in the real topology |
| Staging | production-shaped, reduced replicas | same schema as prod | staging profile | load, migration rehearsal, rollback rehearsal |
| Production | — | delivered as env (12-factor) | production profile | — |

The invariant across all five: **the same artefact is promoted; nothing is rebuilt.** Build once (PH-9's B3 independence makes this possible), promote the same image, change only config and secrets. Twelve-factor's build/release/run separation is what makes "roll back" a pointer change rather than a rebuild (R-DEP-01).

NG-04 excludes *provisioning* these environments. It does not exclude specifying them: a budget with no topology to attach to is not enforceable.

### 23.2 D-32 — The deployable set is catalogue-derived

```
catalog/contexts/*.yaml   → context service image   + store (per context)
catalog/clients/*.yaml    → shell artefact (static) + aggregator image
catalog/interfaces/*.yaml → rollout order constraints
```

- **Release independence is real**: one commit may produce many releases; each deployable has its own pipeline, its own version, its own rollback.
- **Rollout order is derived, not remembered**: a context API is rolled out *before* any consumer that depends on a new version of its contract, and *after* consumers have finished migrating away from a deprecated field. The order comes from the interface rows' `breakingChangePolicy`.
- A preview environment contains **only** the deployables the PR touched plus their declared dependencies — which is the metadata paying for itself.

### 23.3 D-33 — Asset delivery: hashed assets, stable manifest

MF-6 (`contenthash` filenames) and MF-7 (remotes redirectable without a rebuild) pull in opposite directions: if the shell embedded remote content hashes, every remote deploy would force a shell rebuild. Resolution:

| Artefact | Naming | Cache | Notes |
|---|---|---|---|
| shell + remote JS/CSS chunks | `[name].[contenthash:8].js` | `immutable`, 1 year | MF-6 |
| `remoteEntry` | content-hashed | `immutable`, 1 year | referenced by hash |
| **remote manifest** (name → hashed entry, exposes, shared versions) | **stable path, `no-store` (or max-age seconds)** | never immutable | the only thing the shell fetches at boot |
| federation runtime file | stable path, short TTL | — | provided once by the shell (D-15) |

The shell's boot sequence reads the manifest, not a build-time hash. Consequence: **a remote can ship without any shell change** — which is the entire point of DEC-06 — and PERF-04's no-speculative-preload rule is enforced by the manifest not listing assets for routes not being visited. `manifest.disableAssetsAnalyze` stays unset (MF-2) because disabling it disables preload entirely.

This is GAP-14: the PRD specifies both MF-6 and MF-7 without stating the mechanism that makes them compatible.

### 23.4 Scalability and availability

| Component | Scaling model | Autosignal | Floor | Ceiling |
|---|---|---|---|---|
| Shell / remotes | CDN; no origin compute | — | — | — |
| Aggregator | horizontal, stateless | CPU + in-flight requests | 2 (no single instance) | per-request budget × concurrency (PERF-09 bulkhead) |
| Context service | horizontal, stateless | CPU + p99 | 2 | store connection pool |
| Store | managed, per context | storage / IOPS | — | — |

Availability targets are **per availability class** from §18.1, not global:

| Class | Meaning | Target | Degradation |
|---|---|---|---|
| A | edge, gateway, IdP | highest; outage = total outage | CDN serves a cached shell; gateway fails closed |
| B | aggregator, context service | high; outage = feature loss | partial responses (INT-02); breaker + retry budget (PERF-09) |
| C | one remote | isolated | region fallback (D-17); the rest of the app unaffected |

**Explicit non-claims:** no multi-region active-active is designed here (it would be a cost decision with no requirement behind it); no DR design is proposed beyond "the store's own backup policy, tested by restore rehearsal" — RTO/RPO are declared per store, measured by rehearsal, and are not invented in this document.

### 23.5 Configuration, secrets and cost

- Config is delivered, never baked: an image is valid in every environment because its config is external (12-factor config, R-CFG-01).
- Secrets are resolved by SecretSpec at start-up; an unresolved secret **terminates the process before it binds a socket** (FR-16, AC-09). Failing closed at boot is the difference between an outage and a silent misconfiguration.
- **Cost attribution is generated**: image tags, resource names and cost-centre labels come from the catalogue (RES-10), so FinOps allocation needs no manual tagging discipline.

### 23.6 Rollback

| Change | Rollback | Time |
|---|---|---|
| shell / remote | revert the manifest entry (or re-point to the previous hash) | seconds |
| aggregator / context image | revert to the previous image tag | one rollout |
| config | revert the config change | one rollout, no rebuild |
| **schema** | **cannot be rolled back by reverting the app** — this is why §20.3 is expand/contract only | migrations are forward-only by construction |

The last row is the reason the schema rules are the strictest in this document: an expand-only schema is what makes every other rollback safe.

---

## 24. Detailed technical design

Module specifications a developer implements against. Each states responsibility, contract, failure modes and test. **If a module is not in this section, it is not part of the design.**

### MOD-1 — `catalog/schema/*.schema.ts`

- **Responsibility**: the sole definition of catalogue document shapes; every object `.strict()`.
- **Contract**: exports zod schemas + inferred types; consumed by the generator, the validator and the template runner.
- **Failure**: any unknown key → error naming the exact key path (FR-02).
- **Test**: property test that mutating each document with one unknown key fails; and that a valid document parses.

### MOD-2 — `teams/platform/generator` (pipeline)

- **Responsibility**: catalog → the 10 artefact classes of §8.2, byte-stably.
- **Contract**: `catalog:generate [--check] [--format=json]`; exit 0/1/2 per §3.2.
- **Failure**: validation error → nothing is written (all-or-nothing, so a failed run cannot half-update a repo); byte-stability violation → exit 1.
- **Test**: the golden test — generate, `git diff --exit-code`, generate again, assert mtimes unchanged (S6).

### MOD-3 — Shell bootstrap sequence (ordered, failure-isolated)

```
 1  load @cms/composition types only              (no domain code; AC-05)
 2  install the tracer once, publish the guarded global        (D-19)
 3  assert the React singleton count                              (PERF-05)
 4  fetch the remote manifest (stable path, short TTL)           (D-33)
 5  publish the federation runtime                               (D-15, GAP-03)
 6  register the generated route map                             (D-06/FR-08)
 7  resolve session → /session on the aggregator
 8  render chrome
 9  on navigation: dynamic-import the remote for the route only
10  mount inside the route's error boundary                      (D-17)
```

Steps 2, 3 and 5 are startup assertions: if any fails, the shell renders a *chrome-only* degraded mode and reports the failure, rather than booting into a page whose invariants are already broken.

### MOD-4 — Remote mount contract

| Element | Contract |
|---|---|
| Entry point | `exposes: { './App': … }` — exactly one entry (AC-05: internals are never imported) |
| Props in | `{ session: SessionSummary, section?: <ctx>Section, route: OpaqueRouteSegment }` — the remote cannot construct a `RouteSegment` (D-03) |
| Props out | `{ onNavigate(target: OpaqueRouteSegment), onError(problem: Problem) }` — navigation goes *through the shell*, never by mutating the URL itself |
| Data | its own context API only; never the aggregator (RISK-01) |
| Styling | consumes `@cms/ui`; ships no global stylesheet (D-18) |
| Lifecycle | `mount(el)` / `unmount()`; the shell guarantees `unmount` on route change so a remote cannot leak listeners |
| Failure | throw at any point → the boundary catches; the shell's fallback renders (D-17) |

### MOD-5 — Federation config builder

- **Responsibility**: emit the bundler config of §10.1/D-15 **from the catalogue**, so a hand-edited config is a diff failure.
- **Inputs**: `contexts/*.yaml#provides.ui.web`, the resolved shared manifest, the environment (`dev` | `prod`).
- **Deviation rule**: `disableSnapshot` is `true` in prod and `false` in dev, because it costs HMR and type sync (R-MF-21, GAP-02). The switch is environment-derived, not hand-set.
- **Test**: asserts `shareStrategy === 'loaded-first'`, `disableAssetsAnalyze` absent, `disableShared === false` with non-empty `shared` — the three misconfigurations that silently cost bytes or instances.

### MOD-6 — Aggregator pipeline (middleware order is normative)

```
1  correlation id      (mint if absent, else forward)        INT-01
2  trace               (extract incoming context)           D-19
3  config              (already validated at boot)          FR-16
4  session attestation (401 before any downstream call)      D-09
5  deadline            (compute the plan's budgets)         ALG-3
6  cache-aside         (TTL from budgets, single-flight)     PERF-11
7  per-request loader  (created here, never shared)         PERF-08
8  breaker + bulkhead  (per dependency)                     PERF-09
9  fan-out             (parallel; no gratuitous Sequence)   PERF-07
10 assemble            (per-section status; problem+json)   INT-02
11 metrics             (per-node histogram, per-request)    PERF-06, PERF-10
```

Order is load-bearing: attestation before planning (never spend a downstream call on an unauthenticated request), deadline before execution (budgets must exist before they can be exceeded), loader per request (a shared loader is a correctness bug, not an optimisation).

### MOD-7 — Bounded-context API template (what FR-12 scaffolds)

| Module | Contains | May import |
|---|---|---|
| `domain/` | entities, value objects, domain services, repository interfaces | **nothing outside `domain/`** |
| `application/` | use cases; each declares its own ports | `domain/` |
| `adapters/inbound/` | controllers, mapping, error translation | `application/`, `domain/`, framework |
| `adapters/outbound/` | repositories, clock, ids, external clients | `application/`, `domain/`, framework |
| `config/config.schema.ts` | strict env contract | zod |
| `main.ts` | **the only** port↔adapter binding | everything |

The scaffold compiles, lints and passes `check:boundaries` with zero manual edits (RES-05a, ≤ 60 s), and its first commit already contains the consumer test skeleton for its own contract.

### MOD-8 — Config and boot module

1. parse env strictly → fail closed with the offending key;
2. verify secrets resolvable via SecretSpec → fail closed;
3. build the dependency graph from the catalogue (ROW-10);
4. bind ports to adapters (`main.ts`);
5. **only now** bind the socket;
6. emit a `startup` metric with version, config digest and commit.

Step 6 exists so a deployment can be attributed to a build without reading logs.

### MOD-9 — Contract harness

```
provider side:  publish openapi.yaml + its digest
consumer side:  generate the adapter from the schema; write expectations as executable examples;
                run against the provider's PUBLISHED schema in CI (INT-05);
                assert both success and denial cases (R-SEC-01 BOLA)
```

### MOD-10 — Check harness (`tools/checks`)

Shared library so every `check:*` behaves identically: same argument parsing, same `--format=json`, same exit codes (§13), same fixture runner. A check written outside the harness is not merged — its exit-code semantics would be unverified.

### 24.1 Module dependency rule for the platform itself

The generator, the checks and the templates are ordinary workspace packages and obey the same rule as everything else: they depend on `@cms/ui`/`@cms/composition` where relevant, never on a deployable, and their tests are in the same package. The platform team has no exemption from AC-01; if it did, the enforcement would be theatre.

---

## 25. Traceability for Part II

| View | Primary PRD clause | Design sections | Checks |
|---|---|---|---|
| Solution architecture | §4, §5, §6, D-01…D-06 | §18, §4 | CHK-01, CHK-04, CHK-07 |
| Integration design | D-02, D-03, D-05, D-06, FR-23 | §19, §5.4, §6.4 | CHK-06, CHK-13, CHK-15 |
| Data design | D-03, AC-03, FR-16, PERF-08, PERF-11 | §20 | CHK-06, CHK-15 |
| Technology stack | NG-11, MF-1…MF-9, DEC-07, DEC-22, DEC-24 | §21 | CHK-09, CHK-17 |
| Security design | D-05, D-06, RISK-01, RISK-02, FR-20 | §22, §5.5, §10.1 | CHK-13, CHK-16, CSP assertion |
| Deployment architecture | B3, PERF-11, PERF-12, RES-09, RES-10 | §23 | CHK-17, CHK-21 |
| Detailed technical design | FR-12, FR-16, FR-19, FR-22 | §24 | CHK-05, CHK-08, CHK-14 |

### 25.1 GAP-14 — added by Part II

| GAP | Finding | Resolution | ADR / phase |
|---|---|---|---|
| **GAP-14** | MF-6 (`contenthash` filenames) and MF-7 (remotes redirectable **without a rebuild**) are incompatible as written: a shell embedding remote content hashes must be rebuilt on every remote deploy, which destroys the independence DEC-06 exists to buy. | D-33: hashed assets + a **stable, non-immutable remote manifest** that the shell reads at boot. The shell's build embeds remote *contracts* (names, exposes, shared versions) and never remote content hashes | ADR-0024 / PH-6 |
