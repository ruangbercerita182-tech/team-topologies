# Verified Reference Catalogue — CMS Platform Architecture

| Field | Value |
|---|---|
| Document ID | REF-CMS-001 |
| Version | 3.0.0 |
| Status | Active |
| Date | 2026-10-14 |
| Supersedes | REF-CMS-001 v1.0.0 (carried ~150 refs) |
| Consumed by | `docs/PRD.md` (PRD-CMS-001 v3.0.0) |
| Total references | 403 admissible (379 clean VERIFIED + 24 PARTIAL with a stated limitation) — 379 as of v3.0.0, +24 added by §R-25 for TDD-CMS-001 |
| Consumed also by | `docs/TDD.md` (TDD-CMS-001 v1.0.0) |
| Rejected (never cite) | 77 (66 in the R-23 table + 11 carried as numbered R-xx entries) |

> **Section index.** R-1 Team Topologies · R-2 DDD · R-3 SOLID · R-4 Clean Architecture · R-5 Repository topology · R-6 Metadata · R-7 Dev environment · R-8 Aggregator/BFF · R-9 GraphQL federation · R-10 Contracts · R-11 Resilience · R-12 Micro-frontends · R-13 Module Federation · R-14 Web perf budgets · R-15 Backend efficiency · R-16 Build/CI efficiency · R-17 Boundary enforcement · R-18 Configuration · R-19 Ownership · R-20 Cost allocation · R-21 BFF boundary · R-22 Platform-scope policy · R-23 Rejected · R-24 Maintenance · **R-25 Addendum (TDD-CMS-001)**.
>
**Verification rule.** Every reference below was retrieved by HTTP and its content read on 2026-10-14. A reference is admissible in the PRD only if it appears here with status `VERIFIED`. Any URL added after this date must be verified and added here *before* it is cited anywhere (PRD §20.2).

**Status vocabulary.**

| Status | Meaning |
|---|---|
| `VERIFIED` | URL resolves and content confirms the stated claim. |
| `PARTIAL` | URL resolves but the claim is only partly supported; the limitation is stated inline. |
| `REJECTED` | 404, 403, dead domain, misattributed, or the claim does not exist. Listed in §R-9 with a substitute. **Never cite.** |

**Attribution corrections carried by this catalogue.** These are frequently miscited and must be corrected wherever they appear:

| Commonly miscited as | Correct |
|---|---|
| Martin Fowler / "Martijn Foster" — *Micro Frontends* | **Cam Jackson**, martinfowler.com, 19 Jun 2019 (R-MFE-01) |
| micro-frontends.org — Cam Jackson | **Michael Geers**, neuland, 2017 (R-MFE-02) |
| Martin Foster — Consumer-Driven Contracts | **Ian Robinson** (Thoughtworks) for Martin Fowler (R-CDC-01) |
| Sam Newman — *Microservices Anti-Patterns* | That book does not exist. **Chris Richardson** (R-BFF-24), **Mark Richards** (R-BFF-25), Taibi/Lenarduzzi/Pahl (R-BFF-26) |
| Brian Foote — *Solid Considered a Harmful* | **No such article exists.** Widely circulated misattribution (R-SOLID-09) |
| Martin Fowler — *MonolithMacro* bliki | **No such page.** Common hallucination (R-MONO-09) |
| Evan Luton — *ruthlessly monorepo* | Article is real but **no fetchable canonical URL survives** (R-MONO-12) |
| Jetify — `secretspec` | **Cachix** maintains SecretSpec (`org.cachix.secretspec`) (R-SCRT-01) |
| teamapi.dev — the Team API standard | **Third-party, unaffiliated.** No official Team API spec exists (R-TTA-01) |
| OpenAPI "latest" = 3.1.0 | Live latest is **3.2.1**; this PRD pins **3.1.x** deliberately (R-META-12) |
| AsyncAPI "latest" = 2.x | Live latest is **3.1.0** (R-META-14) |
| `eslint-plugin-boundaries` — `Nick-vv/...` | **javierbrea/eslint-plugin-boundaries** (R-BND-03) |
| `import-linter` — `sbidoul/...` or `siddharthkp/...` | **seddonym/import-linter** (R-BND-05) |
| MF `shareStrategy: 'eager'` | Options are `'version-first'` (default) and `'loaded-first'`; `eager` is a per-entry `shared` flag (R-MF-20) |
| Domain `modulefederation.io` | **`module-federation.io`** (hyphen). The unhyphenated domain does not resolve |
| Bun vs pnpm disk "benchmarks" | Both are **vendor architectural claims with no published benchmark** (R-BUILD-22, R-BUILD-23) |

---

## R-1 Team Topologies, team types, cognitive load, interaction modes

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-TT-01 | Key Concepts | Skelton & Pais / Team Topologies Ltd | https://teamtopologies.com/key-concepts | Four fundamental team types, three interaction modes, cognitive load as the design axis, thinnest viable platform |
| R-TT-02 | What are the core team types in Team Topologies? | Team Topologies | https://teamtopologies.com/key-concepts-content/what-are-the-core-team-types-in-team-topologies | Canonical definitions of stream-aligned / enabling / complicated-subsystem / platform; platform as fractal Russian-doll nesting |
| R-TT-03 | Team Interaction Modeling with Team Topologies | Team Topologies | https://teamtopologies.com/key-concepts-content/team-interaction-modeling-with-team-topologies | Interaction-mode selection rules; "stream-aligned teams should generally never provide an X-as-a-Service directly"; flow-of-change left-to-right; implied handshake between teams on the same y-axis |
| R-TT-04 | Finding good stream boundaries with Independent Service Heuristics | Team Topologies | https://teamtopologies.com/key-concepts-content/finding-good-stream-boundaries-with-independent-service-heuristics | ISH as the boundary-finding method; fracture planes as workshop input |
| R-TT-05 | How to use the Team Topologies Modeling Shapes | Team Topologies | https://teamtopologies.com/how-to-use-shapes | Eight shaping principles incl. the fractal nature of flow |
| R-TT-06 | Monoliths vs Microservices is Missing the Point — Start with Team Cognitive Load | Skelton & Pais, DOES/EM 2019 | https://teamtopologies.com/videos-slides/2019/07/10/monoliths-vs-microservices-is-missing-the-point-start-with-team-cognitive-load-does-eur-2019 | **TT's own statement that monolith-vs-microservices is the wrong axis and cognitive load is the right one** |
| R-TT-07 | Team Topologies, 2nd Edition — product page | Skelton & Pais / IT Revolution | https://itrevolution.com/product/team-topologies/ | Current edition (2025); book record |
| R-TT-08 | Rebuilding and scaling product development at Docker | Team Topologies case study | https://teamtopologies.com/industry-examples/rebuilding-and-scaling-product-development-at-docker-using-team-topologies | Fracture-plane adoption in practice. `PARTIAL` — full text contains no repository-topology discussion; cited for fracture planes only |
| R-TT-09 | Evolving teams and software at Wealth Wizards | Team Topologies case study | https://teamtopologies.com/industry-examples/evolving-teams-and-software-at-wealth-wizards-using-team-topologies | Workflow: visualise logical components → find fracture planes → map to business domains → re-align teams. Boundaries derived from domain, not from repository shape |
| R-TT-10 | Team Topologies — home | Team Topologies | https://teamtopologies.com/ | Project home; 2e status |
| R-TT-11 | Team Cognitive Load Assessment (instrument) | Team Topologies | https://github.com/TeamTopologies/Team-Cognitive-Load-Assessment | The official cognitive-load instrument. **Contains no repository question** — cited as evidence that repo topology is not a cognitive-load dimension |
| R-TT-12 | Team-Dependencies-Tracking | Team Topologies | https://github.com/TeamTopologies/Team-Dependencies-Tracking | Dependency tracking keyed on team dependencies and artefacts, not repositories |
| R-TT-13 | Team Topologies Community Materials | Team Topologies | https://github.com/TeamTopologies/Team-Topologies-Community-Materials | Community bibliography; documents the sparseness of monorepo-vs-polyrepo material inside the TT ecosystem |
| R-TT-14 | *Team Topologies*, Part I excerpt (Ch. 1–2, Conway's Law) | Skelton & Pais, via InfoQ | https://res.infoq.com/articles/book-review-team-topologies/en/resources/TTOP_excerpt_InfoQ-1572531146315.pdf | **Load-bearing negative evidence:** 3,177 extracted lines contain **zero** occurrences of "monorepo", "repository", or "repo". The foundational framing is team-first, never repo-structural |
| R-TT-15 | *Topologies* excerpt (chapter list + conclusions) | Skelton & Pais, via IT Revolution | https://itrevolution.com/wp-content/uploads/2022/06/TTOP_excerpt.pdf | Chapter map: Ch. 5 four topologies, Ch. 7 interaction modes, Ch. 8 architecture for participation. Reverse-Conway framing |
| R-TT-16 | Independent Service Heuristics (full checklist) | Team Topologies (CC BY-SA) | https://github.com/TeamTopologies/Independent-Service-Heuristics | **Load-bearing negative evidence:** the 10-item ISH checklist contains no repo-boundary heuristic. Teams heuristic = "would cognitive load be bounded?"; Dependencies = "act independently of other teams" |
| R-TTA-01 | TeamAPI | **teamapi.dev — third party, unaffiliated** | https://teamapi.dev/ | Open-source Team API tooling. **No official Team API specification exists.** Cited with this caveat, never as a standard |
| R-TTA-02 | Team Topologies Key Concepts (official) | Team Topologies | https://teamtopologies.com/key-concepts | The only vendor-official source for team-type vocabulary. Used in place of a Team API spec |

---

## R-2 Domain-Driven Design

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-DDD-01 | *Domain-Driven Design: Tackling Complexity in the Heart of Software* | Eric Evans / Addison-Wesley | https://www.pearson.com/en-us/subject-catalog/p/domain-driven-design-tackling-complexity-in-the-heart-of-software/P200000003550/9780321125217 | **Primary source** for Bounded Context (§2), Ubiquitous Language (§1), Aggregate (§5), Context Map (Part II). The citable form of Evans's definitions |
| R-DDD-02 | Context Maps | Eric Evans / Domain Language | https://www.domainlanguage.com/2003/04/context-map/ | Context Map essay; supports ACL/wrapper reasoning |
| R-DDD-03 | *Implementing Domain-Driven Design: Architectures That Scale* | Vaughn Vernon / Addison-Wesley | https://www.pearson.com/en-us/subject-catalog/p/implementing-domain-driven-design-architectures-that-scale/P200000002979 | Aggregates, repositories, application services, ACLs, strategic design process |
| R-DDD-04 | The Independent Service Heuristics | Team Topologies | https://github.com/TeamTopologies/Independent-Service-Heuristics | The operational boundary-finding checklist complementing DDD heuristics |

---

## R-3 SOLID — primary sources

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-SOLID-01 | DIP: The Dependency Inversion Principle | Robert C. Martin / Object Mentor | https://objectmentor.com/resources/articles/dip.pdf | **Primary source of DIP.** "High-level modules should not depend on low-level modules; both should depend on abstractions; abstractions should not depend on details." ~1996–2003 |
| R-SOLID-02 | SRP: The Single Responsibility Principle | Robert C. Martin / Object Mentor | https://objectmentor.com/resources/articles/srp.pdf | **Primary source of SRP.** Responsibility = "a reason for change"; cohesion via DeMarco, Page-Jones, Meyer 1992. 1999/2002 |
| R-SOLID-03 | OCP: The Open-Closed Principle | Robert C. Martin / Object Mentor | https://objectmentor.com/resources/articles/oclp.pdf | **Primary source of OCP.** Open for extension, closed for modification |
| R-SOLID-04 | LSP: The Liskov Substitution Principle | Robert C. Martin / Object Mentor | https://objectmentor.com/resources/articles/lsp.pdf | Martin's restatement with Rectangle/Square violations; credits Liskov, *Programming With Abstract Data Types*, CONPAS 1974 |
| R-SOLID-05 | ISP: The Interface Segregation Principle | Robert C. Martin / Object Mentor | https://objectmentor.com/resources/articles/isp.pdf | Martin's statement of ISP (terminology originates in a 1986 Meyer talk) |
| R-SOLID-06 | The Single Responsibility Principle (2014 restatement) | Robert C. Martin / Clean Coder | https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html | Full text: "each software module should have one and only one reason to change"; "This principle is about people"; traces to Parnas 1972 and Dijkstra 1974 |
| R-SOLID-07 | The Open Closed Principle (2014 restatement) | Robert C. Martin / Clean Coder | https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html | 2014 SOLID series restatement |
| R-SOLID-08 | SOLID Relevance (author's response to criticism) | Robert C. Martin / Clean Coder | https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html | **The correct way to present SOLID's limits:** the author's own qualification, not a critic's strawman |
| R-SOLID-09 | *Solid Considered a Harmful* | **attributed to Brian Foote** | — | **REJECTED — the article does not exist.** `brianfoote.blogspot.com/2003/06/solid-considered-a-harmful.html` → 404; no Wayback snapshot; Foote's blog root has no such post. **Use R-SOLID-08 instead** |
| R-SOLID-10 | Big Ball of Mud (PLoP '97) | Brian Foote & Joseph Yoder, UIUC | https://www.plopcon.org/pastplops/plop97/abstracts/foote.txt | **The real, citable Patterns-community criticism** of layered/integration-heavy architecture. Use this where SOLID-criticism is needed |
| R-SOLID-11 | *Design Patterns: Elements of Reusable Object-Oriented Software* | GoF / Addison-Wesley | https://www.pearson.com/en-us/search/All-results?aq=design%20patterns%20elements%20of%20reusable%20object%20oriented%20software | Ch. 2 "Design Principles in GoF" uses Martin's "depends on / used by" inversion notation, adjacent to DIP layering |
| R-SOLID-12 | *Agile Software Development: Principles, Patterns, and Practices* | Robert C. Martin / Prentice Hall | https://www.pearson.com/en-us/subject-catalog/p/agile-software-development-principles-patterns-and-practices/P200000002797 | Ch. 11 carries DIP as Martin published it — the citation Cockburn himself uses |
| R-SOLID-13 | On the Criteria to Be Used in Decomposing Systems into Modules (CACM 15(12)) | David L. Parnas | DOI 10.1145/361598.361623 | **Origin of module-boundary reasoning.** `PARTIAL` — ACM returns 403 to automated clients; cite the DOI as identifier, not the URL |

---

## R-4 Clean Architecture, Hexagonal, layering

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-CA-01 | The Hexagonal (Ports & Adapters) Architecture (HaT TR 2005.02) | Alistair Cockburn | https://alistair.cockburn.us/hexagonal-architecture/ | **Primary source.** Inside/outside asymmetry rule; critique of 3-layer drawings ("people tend not to take the 'lines' seriously"); primary vs secondary adapters; ports named by purpose not technology; use cases at the inner boundary. Cites Martin's DIP and Fowler's DI |
| R-CA-02 | The Clean Architecture | Robert C. Martin / Clean Coder | https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html | 2012 statement (originally *Craftsman*). **Load-bearing: "the framework is an adapter, not an architecture"** |
| R-CA-03 | Screaming Architecture | Robert C. Martin / Clean Coder | https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html | Source-tree structure should name the domain, not the framework. Basis for the `domain/` layer being first-class |
| R-CA-04 | *Clean Architecture: A Craftsman's Guide to Software Structure and Design* | Robert C. Martin / Prentice Hall | https://www.pearson.com/en-us/subject-catalog/p/clean-architecture-a-craftsmans-guide-to-software-structure-and-design/P200000009284 | Ch. 7 SRP, Ch. 8 OCP, Ch. 9 LSP, Ch. 10 ISP, Ch. 11 DIP, Ch. 12–13 Dependency Rule and Circle of Dependencies |
| R-CA-05 | *Domain-Driven Design Reference* | Eric Evans / Domain Language | https://www.domainlanguage.com/ | Evans's own site. **Do not cite sub-paths** — `/2003/04/the-ddd-reference/` etc. all 404 |
| R-CA-06 | Practicing SOLID in TypeScript | Kamil Grzybek | https://kgrzybek.github.io/solid-principles/ | TypeScript worked examples of constructor-boundary dependency inversion. `PARTIAL` — widely-mirrored `ams360.com` copy is dead (DNS 000) |
| R-CA-07 | Modules are not a thing | — | — | **REJECTED — no such citation needed.** Layering here is grounded in R-CA-01 and R-CA-02, not in "modular monolith" advocacy |

---

## R-5 Repository topology: monorepo, polyrepo, and why the framing is wrong

This section carries the evidence base for PRD §1 (three separable boundaries) and §2 (DEC-01). It is the most heavily corrected section of this catalogue.

### R-5a — Evidence that repository topology is NOT a Team Topologies architectural force

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-MONO-01 | *Team Topologies* Part I excerpt, full-text search | Skelton & Pais | https://res.infoq.com/articles/book-review-team-topologies/en/resources/TTOP_excerpt_InfoQ-1572531146315.pdf | **NEGATIVE, load-bearing:** zero occurrences of "monorepo"/"repository"/"repo" in 3,177 lines. See R-TT-14 |
| R-MONO-02 | Independent Service Heuristics, full-text search | Team Topologies | https://github.com/TeamTopologies/Independent-Service-Heuristics | **NEGATIVE, load-bearing:** 10 heuristics, none about repositories. See R-TT-16 |
| R-MONO-03 | Team Cognitive Load Assessment, full-text search | Team Topologies | https://github.com/TeamTopologies/Team-Cognitive-Load-Assessment | **NEGATIVE:** no repository question. See R-TT-11 |
| R-MONO-04 | Docker case study, full-text search | Team Topologies | https://teamtopologies.com/industry-examples/rebuilding-and-scaling-product-development-at-docker-using-team-topologies | **NEGATIVE:** fracture-plane case study containing zero "repo" occurrences |
| R-MONO-05 | Monoliths vs Microservices is Missing the Point | Skelton & Pais | https://teamtopologies.com/videos-slides/2019/07/10/monoliths-vs-microservices-is-missing-the-point-start-with-team-cognitive-load-does-eur-2019 | **Positive form of the negative:** TT's own replacement axis is team cognitive load |

### R-5b — Evidence that repository, deployment, versioning and ownership boundaries are separable

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-MONO-06 | What is a Monorepo? | Nx (Nrwl) | https://nx.dev/docs/concepts/decisions/why-monorepos | **"A monorepo is not a monolith: each project inside it stays separate and can be built, tested, and deployed on its own."** Six named benefits incl. atomic changes and developer mobility |
| R-MONO-07 | Monorepo vs Polyrepo | Nx (Nrwl) | https://nx.dev/docs/concepts/decisions/monorepo-vs-polyrepo | **The single most decision-useful page found.** Verbatim: "With modern build tooling, the technical challenges of maintaining a large repository are solvable, so the choice is mostly organizational." Names exactly two conditions where polyrepo wins (hard repo-level access control; teams share no code). Names the **hybrid ("Multiple monorepos")** as a first-class option with concrete split criteria |
| R-MONO-08 | External dependencies overview | Bazel | https://bazel.build/external/overview | **The technical refutation of "one repo = one team" as an architectural law.** A repository is "a directory tree with a boundary marker file at its root"; **multiple such files can coexist in a directory**. Repo boundaries are a dependency-fetch concern, not an ownership or deployment concern |
| R-MONO-09 | *MonolithMacro* bliki | Martin Fowler | — | **REJECTED — page does not exist (404).** Verified across four casings plus `/articles/monolithic-repository.html`, `/bliki/Monorepo.html`, `/eaaMonolith/`. **Commonly hallucinated. Never cite** |
| R-MONO-10 | Feature Toggle | Martin Fowler | https://martinfowler.com/bliki/FeatureToggle.html | **The canonical proof that deploy unit, release unit, and codebase unit are three different things.** Dissolves the repo framing |
| R-MONO-11 | Microservice Premium | Martin Fowler | https://martinfowler.com/bliki/MicroservicePremium.html | The cost side: microservices pay their premium in team-level complexity. Full text contains zero repo mentions |
| R-MONO-12 | ruthlessly monorepo | Evan Luton | — | **REJECTED (fetchability).** Widely cited; Medium returns 403, and `evanluton.github.io`, `evanluton.com`, and the GitHub repo all 404. No fetchable canonical URL survives |
| R-MONO-13 | Code Ownership | Nx (Nrwl) | https://nx.dev/docs/concepts/decisions/code-ownership | Frames the monorepo-ownership problem and notes "the structure of an Nx workspace often reflects the structure of an organization". Closest TT-aligned position on repo topology |

### R-5c — Evidence FOR monorepo

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-MONO-14 | Why Google Stores Billions of Lines of Code in a Single Repository | Potvin & Levenberg, CACM 59(7):78–87 | https://research.google/pubs/pub45424/ | 1B files, 9M source files, 2B LOC, 35M commits, 86TB, ~40k commits/workday. Reviews advantages **and trade-offs**. Dated 2016 (the frequently-cited 2010 item is Pike, *Declarative Management of Large Software Systems*) |
| R-MONO-15 | Same, open PDF mirror | CACM (mirror) | https://bowringj.people.charleston.edu/classes/csci%20362/docs/GoogleCodeRepo-78-potvin.pdf | Accessible full text with the figures table when ACM blocks bots |
| R-MONO-16 | Scaling Git (and some back story) | Brian Harry / Microsoft | https://devblogs.microsoft.com/bharry/scaling-git-and-some-back-story/ | **The strongest decision datum: a directional change, not a success report.** Harry's strategy was "the right number of repos based on the character of the code"; Microsoft then "back[ed] away from that strategy" and merged 40+ depots into one |
| R-MONO-17 | The largest Git repo on the planet | Brian Harry / Microsoft | https://devblogs.microsoft.com/bharry/the-largest-git-repo-on-the-planet | ~3.5M files, ~300GB, ~4,000 engineers, 1,760 daily lab builds across 440 branches |
| R-MONO-18 | Perf results on scaling Git on VSTS with GVFS | Brian Harry / Microsoft | https://devblogs.microsoft.com/bharry/perf-results-on-scaling-git-on-vsts-with-gvfs | Real-usage numbers post-"O(modified)": clone minutes (not 12+ h); checkout ~30 s (not 2–3 h); status 4–5 s (not 10 min) |
| R-MONO-19 | microsoft/scalar | Microsoft | https://github.com/microsoft/scalar | Sparse checkout, filesystem monitoring, multi-pack-index, commit-graph. **Tooling, not topology, is what made the monorepo tractable** |
| R-MONO-20 | Advancing the .NET Virtual Monolithic Repository | .NET announcements | https://github.com/dotnet/announcements/issues/241 | **Explicit, quantified-in-kind polyrepo pain:** building from individual product repos "requires orchestration infrastructure that is available only to Microsoft" and destroys reproducibility of the official build in the open |
| R-MONO-21 | Monorepos: A Multivocal Literature Review | Brito, Terra, Valente — VEM 2018 | https://arxiv.org/abs/1810.09477 | **The only peer-reviewed treatment.** Monorepo benefits = simplified dependencies, cross-project change coordination, easy refactoring; challenges = code health, complexity, tooling investment |
| R-MONO-22 | Advantages of monorepos | Dan Luu | https://danluu.com/monorepo/ | Canonical pro essay, with the author's explicit refusal to call monorepos superior: "Monorepos aren't strictly superior to many-repos. They're not strictly worse, either." |
| R-MONO-23 | Maintaining a Monorepo — Why a monorepo? | Michael Nygard et al | https://monorepo-book.github.io/why-monorepo.html | Best-sourced critical treatment; concedes each pro point one-for-one. Closing operational claim: "Monorepos don't maintain themselves… the fraction of budget allocated to maintaining the monorepo, including infrastructure, tools, and people" |
| R-MONO-24 | Maintaining a Monorepo — Git's dimensions of scale | Nygard et al | https://monorepo-book.github.io/dimensions.html | **Kills "the repo is too big" as a single objection:** it decomposes into working directory, history size, refs, file count — each with its own Git-native fix |
| R-MONO-25 | Maintaining a Monorepo — How to detect and analyze scale problems | Nygard et al | https://monorepo-book.github.io/detection.html | Empirical methodology for diagnosing scale pain rather than assuming it |

### R-5d — Evidence FOR polyrepo, and evidence that hybrids fail by drift

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-MONO-26 | Don't ask if a monorepo is good for you — ask if you're good enough for a monorepo | Josef Šimánek | https://yosefk.com/blog/dont-ask-if-a-monorepo-is-good-for-you-ask-if-youre-good-enough-for-a-monorepo.html | **The most decision-relevant criticism.** "Monorepo is great if you're really good, but absolutely terrible if you're not that good." Organisational-readiness critique |
| R-MONO-27 | Poly Repos (architecture design document) | GitLab Handbook | https://handbook.gitlab.com/handbook/engineering/architecture/design-documents/poly_repos/ | The most explicit polyrepo engineering rationale from a hyperscale vendor. Names patch sets, grouped MRs, diff-recomputation load — and concedes "this problem already exists for monorepos" |
| R-MONO-28 | Implementing polyrepo engineering | GitHub Well-Architected | https://learn.github.com/well-architected/architecture/recommendations/implementing-polyrepo-engineering | **GitHub publishes an official polyrepo recommendation**, naming reusable workflows' cost: "questions of adoption, drift, failures, and versioning" |
| R-MONO-29 | Implementing monorepo engineering | GitHub Well-Architected | https://learn.github.com/well-architected/architecture/recommendations/implementing-monorepo-engineering | **GitHub publishes both.** Their position is that this is not a settled binary |
| R-MONO-30 | Monorepos Aren't Perfect | Wilfred Hughes | https://notes.wilfred.me.uk/MonoreposArentPerfect | Sharpest statement of the upstream/OSS cost: importing external code into a monorepo makes syncing and contributing back harder |
| R-MONO-31 | monorepo vs polyrepo repository structure as an architectural decision | Glenn Lum | https://gd-mrng.github.io/engineering-blog/216-monorepo-vs-polyrepo-repository-structure-as-an-architectural-decision | "Neither eliminates the cost. They relocate it." Hybrids "combine the costs of both models… chosen deliberately, not arrived at by drift" |
| R-MONO-32 | Monolithic Repositories Are Evil | Yegor Bugayenko | https://www.yegor256.com/2018/09/05/monolithic-repositories.html | Critique of monorepo as a smell. `PARTIAL` — **conflates monorepo with monolith**, which R-MONO-06 and R-MONO-14 explicitly reject. Cite as opinion only |
| R-MONO-33 | Monolithic vs multi-repo | Peter Seibel | http://www.gigamonkeys.com/mono-vs-multi/ | The older, calmer framing; shows the debate predates the tooling era |
| R-MONO-34 | I. Codebase — Twelve-Factor App | Adam Wiggins | https://12factor.net/codebase | **Origin of the polyrepo doctrine, and stricter than usually remembered.** "Multiple apps sharing the same code is a violation of twelve-factor" |
| R-MONO-35 | V. Build, release, run | Adam Wiggins | https://12factor.net/build-release-run | Strict build/release/run separation; **the deploy-unit ≠ repo-unit distinction already present in 2011** |
| R-MONO-36 | Managing monorepos / improving monorepo performance | GitLab Docs | https://docs.gitlab.com/user/project/repository/monorepos/ | Mirror-image doc: Gitaly inherits all Git limitations; shallow clone, hideRefs, branch cleanup as mitigations |
| R-MONO-37 | monorepo-vs-polyrepo | Joel P. Henderson | https://github.com/joelparkerhenderson/monorepo-vs-polyrepo | Opinion, not data — but the standup criterion is TT-shaped: "if your developers are not all attending the same standup, then you should be working in multiple repositories" |

### R-5e — Ownership at monorepo scale (the model this PRD adopts)

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-MONO-38 | Chromium — Code Reviews (OWNERS model) | The Chromium Authors | https://chromium.googlesource.com/chromium/src/+/main/docs/code_reviews.md | **The reference implementation of monorepo + hard ownership.** Recursive per-directory OWNERS; a change needs positive review from an owner of *each directory touched*; prefer more-specific owners; "any committer can contribute" — contribution open, approval hard-scoped |
| R-MONO-39 | Chromium — Mandatory Code-Review and Native OWNERS | The Chromium Authors | https://chromium.googlesource.com/chromium/src/+/main/docs/code_review_owners.md | Since 24 Mar 2021 committers can **no longer bypass** code review or OWNERS approval. Bypasses removed |
| R-MONO-40 | Chromium — Large Scale Changes (LSC) | The Chromium Authors | https://chromium.googlesource.com/chromium/src/+/main/docs/process/lsc/large_scale_changes.md | **The escape hatch.** An approved LSC process lets cross-cutting refactors **temporarily bypass OWNERS** via `Owners-Override`, still requiring a second human. This is the exact hybrid this PRD adopts: strict local ownership + explicit architectural escape hatch |
| R-MONO-41 | Gerrit code-owners plugin — backend file format | Gerrit Code Review | https://github.com/GerritCodeReview/plugins_code-owners/blob/master/resources/Documentation/backend-find-owners.md | The normative OWNERS file-format spec that Chromium's docs defer to |
| R-MONO-42 | Gerrit | Google | https://gerrit.googlesource.com/ | The review substrate that makes OWNERS enforcement mechanical |
| R-MONO-43 | chromium/src source browser | Chromium | https://source.chromium.org/ | Lets one audit real OWNERS placement across the tree — evidence that ownership must be directory-granular |

### R-5f — Adoption data

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-MONO-44 | State of JavaScript 2024 — Monorepo Tools | State of JS / Devographics | https://2024.stateofjs.com/en-US/libraries/monorepo_tools | **Only quantified adoption data found.** n≈10,068: pnpm 3,508; npm Workspaces 2,438; Nx 1,917; Yarn 1,784; Turborepo 1,412; Lerna 1,230; **None 2,928**. Avg 1.3 monorepo tools; 5,940 respondents use zero. `PARTIAL` — self-selected JS survey, not enterprise-representative. **Load-bearing: the tooling prerequisite is not met by most shops** |

---

## R-6 Metadata-driven architecture and declarative composition

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-META-01 | Operator pattern | Kubernetes / CNCF | https://kubernetes.io/docs/concepts/extend-kubernetes/operator/ | **The declarative-desired / imperative-reconciler split.** The CR is the desired state; the operator is imperative code whose *input* is declarative metadata |
| R-META-02 | Custom Resources | Kubernetes | https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/ | The CRD schema **is** the metadata contract; the apiserver validates it |
| R-META-03 | Declarative Management of Kubernetes Objects Using Configuration Files | Kubernetes | https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/ | The canonical citation for the declarative-vs-imperative boundary |
| R-META-04 | Controllers (control plane pattern) | Kubernetes | https://kubernetes.io/docs/concepts/architecture/controller/ | The control loop: observe desired vs actual, reconcile, repeat |
| R-META-05 | What are Operators? | Red Hat OpenShift Container Platform docs | https://docs.redhat.com/en/documentation/openshift_container_platform/4.21/html/operators/understanding-operators | **File-based catalog schemas with explicit types:** `olm.package`, `olm.channel`, `olm.bundle`, `olm.gvk`. Declarative metadata catalog, production-grade, predating Backstage by years |
| R-META-06 | What are Operators? | OKD / OpenShift | https://docs.okd.io/latest/operators/understanding/olm-what-operators-are.html | Operator Framework, CSV, catalog source, operator maturity model |
| R-META-07 | Descriptor Format of Catalog Entities | Backstage (Spotify) | https://backstage.io/docs/features/software-catalog/descriptor-format/ | **The `catalog-info.yaml` schema.** Envelope `apiVersion`/`kind`/`metadata`/`spec`; `metadata.name` required, `uid` **output-only and explicitly unstable**; component `spec` requires `type`, `lifecycle`, `owner`; optional `providesApis`, `consumesApis`, `dependsOn`. **`relations` and `status` are read-only and must not be authored** |
| R-META-08 | System Model | Backstage | https://backstage.io/docs/features/software-catalog/system-model/ | Domain → System → Component → Resource containment model |
| R-META-09 | Well-known Relations | Backstage | https://backstage.io/docs/features/software-catalog/well-known-relations/ | `ownedBy`/`ownerOf`, `partOf`/`hasPart`, `dependsOn`/`dependencyOf`, `providesApi`/`apiProvidedBy`, `consumesApi`/`apiConsumedBy`. **Critical: consume the relation, not `spec.owner` — owner may be derived from CODEOWNERS, not YAML** |
| R-META-10 | Well-known Annotations | Backstage | https://backstage.io/docs/features/software-catalog/well-known-annotations/ | Reserved `backstage.io/` annotation keys |
| R-META-11 | Entity References | Backstage | https://backstage.io/docs/features/software-catalog/references/ | `kind:namespace/name` string refs — the stable-identity mechanism given `uid` instability |
| R-META-12 | OpenAPI Specification v3.1.0 | OpenAPI Initiative / Linux Foundation | https://spec.openapis.org/oas/v3.1.0.html | **This PRD pins 3.1.x.** Required root fields are only `openapi` and `info`; `info` requires `title` and `version`; **`servers` is optional**; `components` entries have no effect unless `$ref`d |
| R-META-13 | OpenAPI Specification v3.2.1 | OpenAPI Initiative | https://spec.openapis.org/oas/v3.2.1.html | **The current live "latest".** Cited to record that v3.0.0 deliberately pins 3.1.x rather than tracking latest |
| R-META-14 | AsyncAPI Specification v3.1.0 | AsyncAPI Initiative | https://www.asyncapi.com/docs/reference/specification/v3.1.0 | Event-driven metadata; `channels` (v3) replace `topics` |
| R-META-15 | JSON Schema Draft 2020-12 — Core and Validation | IETF / JSON Schema | https://json-schema.org/draft/2020-12/json-schema-core | `$vocabulary`, `$dynamicRef`, dialect URIs — schema evolution via `$schema` |
| R-META-16 | JSON Schema Draft 2020-12 — Release Notes | IETF / JSON Schema | https://json-schema.org/draft/2020-12/release-notes | The normative dialect specification used for commit-time metadata validation |
| R-META-17 | CUE Documentation | CUE authors | https://cuelang.org/docs/ | **CUE collapses schema and instance into one artifact.** The strongest support for constraints expressible as data. `PARTIAL` — cited for the unification property, not adopted (see DEC-11) |
| R-META-18 | CUE Language Specification | CUE authors | https://cuelang.org/docs/references/spec/ | Normative reference; the determinism claim rests here |
| R-META-19 | Life of an Entity | Backstage | https://backstage.io/docs/features/software-catalog/life-of-an-entity | **The ingestion pipeline: YAML → discovery → providers → processors → DB.** Establishes the catalog as a *derived index*, not a source of truth |
| R-META-20 | Creating the Catalog Graph | Backstage | https://backstage.io/docs/features/software-catalog/creating-the-catalog-graph/ | The catalog is a graph; descendants/ancestors traversal is derived, not authored |
| R-META-21 | Bzlmod Migration Guide | Bazel | https://bazel.build/external/migration | `MODULE.bazel`; `bazel_dep` resolved transitively by MVS — **dependency metadata decides the build graph** |
| R-META-22 | Bazel Central Registry | Bazel | https://registry.bazel.build/ | A real version-addressed metadata catalog |
| R-META-23 | Nx Project Configuration | Nx | https://nx.dev/reference/project-configuration | Declarative per-project build metadata; task inference |
| R-META-24 | Configuring Tasks (`turbo.json`) | Turborepo | https://turborepo.com/docs/crafting-your-repository/configuring-tasks | `tasks`, `inputs`/`outputs`, `dependsOn` as the remote-cache contract |
| R-META-25 | mcp-actions-backend plugin README | Backstage | https://github.com/backstage/backstage/tree/master/plugins/mcp-actions-backend | Catalog actions exposed as MCP tools; MCP servers modelled as catalog entities with owner and lifecycle |

---

## R-7 Developer environment: devenv, direnv, Nix, secrets

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-DV-01 | devenv — home | Cachix | https://devenv.sh/ | Declarative, reproducible, composable dev environment built on Nix |
| R-DV-02 | Getting Started | Cachix | https://devenv.sh/getting-started/ | `devenv init`, `devenv shell`, `devenv up` |
| R-DV-03 | Options reference | Cachix | https://devenv.sh/reference/options/ | **Authoritative list of every `devenv.nix` option**, generated from the module tree: `enterShell`, `tasks`, `languages.*`, `services.*`, `processes.*`, `git-hooks.*`, `env.*`, `enterTest`, `cleanup`, `files`, `scripts` |
| R-DV-04 | `devenv.yaml` reference | Cachix | https://devenv.sh/reference/yaml-options/ | `inputs` (`flake`, `inputs`, `overlays`, `url`), `imports` for monorepo composition, `clean.enabled`, `require_version` |
| R-DV-05 | Inputs | Cachix | https://devenv.sh/inputs/ | `devenv update` / `devenv lock`; per-input revision pinning — the reproducibility mechanism |
| R-DV-06 | Tasks | Cachix | https://devenv.sh/tasks/ | `tasks.<name>` with `before`/`after` deps |
| R-DV-07 | Services | Cachix | https://devenv.sh/services/ | `services.<name>.enable` — declarative local dependencies |
| R-DV-08 | Scripts / personal overrides | Cachix | https://devenv.sh/scripts/ | **`devenv.local.nix` is the uncommitted personal-override file** |
| R-DV-09 | Environment variables reference | Cachix | https://devenv.sh/reference/environment-variables/ | `env.<VAR>` vs `enterShell` ordering; invasive vs non-invasive |
| R-DV-10 | Direnv integration | Cachix | https://devenv.sh/integrations/direnv/ | **The official devenv↔direnv guide.** Auto-writes `use devenv` into `.envrc` |
| R-DV-11 | Using devenv with Nix Flakes | Cachix | https://devenv.sh/guides/using-with-flakes/ | When to prefer a hand-rolled `flake.nix` / `devenvShell` |
| R-DV-12 | Migrating to devenv 2.0 | Cachix | https://devenv.sh/guides/migrating-to-20/ | Version-2 breaking changes; cite before pinning behaviour claims |
| R-DV-13 | devenv (repository) | Cachix | https://github.com/cachix/devenv | Source of truth; the `devenv.nix` schema lives in the Nix module tree |
| R-DV-14 | devenv changelog / design rationale index | Cachix | https://devenv.sh/blog/2024/09/11/devenv-11-nested-nix-outputs-using-the-module-system/index.md | Module system (1.1), convergent tasks (1.2), Nix caching (1.3), Tvix evaluator (1.3), monorepo `imports` (1.10) |
| R-NIX-01 | nix flake (command reference) | NixOS | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html | Flake outputs locked to a **fixed, hard-coded schema**; `flake.nix` inputs evaluated **statically** — no variables, functions or imports in that file |
| R-NIX-02 | nix develop | NixOS | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-develop.html | `--ignore-environment`/`-i`, `--refresh`, `--offline` |
| R-NIX-03 | nix flake lock | NixOS | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-lock.html | `flake.lock` as the reproducibility contract; `--no-update-lock-file`; `--override-input` (a documented pin-defeating escape hatch) |
| R-NIX-04 | nix flake check | NixOS | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html | Lint/verify all flake outputs — the validate-metadata-at-CI verb |
| R-NIX-05 | nix-store(1) | NixOS | https://nix.dev/manual/nix/stable/command-ref/nix-store.html | `nix-store --realise` (`-r`), `--timings`. **The canonical reference for why a cold build is slow:** realisation is fetching-or-building a closure |
| R-NIX-06 | cache.nixos.org | NixOS | https://cache.nixos.org/ | The official binary cache. Build speed is entirely a function of closure cache-hit rate |
| R-NIX-07 | Determinate Nix is the future of Nix today | Determinate Systems | https://determinate.systems/blog/determinate-nix-future/ | **Vendor-confirmed limitation:** flakes "forced flake outputs into an inflexible mold, with a static, pre-set list of known output types" |
| R-NIX-08 | Nix purity and the illusion of isolation | Dominic Egginton | https://dominicegginton.dev/documents/nix-purity-and-the-illusion-of-isolation/ | `PARTIAL` — the insidiest leak is `sandbox-paths`, which mounts host paths into a build **without recording them in the derivation**: same `.drv`, different output |
| R-DIR-01 | DIRENV(1) man page | direnv / rofle | https://direnv.net/man/direnv.1.html | **Canonical CLI and security model.** Checks `.envrc` in current + parent dirs before each prompt, loads it in a bash subshell, diffs exported vars back; `direnv allow`/`deny` records authorisations under `$XDG_DATA_HOME/direnv/allow`. States the threat: "any git repo you pull… would be able to wipe your hard disk once you `cd` into it" |
| R-DIR-02 | DIRENV-STDLIB(1) | direnv | https://direnv.net/man/direnv-stdlib.1.html | `layout<name>`, `dotenv`, `source_up`, `use flake`/`use nix`, and **`require_allowed`** (≥2.38.0) which extends the allow-list to **lockfiles consumed by** the activation script |
| R-DIR-03 | DIRENV.TOML(1) | direnv | https://direnv.net/man/direnv.toml.1.html | `[whitelist]` `prefix`/`exact` directives — bypasses the allow list; the docs themselves warn this "should be used with great care". **The real weakness in direnv's model** |
| R-DIR-04 | direnv (repository) | direnv | https://github.com/direnv/direnv | Implementation and README |
| R-DIR-05 | direnv — home | direnv | https://direnv.net/ | **All `direnv.net/docs/*.html` paths 404. The docs live under `/man/`. Do not cite `/docs/`** |
| R-DIR-06 | devbox | Jetify | https://www.jetify.com/devbox | Nix-based dev shells with a simpler DX layer; comparison point |
| R-DIR-07 | mise | Jeff Dickey | https://mise.jdx.dev/getting-started.html | Polyglot runtime manager via `.mise.toml`; the asdf successor |
| R-DIR-08 | asdf guide | asdf-vm | https://asdf-vm.com/guide/getting-started.html | `.tool-versions` per-project pinning, but no system packages, services or containers |
| R-DIR-09 | Pants — Welcome to Pants! | Pants | https://www.pantsbuild.org/stable/docs/introduction/welcome-to-pants | **"Pants works well with (but does not require) a monorepo architecture."** Load-bearing evidence that tooling determines the *cost* of monorepo, not its correctness |
| R-SCRT-01 | SecretSpec — A declarative interface for every secret provider | **Cachix** (`org.cachix.secretspec`) | https://secretspec.dev/ | Declares secret **requirements** separately from **providers** (35 backends). Positions explicitly against `.env`: "Eliminate secrets from environment variables and configuration files". Integrates with devenv |
| R-SCRT-02 | SecretSpec — Declarative Configuration | SecretSpec | https://secretspec.dev/concepts/declarative/ | `secretspec.toml` schema: `[project]` with `extends`, `[profiles.<name>]` per environment |
| R-SCRT-03 | SecretSpec — CLI reference | SecretSpec | https://secretspec.dev/reference/cli/ | `secretspec init --from dotenv://` — **the practical `.env` migration path**; `run --profile`, `schema`, `import` |
| R-SCRT-04 | SOPS | getsops | https://github.com/getsops/sops | Encrypted-in-place file secrets with tree-level key selection; decrypt-on-read |
| R-SCRT-05 | age | Filippo Valsorda | https://github.com/FiloSottile/age | Modern minimal file encryption; the default SOPS recipient |
| R-SCRT-06 | 1Password CLI reference | 1Password | https://developer.1password.com/docs/cli/reference/ | `op run` injects secrets into a child process's environment from vaults |
| R-SCRT-07 | III. Config — The Twelve-Factor App | Wiggins / Heroku | https://12factor.net/config | **Cited against the common misuse.** Twelve-factor says env vars are a *config delivery* mechanism; it says **nothing about secret storage** and nothing that justifies committing a `.env` |

---

## R-8 Aggregator / BFF / API composition

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-BFF-01 | Pattern: Backends For Frontends | Sam Newman | https://samnewman.io/patterns/architectural/bff/ | **Primary source of the BFF pattern.** One BFF per UI type; downstream-call reuse; **perimeter concerns kept out of the BFF**; when *not* to use it |
| R-BFF-02 | Pattern: UI Composition | Sam Newman | https://samnewman.io/patterns/architectural/ui-composition/ | The client-side counterpart (SSI, MSEO, MACH/NW.js) — the decision reference for server- vs client-side aggregation |
| R-BFF-03 | Backends for Frontends Pattern | Microsoft Azure Architecture Center | https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends | Frontend teams own their BFF (language, release cadence, workload priority); cross-cutting stays in APIM. **"With GraphQL, the querying mechanism eliminates the need for a separate BFF layer"** |
| R-BFF-04 | Front-end client communication | Microsoft / .NET cloud-native | https://learn.microsoft.com/en-us/dotnet/architecture/cloud-native/front-end-communication | **The sharpest risk statement:** "Keep the API Gateway simple and fast… A complex gateway risks becoming a bottleneck and eventually a monolith itself" |
| R-BFF-05 | Gateway Aggregation Pattern | Microsoft | https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-aggregation | "Gateway fans out and merges N responses" — the mechanism a BFF uses; explicit trade-off warning on overuse |
| R-BFF-06 | Cloud Design Patterns index | Microsoft | https://learn.microsoft.com/en-us/azure/architecture/patterns/ | Umbrella vocabulary: Circuit Breaker, Bulkhead, Cache-Aside, Gateway Offloading/Routing |
| R-BFF-07 | API Gateway Pattern | Chris Richardson | https://microservices.io/patterns/apigateway.html | The single entry point for all client requests; routing and protocol translation. The canonical *pre-BFF* tier |
| R-BFF-08 | *Building Microservices*, 2nd ed. | Sam Newman | https://samnewman.io/books/building_microservices_2nd_edition/ | **Ch. 4 "API composition"** is the citable chapter for gateway aggregation, GraphQL and BFF |
| R-BFF-09 | *Monolith to Microservices* | Sam Newman | https://samnewman.io/books/monolith-to-microservices/ | Decomposition and pattern mapping. `PARTIAL` — **no dedicated aggregation/BFF chapter**; use R-BFF-01 and R-BFF-08 |
| R-BFF-10 | Pattern: Strangler Fig Application | Sam Newman | https://samnewman.io/patterns/refactoring/strangler-fig-application/ | Newman's write-up of the migration pattern |
| R-BFF-11 | Strangler Fig Application | Martin Fowler | https://martinfowler.com/bliki/StranglerFigApplication.html | Routing traffic around a legacy system one slice at a time |
| R-BFF-12 | Microservices (with James Lewis) | Martin Fowler & James Lewis | https://martinfowler.com/articles/microservices.html | "Smart endpoints and dumb pipes", "Design for failure", Tolerant Reader, Consumer-Driven Contracts. **Full text contains zero repo mentions** |
| R-BFF-13 | Microservice Trade-Offs | Martin Fowler | https://martinfowler.com/articles/microservice-trade-offs.html | The latency argument for aggregation: "six parallel async calls are as slow as the slowest, not the sum" |
| R-BFF-14 | Microservices and the First Law of Distributed Objects | Martin Fowler | https://martinfowler.com/articles/distributed-objects-microservices.html | "Distribution is a complexity booster" — the cost an aggregator does *not* remove |
| R-BFF-15 | MonolithFirst | Martin Fowler | https://martinfowler.com/bliki/MonolithFirst.html | Don't split until there is evidence |
| R-BFF-16 | PresentationDomainDataLayering | Martin Fowler | https://martinfowler.com/bliki/PresentationDomainDataLayering.html | Presentation / Domain / Data Mapper separation — what an aggregator must respect to avoid becoming a fat domain model |
| R-BFF-17 | Richardson Maturity Model | Martin Fowler (explaining Leonard Richardson) | https://martinfowler.com/articles/richardsonMaturityModel.html | Levels 0–3; Fowler's caveat that it is not a REST definition; level 2 is the "industry sweet spot" |
| R-BFF-18 | Measuring the RESTful-ness of an application | Mark Little interviewing Leonard Richardson, InfoQ | https://www.infoq.com/news/2011/05/measuring-rest/ | Richardson's own clarification that the ladder is a heuristic, not a conformance test |
| R-BFF-19 | Enterprise Integration Patterns | Hohpe & Woolf | https://www.enterpriseintegrationpatterns.com/ | The 65-pattern distributed-systems vocabulary; **Mediator vs Facade** is the canonical distinction between an aggregation layer and a routing hub |
| R-BFF-20 | Message Routing patterns | Hohpe & Woolf | https://www.enterpriseintegrationpatterns.com/patterns/messaging/Introduction.html | Hub-mediated routing; establishes Mediator semantics |
| R-BFF-21 | Microservices Anti-Patterns (talk) | **Chris Richardson** — *not* Sam Newman | https://microservices.io/post/antipatterns/2019/01/28/melbourne-microservices.html | Magic Pixie Dust, Microservices as the Goal. **Attribution corrected** |
| R-BFF-22 | Microservices Anti-Patterns | Chris Richardson | https://microservices.io/patterns/ | The pattern catalogue containing the above |
| R-BFF-23 | Microservices AntPatterns and Pitfalls | **Mark Richards** / O'Reilly | https://www.oreilly.com/content/microservices-antipatterns-and-pitfalls/ | **The book actually titled *Microservices Anti-Patterns*.** Ten anti-patterns incl. Reach-in Reporting, "I Was Taught to Share", Static Contract, Timeout Anti-Pattern |
| R-BFF-24 | Seven Microservices Anti-patterns | Vijay Alagarasan, InfoQ | https://www.infoq.com/articles/seven-uservices-antiparterns/ | Freely readable enumeration incl. "building a gateway in every service" — the anti-BFF-per-service failure mode |
| R-BFF-25 | Microservices Anti-patterns: A Taxonomy | Taibi, Lenarduzzi, Pahl / Springer | https://link.springer.com/chapter/10.1007/978-3-030-31646-4_5 | Academic 20-item taxonomy split organisational/technical. `PARTIAL` — abstract visible, chapter paywalled |
| R-BFF-26 | Microservices Anti-Patterns and Bad Smells: a tertiary study | Al-Dajani et al., JSS | https://www.sciencedirect.com/science/article/pii/S0164121223002248 | Catalogue of **58** documented anti-patterns + detection techniques. `PARTIAL` — landing page; full text paywalled |
| R-BFF-27 | Microservices Guide | Martin Fowler | https://martinfowler.com/microservices/ | Fowler's curated index of his own microservice material |

---

## R-9 GraphQL federation (recorded; not adopted)

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-AGGR-01 | Federation overview | Apollo | https://www.apollographql.com/docs/graphos/federation | Supergraph architecture |
| R-AGGR-02 | Subgraph specification | Apollo | https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/reference/subgraph-spec | `_service { sdl }`, `Query._entities`, `_Any`, `_FieldSet` — the subgraph introspection contract |
| R-AGGR-03 | Composition rules | Apollo | https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/reference/composition-rules | Fed2 satisfiability, entity/key rules, `@shareable` conflicts, `EXTERNAL_MISSING_ON_BASE`, `INCONSISTENT_VALUE` |
| R-AGGR-04 | Federation directives reference | Apollo | https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/reference/directives | `@key`, `@requires`, `@provides`, `@shareable`, `@external` semantics |
| R-AGGR-05 | Federation specification v2.0 | Apollo | https://specs.apollo.dev/federation/v2.0/ | **Normative, version-pinned spec snapshot** incl. `join__Graph`, `join__FieldSet` |
| R-AGGR-06 | Query plans | Apollo | https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/reference/query-plans | `Fetch` / `Parallel` / `Sequence` / `Flatten` / `Defer` / `Skip`. **`Sequence` = "one subgraph's response depends on data that first must be returned by another"** — the waterfall this PRD forbids |
| R-AGGR-07 | Apollo Router | Apollo | https://www.apollographql.com/docs/graphos/routing | Router as gateway/runtime; explicitly positioned against URL/REST-based API gateways |
| R-AGGR-08 | Router request lifecycle | Apollo | https://www.apollographql.com/docs/graphos/routing/v3/request-lifecycle | Router → Supergraph → Execution → Subgraph pipeline |
| R-AGGR-09 | Native Query Planner | Apollo | https://www.apollographql.com/docs/graphos/routing/query-planning/native-query-planner | Rust-native planner, default since v1.59.0. **Direct evidence that a composition tier is itself a resource cost** |
| R-AGGR-10 | Incremental Query Planner | Apollo | https://www.apollographql.com/docs/graphos/routing/v3/query-planning/incremental-query-planner | `beam_width` / `fuel` / `timeout` knobs; planner cost explodes with `@shareable`/`@key`/`@requires` density |
| R-AGGR-11 | `@defer` support | Apollo | https://www.apollographql.com/docs/graphos/routing/operations/defer | **The escape hatch for an unavoidable waterfall:** return sub-query 1 instead of blocking on 2 |

---

## R-10 Contract testing and provider/consumer contracts

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-CDC-01 | Consumer-Driven Contracts: A Service Evolution Pattern | **Ian Robinson** (Thoughtworks) for Martin Fowler | https://martinfowler.com/articles/consumerDrivenContracts.html | **The canonical CDC theory piece.** Postel's Law, "just enough validation", bounded stability/immutability, and the claim that provider contracts are *derived from* consumer contracts. **Attribution corrected** |
| R-CDC-02 | Tolerant Reader | Martin Fowler | https://martinfowler.com/bliki/TolerantReader.html | The consumer-side half of CDC; ship the reader plus its tests to the provider |
| R-CDC-03 | Testing Strategies in a Microservice Architecture | Toby Clemson for Martin Fowler | https://martinfowler.com/articles/microservice-testing/ | Best free treatment of contract tests: each consumer writes tests asserting only what it uses; the sum defines the service contract |
| R-CDC-04 | Consumer-driven contract testing | Thoughtworks Technology Radar | https://www.thoughtworks.com/radar/techniques/consumer-driven-contract-testing | Independent validation + the caution that CDC is "a technique and an attitude", not a Pact dependency |
| R-CDC-05 | Pact | Pact Foundation | https://www.pact.io/ | The de-facto standard implementation; broker model, `can-i-deploy` |
| R-CDC-06 | Pactflow | Pactflow | https://pactflow.io/ | Hosted broker + CI integration |
| R-CDC-07 | pact-js | Pact Foundation | https://github.com/pact-foundation/pact-js | JavaScript implementation |
| R-CDC-08 | Spring Cloud Contract | Spring / Broadcom | https://docs.spring.io/spring-cloud-contract/reference/ | Producer-driven stub generation; the common JVM alternative to Pact |
| R-CDC-09 | ts-rest | ts-rest | https://ts-rest.com/ | **Verified verbatim** as "tRPC-like typesafe REST with OpenAPI": one `t.router` contract shared by client and server, Zod-derived inference, auto-generated OpenAPI |
| R-CDC-10 | ts-rest — OpenAPI | ts-rest | https://ts-rest.com/openapi | The OpenAPI generation path |

---

## R-11 Resilience, caching, and aggregation latency

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-RES-01 | Timeouts, retries, and backoff with jitter | AWS Builders' Library | https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/ | **Retry budgets across the whole call tree.** Load-bearing for an aggregator's blast radius |
| R-RES-02 | Using load shedding to avoid overload | AWS Builders' Library | https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/ | Graceful degradation under load; cheaper than scaling |
| R-RES-03 | Circuit Breaker Pattern | Microsoft | https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker | Closed/Open/Half-Open; "consider a timeout for each try" |
| R-RES-04 | Circuit Breaker | Martin Fowler (bliki, with Nigel Prosop) | https://martinfowler.com/bliki/CircuitBreaker.html | In practice you usually cannot tell a timeout from a refusal |
| R-RES-05 | Bulkhead Pattern | Microsoft | https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead | Partitioned pools so one dependency's exhaustion cannot take down the caller |
| R-RES-06 | Cache-Aside Pattern | Microsoft | https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside | Lazy on-demand load with expiry; the default recommendation for read-heavy aggregation |
| R-RES-07 | Caching patterns | AWS Prescriptive Guidance | https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/caching.html | Canonical cache-aside vs write-through definitions and the write-around/write-back family |
| R-RES-08 | Redis client patterns | Redis Ltd | https://redis.io/docs/latest/develop/clients/patterns/ | **The mandate-ready mechanisms: key-versioning (TTL jitter on hot keys) and request coalescing / single-flight** |
| R-RES-09 | The Tail at Scale | Dean & Barroso, CACM 56(2) | https://research.google/pubs/pub40801/ | **The p99 argument for an aggregator.** Fan-out multiplies per-hop latency variance; temporary latency episodes dominate at scale. DOI 10.1145/2408776.2408794 |
| R-RES-10 | Service Best Practices (SRE Book ch. 2) | Google SRE | https://sre.google/sre-book/service-best-practices/ | Timeouts, retries + backoff, **deadline propagation**, and "inappropriate parallelism" |
| R-RES-11 | Addressing Cascading Failures (SRE Book ch. 22) | Google SRE | https://sre.google/sre-book/addressing-cascading-failures/ | Retries should be a tiny fraction of requests; resource exhaustion propagates through queues. **Note: this is a section of ch. 22; the bare `/cascading-failures/` slug 404s** |
| R-RES-12 | Handling Overload (SRE Book ch. 22) | Google SRE | https://sre.google/sre-book/handling-overload/ | Queue management, load shedding, graceful degradation |
| R-RES-13 | Monitoring Distributed Systems (SRE Book ch. 6) | Google SRE | https://sre.google/sre-book/monitoring-distributed-systems/ | **The four golden signals**; the quantile argument that motivates p99 budgets over averages |
| R-RES-14 | Service Level Objectives (SRE Book ch. 4) | Google SRE | https://sre.google/sre-book/service-level-objectives/ | SLI/SLO/SLA definitions |
| R-RES-15 | Alerting on SLOs (SRE Workbook ch. 5) | Google SRE | https://sre.google/workbook/alerting-on-slos/ | Burn-rate alerting; a defensible alternative to "page if p99 > X" |
| R-RES-16 | Handling Overload (SRE Workbook ch. 4) | Google SRE | https://sre.google/workbook/overload/ | Soft vs hard limits, per-customer load shedding |
| R-RES-17 | DataLoader | graphql/dataloader (GraphQL Foundation) | https://github.com/graphql/dataloader | **Verbatim:** "DataLoader will coalesce all individual loads which occur within **a single frame of execution (a single tick of the event loop)**". "With DataLoader this application will make at most **two**" round trips instead of four |
| R-RES-18 | DataLoader — Caching Per-Request | graphql/dataloader | https://github.com/graphql/dataloader | **The threshold rule:** its cache "only serves the purpose of not repeatedly loading the same data **in the context of a single request**". **Loaders must be created per request** — this is the anti-pattern a PRD must forbid |
| R-RES-19 | Handling N+1 in Apollo GraphOS | Apollo | https://www.apollographql.com/docs/graphos/schema-design/guides/handling-n-plus-one | The operational half of N+1: query plans, DataLoader at the subgraph edge, router-level detection |
| R-RES-20 | HTTP/2 (RFC 9113) | IETF | https://httpwg.org/specs/rfc9113.html | Streams, HPACK, and the **removal of HTTP/1.1's connection-concurrency restriction** — the citable basis for aggregator fan-out over one connection. **MDN has no HTTP/2 guide; cite the RFC** |
| R-RES-21 | HTTP Caching (RFC 9111) | IETF | https://httpwg.org/specs/rfc9111.html | The normative caching spec — the basis for immutable CDN caching of `remoteEntry` |
| R-RES-22 | HTTP caching (MDN) | MDN | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | Practical `Cache-Control` semantics |
| R-RES-23 | CDN (MDN Glossary) | MDN | https://developer.mozilla.org/en-US/docs/Glossary/CDN | Definitional |
| R-RES-24 | gRPC core concepts | gRPC / Google | https://grpc.io/docs/what-is-grpc/core-concepts/ | Generated stubs, deadline propagation (`grpc-timeout`), load balancing. **`PARTIAL` — documents what gRPC does; does *not* benchmark it against REST** |
| R-RES-25 | gRPC performance guide | gRPC / Google | https://grpc.io/docs/guides/performance/ | Connection reuse, channel-per-process, keepalive, separate channels per QoS |
| R-RES-26 | PgBouncer features | PgBouncer | https://www.pgbouncer.org/features.html | Three pooling modes + the transaction-mode caveat about prepared statements and session state |
| R-RES-27 | PgBouncer configuration | PgBouncer | https://www.pgbouncer.org/config.html | `pool_mode`, `max_client_conn`, `default_pool_size`, `reserve_pool_size` — the actual knobs |
| R-RES-28 | Little's Law | Wikipedia | https://en.wikipedia.org/wiki/Little's_law | L = λW. `PARTIAL` — **weak citation, used only for the formula.** Primary source is Little (1961), behind JSTOR |

---

## R-12 Micro-frontends and the composition layer

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-MFE-01 | Micro Frontends | **Cam Jackson** (Thoughtworks) for Martin Fowler | https://martinfowler.com/articles/micro-frontends.html | **The canonical article.** "Independently deliverable frontend applications composed into a greater whole". Defines **the container application**: renders common header/footer, owns authentication and navigation, composes remotes and tells each when and where to render. Five integration approaches. **Explicitly recommends *against* build-time integration** ("we would recommend strongly against this kind of approach"). Three downsides: **payload size, environment differences, operational and governance complexity**. Custodian model for shared components: "be careful to ensure that your shared components contain **only UI logic, and no business or domain logic**"; create shared libs too early and you get churn |
| R-MFE-02 | Micro Frontends — extending the microservice idea to frontend development | **Michael Geers**, neuland | https://micro-frontends.org/ | Author verified via the page's own schema.org metadata. Recipes-and-patterns companion to R-MFE-01 |
| R-MFE-03 | Technology Radar: Micro frontends | Thoughtworks | https://www.thoughtworks.com/radar/techniques/micro-frontends | History: Assess Nov 2016 → Trial Nov 2017 → **Adopt Apr 2019** (last updated May 2020). Currently "NOT ON THE CURRENT EDITION". **Note `/radar/techniques/`, not `/radar/tools/`** |
| R-MFE-04 | A Catalog of Micro Frontends Anti-patterns | Nabson P. et al. | https://arxiv.org/abs/2411.19472 | **The strongest verified anti-pattern citation** (open access, empirically validated). *Lack of Skeleton (100%)*, *Micro Frontend as the Goal (100%)*, *Mega Frontend (100%)*, *Cyclic Dependency (95%)*, *Hub-like Dependency (95%)*, *Golden Hammer (95%)*, *Nano Frontend (95%)* |
| R-MFE-05 | micro-frontends-anti-patterns (repository) | Nabson P. | https://github.com/nabsonp/micro-frontends-anti-patterns | The live catalogue backing R-MFE-04 |
| R-MFE-06 | Motivations, Benefits, and Issues for Adopting Micro-Frontends: A Multivocal Literature Review | Peltonen, Mezzalira, Taibi | https://arxiv.org/abs/2007.00293 | **Open access, 43 sources reviewed.** Quantifies the costs this PRD budgets against: "increased payload size of the application, increased code duplication and coupling between teams, and monitoring complexity" |
| R-MFE-07 | Micro-Frontends: Principles, Implementations, and Pitfalls | Taibi, Sorokin, Farrokhlagha-Zadeh, Korobenko | DOI 10.1145/3561846.3561853 | Peer-reviewed decomposition survey (SAP, Zalando, New Relic, Ikea, Starbucks, DAZN). `PARTIAL` — ACM 403; cite the DOI |
| R-MFE-08 | single-spa — Microfrontends Concept | single-spa | https://single-spa.js.org/docs/microfrontends-concept/ | Distinguishes microfrontends (teams) from microservices; root config as orchestrator, `bootstrap`/`mount`/`unmount` lifecycle |
| R-MFE-09 | single-spa — Layout Overview | single-spa | https://single-spa.js.org/docs/layout-overview/ | **The layout/composition layer as a first-class concept** — a concrete implementation of R-MFE-01's container application |
| R-MFE-10 | single-spa — FAQ | single-spa | https://single-spa.js.org/docs/faq/ | Dev-experience and shared-dependency trade-offs |
| R-MFE-11 | Using custom elements | MDN | https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_custom_elements | The Web-Components integration approach |
| R-MFE-12 | Using shadow DOM | MDN | https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM | Style encapsulation — the technical basis for solving the CSS-global problem |
| R-MFE-13 | Angular — Lazy loading | Angular | https://angular.dev/guide/di/lazy-loading | Route-level `loadChildren`; the component-level composition analogue |
| R-MFE-14 | Angular micro-frontend direction (issue 38646) | Angular | https://github.com/angular/angular/issues/38646 | **Records that Angular's framework-level MFE story is unsettled.** Cite as context, not prescription |
| R-MFE-15 | Third Party JavaScript Management Cheat Sheet | **OWASP** | https://cheatsheetseries.owasp.org/cheatsheets/Third_Party_Javascript_Management_Cheat_Sheet.html | **The OWASP citation for federated-supply-chain risk** |
| R-MFE-16 | Content Security Policy Cheat Sheet | **OWASP** | https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html | **The practical control for runtime-loaded federated remotes** (`script-src` allow-listing remote origins) |
| R-MFE-17 | Subresource Integrity | MDN | https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity | **Cited to justify why SRI is *insufficient* for MF remotes**, not as a mitigation: `remoteEntry` URLs resolve at runtime from a manifest and the fetched script is evaluated, not `<script integrity=…>` |
| R-MFE-18 | A06:2021 — Vulnerable and Outdated Components | **OWASP** | https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/ | Stale-shared-dependency risk in MFE architectures |
| R-MFE-19 | OpenTelemetry JS | OpenTelemetry | https://opentelemetry.io/docs/languages/js/ | Browser auto-instrumentation; the prerequisite for observing across federated boundaries |
| R-MFE-20 | A Catalog of Micro Frontends Anti-patterns → *Micro Frontend as the Goal* | Nabson P. et al. | https://arxiv.org/abs/2411.19472 | **The named anti-pattern this PRD's NG-03 forbids**: micro-frontending adopted as an end rather than a means |
| R-MFE-21 | Design system as a service | — | — | **REJECTED — no canonical source exists.** Industry vernacular. Use R-MFE-01's custodian governance model instead |
| R-MFE-22 | Micro-Frontends: A Rejected Dream | Eberhard Weber | — | **REJECTED — unlocatable.** No resolvable source. Use R-MFE-06 (peer-reviewed MLR) instead |
| R-MFE-23 | Micro Frontends are not for you | — | — | **REJECTED — unlocatable.** Use R-MFE-04 and R-MFE-06 |

---

## R-13 Module Federation

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-MF-01 | Module Federation (concepts) | webpack | https://webpack.js.org/concepts/module-federation/ | Runtime vs build-time federation; `remotes`/`exposes`/`shared`. **The `/plugins/module-federation/` path 404s — the concepts path is canonical** |
| R-MF-02 | ModuleFederationPlugin reference | webpack | https://webpack.js.org/plugins/module-federation-plugin/ | Option reference: `remotes`, `exposes`, `shared`, `runtime`, `library`, `dll` |
| R-MF-03 | Module Federation Plugin (shared options) | Rspack | https://www.rspack.org/plugins/module-federation-plugin | **The best single reference for the `shared` flags:** `singleton` = "Ensure that shared modules are only loaded once between different versions"; `requiredVersion` = "If the module version of the remote container does not meet this range, **the module will not be loaded**"; plus `eager`, `shareKey`, `shareScope` (default `"default"`), `import: false` |
| R-MF-04 | Standalone & Library | webpack | https://webpack.js.org/concepts/module-federation/#standalone-remote-modules | Standalone vs shareScope usage for independently-built remotes |
| R-MF-05 | Module Federation 2.0 (core README) | Module Federation / ByteDance | https://github.com/module-federation/core | 2.0 adds **dynamic type hinting, a Manifest, a Federation Runtime, and a Runtime Plugin System** |
| R-MF-06 | Manifest Specification | Module Federation | https://github.com/module-federation/core/blob/main/arch-doc/manifest-specification.md | **The authoritative schema.** Three artefacts: `mf-manifest.json` (runtime), `mf-stats.json` (full stats), `federation-manifest.json` (legacy name). `Manifest<T,K>` with `id`, `metaData` (`name`, `globalName`, **`buildInfo`**, `remoteEntry`, `types`, `pluginVersion`). States the manifest is "an interoperability artifact, **not** a replacement for the remote container contract". **Also lists `rsbuild` among the platform integrations** |
| R-MF-07 | Manifest field reference | Module Federation | https://module-federation.io/guide/advanced/manifest-fields | `StatsBuildInfo` = `{ buildVersion, buildName, target[], plugins[], excludePlugins[] }`. `mf-manifest.json` trims `shared`; `mf-stats.json` keeps `version`, `singleton`, `requiredVersion`, **`hash`**, `assets`, `usedExports` |
| R-MF-08 | `manifest` configuration | Module Federation | https://module-federation.io/configure/manifest | **Literal doc warning: "After setting, the preload function will be disabled!"** — `disableAssetsAnalyze` is the documented build-time↔preload-time trade-off |
| R-MF-09 | Data prefetch | Module Federation | https://module-federation.io/guide/data/data-prefetch | The `prefetch()` API — cite alongside R-MF-08 |
| R-MF-10 | Runtime plugins | Module Federation | https://module-federation.io/guide/runtime/runtime-plugins.html | `ModuleFederationRuntimePlugin` hooks; registered at build time, per instance, or globally. Use cases: rewrite remote URLs, customise manifest requests, patch script loading, override shared resolution, **add recovery/fallback** |
| R-MF-11 | `runtimePlugins` configuration | Module Federation | https://module-federation.io/configure/runtimeplugins | Option shape: `string[]` or `[path, options][]` |
| R-MF-12 | **`shareStrategy`** | Module Federation | https://module-federation.io/configure/shareStrategy | **Correction to a common miscitation:** the options are `'version-first'` (default) and `'loaded-first'`. **`'version-first'` eagerly loads all remote entries at init.** `'loaded-first'` defers remote loading on demand and is explicitly recommended for performance and offline resilience. `errorLoadRemote` lifecycle `beforeLoadShare` fires when a remote is offline under `version-first` |
| R-MF-13 | `shared` configuration | Module Federation | https://module-federation.io/configure/shared | Per-entry `eager: true` and `import: false` — the fine-grained equivalent of `shareStrategy` |
| R-MF-14 | **`experiments` configuration** | Module Federation | https://module-federation.io/configure/experiments | ⚡ **Quotable numbers.** `remoteEntry.js` gzip **21,437 B** unconfigured → **17,998 B** (`disableSnapshot` + `target:'web'`) → **5,381 B** (+ `externalRuntime: true`). Brotli 19,024 → 15,982 → **4,703 B**. Also `asyncStartup`, `disableRemote`, `disableShared` |
| R-MF-15 | Runtime size optimization | Module Federation | https://module-federation.io/guide/advanced/runtime-size-optimization | ⚡ Minified `remoteEntry.js` 73,154 B → 52,916 B (`disableRemote`, −27.66%) → 50,008 B (`disableShared`, −31.64%). Consumer `main.js` 79,328 B → 78,344 B with no `exposes` (−1.24%). Includes the verification procedure: baseline, one flag at a time, then test flows |
| R-MF-16 | `filename` configuration | Module Federation | https://module-federation.io/configure/filename | `[name].[contenthash:8].js`-style output → enables long-lived immutable CDN caching of `remoteEntry` |
| R-MF-17 | Module Federation (Rspack guide) | Rspack / ByteDance | https://www.rspack.org/guide/advanced/module-federation | Three generations: MF v1.0 (`ModuleFederationPluginV1`, "no longer being iterated"), MF v1.5 (`rspack.container.ModuleFederationPlugin`), MF v2.0 (`@module-federation/enhanced/rspack`). **Note: `rspack.dev` now redirects to `rspack.rs`** |
| R-MF-18 | Module Federation (Rsbuild guide) | Rsbuild / ByteDance | https://rsbuild.dev/guide/advanced/module-federation | **First-class MF support in Rsbuild.** `PARTIAL` — `rsbuild.dev/en/guide/…` 404s; drop the `/en` prefix |
| R-MF-19 | `@module-federation/rsbuild-plugin` | Module Federation | https://github.com/module-federation/core | Verified existing — named as a platform integration in R-MF-06 |
| R-MF-20 | webpack issue #15269 (MF RFC discussion) | webpack | https://github.com/webpack/webpack/issues/15269 | The public design thread where `singleton` / version-negotiation semantics were argued. **Use for "why `requiredVersion` exists"** |

---

## R-14 Web performance budgets and metrics

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-PERF-01 | Web Vitals | Google / web.dev | https://web.dev/articles/vitals | ⚡ **Thresholds:** LCP ≤ **2.5 s**, INP ≤ **200 ms**, CLS ≤ **0.1**, each at the **75th percentile**, segmented mobile/desktop. Pass = all three at p75 |
| R-PERF-02 | Largest Contentful Paint (LCP) | Philip Walton / web.dev | https://web.dev/articles/lcp | "Good LCP value is 2.5 seconds or less", measured at p75 |
| R-PERF-03 | Interaction to Next Paint (INP) | web.dev | https://web.dev/articles/inp | "An INP below or at 200 milliseconds means a page has good responsiveness" |
| R-PERF-04 | Cumulative Layout Shift (CLS) | web.dev | https://web.dev/articles/cls | Good CLS = 0; the practical p75 bar is 0.1 |
| R-PERF-05 | Total Blocking Time (TBT) | web.dev | https://web.dev/articles/tbt | **"< 200 milliseconds when tested on average mobile hardware."** Lab proxy for INP — explicitly not a substitute |
| R-PERF-06 | User-centric performance metrics | web.dev | https://web.dev/articles/user-centric-performance-metrics | **The argument for why budgets must be user-centric, not byte-counts** |
| R-PERF-07 | Performance budgets 101 | Addy Osmani / web.dev | https://web.dev/articles/performance-budgets-101 | The canonical modern performance-budgets explainer. `PARTIAL` — `/articles/performance-budgets` 404s |
| R-PERF-08 | Use Lighthouse for performance budgets | web.dev | https://web.dev/articles/use-lighthouse-for-performance-budgets | The `budget.json` example a PRD can quote: 3000 ms TTI, 1000 ms FMP, 125 KB JS, 300 KB total, 10 third-party requests |
| R-PERF-09 | Incorporate performance budgets into your build process | web.dev | https://web.dev/articles/incorporate-performance-budgets-into-your-build-tools | Comparison table: Lighthouse vs webpack vs bundlesize vs Lighthouse Bot |
| R-PERF-10 | Lighthouse — `budgets` configuration | GoogleChrome/lighthouse | https://github.com/GoogleChrome/lighthouse/blob/main/docs/configuration.md | **Budget format:** kilobytes (transfer size) and request counts; timings in ms. The legal CI-gating config surface |
| R-PERF-11 | `budget.json` schema | GoogleChrome | https://github.com/GoogleChrome/budget.json | Canonical schema. `resourceType`s: `document, font, image, media, other, script, stylesheet, third-party, total`. Worked example: 300 KB total / 150 KB script / 10 third-party |
| R-PERF-12 | Lighthouse — Overview | Chrome for Developers | https://developer.chrome.com/docs/lighthouse/overview | **Canonical replacement for the dead `/docs/lighthouse/configure`** |
| R-PERF-13 | Resource Summary audit | Chrome for Developers | https://developer.chrome.com/docs/lighthouse/performance/resource-summary | The request-count + transfer-size audit; the exact source of "keep requests low, keep bytes low" |
| R-PERF-14 | webpack `performance` hints | webpack | https://webpack.js.org/configuration/performance/ | `maxAssetSize`, `maxEntrypointSize` — in-build budget enforcement at the bundler layer |
| R-PERF-15 | **JavaScript — Web Almanac 2024** | Abdul Haddi Amjad, Nishu Goel / HTTP Archive | https://almanac.httparchive.org/en/2024/javascript | ⚡ **Market baseline: median JS payload 558 KB mobile / 613 KB desktop, +14% YoY**; mobile median 22 JS requests, p90 68 |
| R-PERF-16 | **Page Weight — Web Almanac 2025** | HTTP Archive | https://almanac.httparchive.org/en/2025/page-weight | **The current edition** (the JS chapter was retired and folded in). Median page 71 desktop / 66 mobile requests; median mobile 558 KB JS + 900 KB images; JS p75 ≈ 1.1 MB, p90 ≈ 1.7 MB |
| R-PERF-17 | Performance — Web Almanac 2025 | HTTP Archive | https://almanac.httparchive.org/en/2025/performance/ | Field-data CWV pass rates to benchmark a budget against reality |
| R-PERF-18 | Efficiently load third-party JavaScript | web.dev | https://web.dev/articles/third-party-javascript | Third-party JS as a distinct, uncontrollable budget line; says to **enforce a budget on it** |
| R-PERF-19 | `size-limit` | Andrey Sitnik / AI | https://github.com/ai/size-limit | **The tool cited for enforced JS budgets in CI.** Computes download+execute *time*, "a much more accurate metric compared to the size in bytes" |
| R-PERF-20 | `@size-limit/preset-small-lib` | AI | https://github.com/ai/size-limit/tree/main/packages/preset-small-lib | The small-library preset |
| R-PERF-21 | BundleWatch (formerly bundlesize) | Bundlewatch | https://github.com/bundlesize/bundlesize | `maxSize: "100kB"` per-file thresholds; GitHub status on PRs. `PARTIAL` — `selectel/bundlesize` is dead; this is the successor |
| R-PERF-22 | Lazy loading | web.dev | https://web.dev/articles/lazy-loading | The code-splitting performance case. `PARTIAL` — `/articles/code-splitting` and `/lazy-loading-guide` 404 |
| R-PERF-23 | Lazy loading (performance guide) | MDN | https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Lazy_loading | Independent second source |

---

## R-15 Backend resource efficiency (Node.js / NestJS)

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-BE-01 | Performance | NestJS | https://docs.nestjs.com/techniques/performance | ⚡ **"Fastify is significantly faster than Express, achieving nearly twice the benchmark results."** Nest defaults to Express for ecosystem reasons, not performance |
| R-BE-02 | Performance FAQ | NestJS | https://docs.nestjs.com/faq/performance | Companion |
| R-BE-03 | Injection scopes | NestJS | https://docs.nestjs.com/fundamentals/scopes | ⚡ **Two quotable numbers:** "A properly designed application that uses request-scoped providers **should not see latency increase by more than ~5%**"; and "For, say, **30k requests in parallel, there are 30k ephemeral instances of the controller**". Recommends `AsyncLocalStorage` to keep everything singleton |
| R-BE-04 | Lazy loading modules | NestJS | https://docs.nestjs.com/fundamentals/lazy-loading-modules | The documented startup-cost lever |
| R-BE-05 | Modules | NestJS | https://docs.nestjs.com/fundamentals/module-ref | The module system as an enforced encapsulation boundary |
| R-BE-06 | Custom providers | NestJS | https://docs.nestjs.com/fundamentals/custom-providers | DI tokens, `useFactory`, `useExisting` — the mechanism that keeps the composition root framework-agnostic |
| R-BE-07 | Keep-alive connections | NestJS | https://docs.nestjs.com/faq/keep-alive-connections | HTTP keep-alive / `server.keepAliveTimeout`; relevant to aggregator socket counts |
| R-BE-08 | Microservices — Introduction and Basics | NestJS | https://docs.nestjs.com/microservices/introduction | Transport-agnostic request/reply and event patterns; hybrid HTTP + broker apps |
| R-BE-09 | CLI options | Node.js | https://nodejs.org/api/cli.html | `--max-old-space-size` (MiB), `--max-semi-space-size` (MiB), `--heap-prof`, `--heap-snapshot-on-oom`. `--experimental-require-module` is the remaining experimental ESM flag |
| R-BE-10 | `perf_hooks` | Node.js | https://nodejs.org/api/perf_hooks.html | ⚡ `monitorEventLoopDelay({ resolution })`; default `resolution` **10 ms**; reports `percentile(n)` in **nanoseconds**. Gives a directly quotable event-loop-lag SLO |
| R-BE-11 | `worker_threads` | Node.js | https://nodejs.org/api/worker_threads.html | Separate V8 isolates in one process; `resourceLimits` incl. `maxYoungGenerationSizeMb`, `maxOldGenerationSizeMb` |
| R-BE-12 | `cluster` | Node.js | https://nodejs.org/api/cluster.html | Server-cluster primary ports across processes; `SO_REUSEPORT` |
| R-BE-13 | V8 | Node.js | https://nodejs.org/api/v8.html | `getHeapSnapshot()`, `getHeapStatistics()` |
| R-BE-14 | ES Modules | Node.js | https://nodejs.org/api/esm.html | ESM stable since Node 13.2 |
| R-BE-15 | The difference between development and production | Node.js | https://nodejs.org/en/learn/getting-started/nodejs-the-difference-between-development-and-production | ⚡ `NODE_ENV=production` makes Node **skip expensive per-process safety checks on `process.env`**. Free, citable perf win |
| R-BE-16 | distroless | GoogleContainerTools | https://github.com/GoogleContainerTools/distroless | Images without a shell or package manager; `static` (nonroot) variant |
| R-BE-17 | Multi-stage builds | Docker | https://docs.docker.com/build/building/multi-stage/ | The canonical multi-stage image pattern |
| R-BE-18 | Official Node Docker images | nodejs/docker-node | https://github.com/nodejs/docker-node | `-alpine` and `-slim` variants — citable "smaller base" lever |
| R-BE-19 | Sampling (OpenTelemetry concepts) | OpenTelemetry | https://opentelemetry.io/docs/concepts/sampling/ | "Sampling is one of the most effective ways to reduce the costs of observability **without losing visibility**" — while naming three real costs, including the **opportunity cost of missing critical info**. The argument for head-based (`ParentBased`, traceid-ratio) sampling |
| R-BE-20 | Express production best practices | Express | https://expressjs.com/en/advanced/best-practice-performance.html | Operational, not microbenchmark-driven |
| R-BE-21 | Benchmarking guide | Fastify | https://fastify.dev/docs/latest/Guides/Benchmarking/ | Ships `fastify-benchmark` for benchmarking **your app**, not a Fastify-vs-Express scorecard |
| R-BE-22 | Structured-logging cost | — | — | **REJECTED — no authoritative primary source exists.** Assert as a design requirement ("sample before export", R-BE-19), never as a measured figure |

---

## R-16 Build and CI resource efficiency

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-BUILD-01 | Why Turborepo? | Turborepo (Vercel) | https://turborepo.com/docs/core-concepts/why-turborepo | Vendor claims: build-time hashing, incremental work, task-graph local caching |
| R-BUILD-02 | Reference configuration (`turbo.json`) | Turborepo | https://turborepo.com/docs/reference/configuration | ⚡ **The silent cache-poisoning bug, verbatim:** with `envMode: "strict"`, "Passthrough values do not contribute to hashes for caching. If you want changes in these variables to cause cache misses, you will need to include them in `env` or `globalEnv`." Also `globalDependencies` → global hash; `globalEnv` → hash of all tasks |
| R-BUILD-03 | Structuring a repository | Turborepo | https://turborepo.com/docs/crafting-your-repository/structuring-a-repository | Explicit `apps/*` + `packages/*` split. **Hard constraint found:** "Turborepo does not support nested packages like `apps/**`". Per-package `package.json` required; one root `package.json` + one `turbo.json`. **No "how big should a package be" guidance is published** |
| R-BUILD-04 | Remote caching | Turborepo | https://turborepo.com/docs/core-concepts/remote-caching | HMAC-SHA256 signature verification for remote artefacts; "Turborepo treats **logs as artifacts**" — a cache-size cost line |
| R-BUILD-05 | Constructing CI | Turborepo | https://turborepo.com/docs/crafting-your-repository/constructing-ci | Task-graph-aware CI wiring |
| R-BUILD-06 | Core concepts | Turborepo | https://turborepo.com/docs/core-concepts | Turbo = task graph + remote caching |
| R-BUILD-07 | Managing dependencies | Turborepo | https://turborepo.com/docs/crafting-your-repository/managing-dependencies | Dependency declaration and `workspace:` protocol guidance |
| R-BUILD-08 | Mental model | Nx | https://nx.dev/docs/concepts/mental-model | Project graph, task graph, `affected`, **computation hashing**. "Nx caches the project graph, so it only reanalyzes the files you have changed" |
| R-BUILD-09 | Configure inputs | Nx | https://nx.dev/docs/guides/tasks--caching/configure-inputs | ⚡ **The concrete "why your CI is slow" citation.** Nx defaults inputs to `["default","^default"]` — **any change to any file in a dependent project busts the cache** |
| R-BUILD-10 | Configure outputs | Nx | https://nx.dev/docs/guides/tasks--caching/configure-outputs | Declaring outputs is what makes a task cacheable in Nx at all |
| R-BUILD-11 | Remote caching | Nx | https://nx.dev/docs/features/ci-features/remote-cache | Cache mechanics; replaying terminal output + artefacts |
| R-BUILD-12 | Affected | Nx | https://nx.dev/docs/features/ci-features/affected | Affected-based test/build selection in PR pipelines |
| R-BUILD-13 | Project Size (KB) | Nx | https://nx.dev/docs/kb/project-size | **Directly on-topic for resource efficiency.** Granularity drives `nx affected` effectiveness; split when tests get slow, split along ownership so CODEOWNERS stays honest, type checking scales with project boundaries |
| R-BUILD-14 | Resolve circular dependencies | Nx | https://nx.dev/docs/kb/resolve-circular-dependencies | Why circular deps degrade both architecture and the affected algorithm |
| R-BUILD-15 | Explore the project graph | Nx | https://nx.dev/docs/features/explore-graph | `nx graph` — the boundary-review visualisation |
| R-BUILD-16 | Remote caching | Bazel | https://bazel.build/remote/caching | Content-addressed action cache; `--disk_cache` with GC and an enforced storage limit; `--nodisk_cache`. **Also: stdout/stderr is "not a good signal for estimating cache hits"** — hence structured cache-miss statistics |
| R-BUILD-17 | Remote execution / Remote analysis | Bazel | https://bazel.build/remote | Canonical entry point for remote cache + remote execution |
| R-BUILD-18 | About Bazel | Bazel | https://bazel.build/about/intro | Google's build system designed around the mega-repo |
| R-BUILD-19 | Build cache hit ratio as a target | — | — | **REJECTED — no vendor-neutral primary source publishes a target hit ratio.** R-BUILD-16 provides the *mechanism* and the reason to use structured telemetry; the threshold is this PRD's own team SLO, attributed to no one |
| R-BUILD-20 | Rspack — `cache` | Rspack | https://rspack.dev/config/cache | ⚡ Verbatim: the persistent cache key includes "the **Rspack version, `config.name`, `config.mode`**"; and "Unlike webpack, **Rspack does not include any preset build dependencies by default**" — you must add your own `cache.buildDependencies`. Managed paths use the lockfile `version` field instead of hashing contents, "speeds up cache validation" |
| R-BUILD-21 | Rspack — `lazyCompilation` | Rspack | https://rspack.dev/config/lazy-compilation | ⚡ Verbatim: "**Lazy compilation is only effective for dev builds and does not affect production builds.**" Enabling `entries` turns entry modules into async chunks, so "dev and production artifacts may differ" |
| R-BUILD-22 | Motivation | pnpm | https://pnpm.io/motivation | `PARTIAL` — **vendor architectural claim, no published benchmark.** "if you have 100 projects using a dependency, you will have 100 copies"; content-addressable store adds only changed files; hard-linking consumes no additional disk space |
| R-BUILD-23 | Global cache | Bun | https://bun.sh/docs/install/cache | `PARTIAL` — **vendor architectural claim.** Packages live at `~/.bun/install/cache`; "if the cache already contains a version in the range specified by package.json, Bun uses the cached copy instead of downloading it again" |
| R-BUILD-24 | Isolated installs | Bun | https://bun.sh/docs/pm/isolated-installs | Bun's hoisted-isolation default — the modern answer to phantom dependencies |
| R-BUILD-25 | `bun install` CLI | Bun | https://bun.sh/docs/pm/cli/install | `--backend`, `--frozen-lockfile`, `--lockfile-only` |
| R-BUILD-26 | pnpm workspaces | pnpm | https://pnpm.io/workspaces | `pnpm-workspace.yaml`, workspace protocol |
| R-BUILD-27 | `npm ci` | npm | https://docs.npmjs.com/cli/v11/commands/npm-ci | **The determinism verb:** requires a lockfile, never writes it, wipes `node_modules` first. Contrast R-BUILD-28 |
| R-BUILD-28 | `npm install` | npm | https://docs.npmjs.com/cli/v11/commands/npm-install | The mutating counterpart — establishes the `ci` vs `install` distinction for CI determinism |
| R-BUILD-29 | `package-lock.json` | npm | https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json | Lockfile semantics, integrity hashes |
| R-BUILD-30 | SLSA — Provenance v1.2 | OpenSSF / SLSA | https://slsa.dev/spec/v1.2/provenance | `buildDefinition` + `runDetails`, subject digests, builder ID. The vocabulary for "reproducible from the commit alone" |
| R-BUILD-31 | SLSA — Provenance v1.1 and Levels | OpenSSF | https://slsa.dev/spec/v1.1/levels | Build L1–L4; the canonical phrasing for hermetic, reproducible builds |
| R-BUILD-32 | Dependabot | GitHub | https://docs.github.com/en/code-security/dependabot | Scheduled dependency updates |
| R-BUILD-33 | Renovate | Renovate (Mend) | https://docs.renovatebot.com/self-hosted-configuration/ | Scheduling, grouping, lockfile maintenance |
| R-BUILD-34 | Nix command reference | Nix project | https://nixos.org/manual/nix/stable/command-ref/ | `nix build`, `nix flake check`. **The determinism claim rests on the derivation hash over (name, version, builder, args, env, source), not on a blog** |
| R-BUILD-35 | Rspack — Architecture | Rspack | https://rspack.rs/api/javascript-api/architecture | The Rust-vs-JS boundary: SWC-based parse/transform, Rust-backed codegen and parallel traversal |
| R-BUILD-36 | Rspack — `experiments` | Rspack | https://rspack.rs/config/experiments | `experiments.css` (native CSS via Lightning CSS), `rspackFuture` |
| R-BUILD-37 | esbuild — `analyze` / `metafile` | Evan Wallace | https://esbuild.github.io/api/#analyze | The standard bundle-size measurement mechanism |
| R-BUILD-38 | source-map-explorer | danvk | https://github.com/danvk/source-map-explorer | Per-tree-shaking-frame bundle attribution — explains *why* bytes are present |
| R-BUILD-39 | Bundlephobia | Keith Cirkel et al. | https://bundlephobia.com/ | Minified/gzipped size per npm package. `PARTIAL` — crowdsourced, occasionally stale, **not a substitute for measuring your own bundle** |
| R-BUILD-40 | Rspack vs Vite memory | — | — | **REJECTED — no primary source exists.** Neither project publishes a reproducible memory benchmark. **The PRD mandates this as a named measurement, never as a cited fact** |
| R-BUILD-41 | Vite — Why Vite | Vite | https://vite.dev/guide/why.html | `PARTIAL` — **vendor source; contains no memory or CPU figures** |
| R-BUILD-42 | Why Use Pants? | Pants | https://v1.pantsbuild.org/why_use_pants.html | The monorepo-at-scale positioning: "a scalable version control system and a build system that can perform fine-grained dependency management among thousands of code modules in a single source tree" |
| R-BUILD-43 | Effective monorepos with Pants | Benjy Weinberger / Pants | https://www.pantsbuild.org/blog/2022/03/15/effective-monorepos-with-pants | Practitioner-level feature rationale |
| R-BUILD-44 | monorepo.tools | Dave Shade / community | https://monorepo.tools/ | Ecosystem landscape survey |

---

## R-17 Boundary enforcement

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-BND-01 | `boundaries` (Experimental) | Turborepo | https://turborepo.com/docs/reference/boundaries | ⚡ **Correction to a common claim.** `turbo boundaries` **does exist**: it checks (a) importing a file outside the package directory and (b) importing a package not declared in its `package.json`; supports `tags` with `dependencies.allow/deny` and `dependents.allow/deny`, applied transitively. **Governed by the Boundaries RFC and carries an Experimental label — this is exactly why a second enforcement path is mandatory (AC-01, RISK-11)** |
| R-BND-02 | Boundaries RFC | Vercel / Turborepo | https://github.com/vercel/turborepo/discussions/9435 | The design discussion behind `turbo boundaries` |
| R-BND-03 | eslint-plugin-boundaries | **Javier Brea** | https://github.com/javierbrea/eslint-plugin-boundaries | Lint-time element-type + dependency-policy enforcement for JS/TS. `PARTIAL` — **`Nick-vv/eslint-plugin-boundaries` is 404 / misattributed** |
| R-BND-04 | dependency-cruiser | Sander Verhulst / community | https://github.com/sverweij/dependency-cruiser | JS/TS dependency-graph validation with a rule DSL; the primary enforcer of "domains must not import frameworks" |
| R-BND-05 | Import Linter | **David Seddonym** | https://github.com/seddonym/import-linter | Layered/hexagonal contracts for Python. `PARTIAL` — **`sbidoul/import-linter` and `siddharthkp/import-linter` are both 404 / misattributed** |
| R-BND-06 | Import Linter documentation | Import Linter | https://import-linter.readthedocs.io/en/stable/ | `independents`, `layers`, `forbidden` contracts |
| R-BND-07 | `@nx/enforce-module-boundaries` | Nx | https://nx.dev/docs/features/enforce-module-boundaries | Tag-based `depConstraints` via ESLint **or Oxlint**, plus a language-agnostic Conformance rule. The only mainstream buildable module-boundary enforcement. "If all of them can depend on each other freely, chaos will ensue" |
| R-BND-08 | ArchUnit User Guide | TNG Technology Consulting | https://www.archunit.org/userguide/html/000_Index.html | **Architecture as code**: layered/onion/hexagonal rules as executable `ArchRule` assertions run in CI. The canonical fitness-function mechanism |
| R-BND-09 | madge | Paden Quast / community | https://github.com/pahen/madge | Circular-dependency detection for JS/TS; complements R-BND-04 for the "no cycles" fitness function |
| R-BND-10 | Nx — Project Size KB | Nx | https://nx.dev/docs/kb/project-size | Boundary granularity guidance that keeps `nx affected` cheap |
| R-BND-11 | Turborepo has no boundaries (negative claim) | — | — | **REJECTED as a citation target.** The substantive claim is true, but no positive Turborepo citation exists saying so. **Assert without citation, or cite R-BND-07 by contrast** |

---

## R-18 Configuration validation

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-CFG-01 | XII. Factor IX — Config | Wiggins / Heroku | https://12factor.net/config | "Store config in the environment"; config is a deploy-time concern, not a build-time one |
| R-CFG-02 | XI. Logs | Wiggins / Heroku | https://12factor.net/logs | Treat logs as event streams; no log rotation in the app |
| R-CFG-03 | zod | Colin McDonnell / Zod | https://github.com/colinhacks/zod | Schema declaration with static inference; `.strict()` rejects unknown keys |
| R-CFG-04 | JSON Schema Draft 2020-12 | IETF | https://json-schema.org/draft/2020-12/release-notes | See R-META-16. **The portable alternative when the validator must not be a JS runtime dependency** |

---

## R-19 Ownership and governance

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-OWN-01 | About CODEOWNERS | GitHub Docs | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners | CODEOWNERS syntax; location precedence (root, `.github/`, `docs/`); `@org/team-slug` mentions; `@@` docs-only ownership; `*` catch-all |
| R-OWN-02 | About protected branches | GitHub Docs | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches | **Required reviewers** — the mechanism that makes CODEOWNERS real; "dismiss stale reviews" |
| R-OWN-03 | DORA — Streamlining change approval | DORA / Google Cloud | https://dora.dev/capabilities/streamlining-change-approval/ | Evidence that fast, code-owner-driven approval correlates with throughput and stability |
| R-OWN-04 | DORA — The Four Keys | DORA | https://dora.dev/guides/dora-metrics-four-keys/ | Deployment frequency, lead time, change failure rate, recovery time |
| R-OWN-05 | DORA — Research and reports | DORA | https://dora.dev/research/ | The empirical base. **Note: no DORA finding on monorepo-vs-polyrepo exists — do not cite DORA for repo topology** |
| R-OWN-06 | DORA — DevOps capabilities | DORA | https://dora.dev/devops-capabilities/ | Capability taxonomy |

---

## R-20 Cost allocation and runtime resource management

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-COST-01 | The FinOps Framework | FinOps Foundation | https://www.finops.org/framework/ | Understand / Optimize / Operate / Govern |
| R-COST-02 | Capability: Allocation | FinOps Foundation | https://www.finops.org/framework/capabilities/allocation/ | **The showback/chargeback citation.** Tagging, shared-cost allocation, idle-cost attribution |
| R-COST-03 | Capability: Budgeting | FinOps Foundation | https://www.finops.org/framework/capabilities/budgeting/ | Budget-setting as a capability, not ad-hoc spreadsheets |
| R-COST-04 | Capability: Unit economics | FinOps Foundation | https://www.finops.org/framework/capabilities/unit-economics/ | **Cost per unit of business value** — the lever tying infra cost to a product metric |
| R-COST-05 | Managing resources for containers | Kubernetes | https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ | ⚡ **The overcommit argument:** "although actual memory or CPU resource usage on nodes is very low, the scheduler still refuses to place a Pod if the capacity check fails". CPU request = cgroup weight, limit = CFS quota **throttling**; memory limit = cgroup OOM. **Throttling, not rejection, is the right-sizing penalty** |
| R-COST-06 | Resource quotas | Kubernetes | https://kubernetes.io/docs/concepts/policy/resource-quotas/ | Namespace-as-budget; `compute-resource`, `requests.cpu`, `requests.memory`, `limits.memory` |
| R-COST-07 | Vertical Pod Autoscaler | Kubernetes SIG-Autoscaling | https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler | Recommender / updater / admission-controller; sets requests from usage; down-scales over-requesting pods. **Documented limitation: not compatible with pod-level `resources` stanzas** |
| R-COST-08 | KEDA — Scaling deployments | KEDA | https://keda.sh/docs/latest/concepts/scaling-deployments/ | Event-driven scaling from a 0 baseline — scales an aggregator on actual queue depth |
| R-COST-09 | Horizontal Pod Autoscaling | Kubernetes | https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ | HPA as the horizontal counterpart to VPA |

---

## R-21 Backend for Frontend — the boundary between composition and domain

| ID | Title | Author / Org | URL | Establishes |
|---|---|---|---|---|
| R-BFFD-01 | Backends for Frontends — "one BFF per client type" | Microsoft | https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends | **The basis for AC-04.** Frontend teams own their BFF; cross-cutting stays in APIM |
| R-BFFD-02 | Gateway Aggregation | Microsoft | https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-aggregation | The fan-out-and-merge mechanism, with an explicit warning against overusing it per-request |
| R-BFFD-03 | The BFF should aggregate and transform, not decide | Sam Newman | https://samnewman.io/patterns/architectural/bff/ | The source of the rule test T2 in §5 |

---

## R-22 Generic reusable-resource (slot) and per-domain asset catalogue

This catalogue does not include platform-as-a-service vendors (Retool, Salesforce, ServiceNow, Okta, Auth0, Stripe, Datadog and comparable proprietary SaaS), because this repository's boundaries are defined by **source-level ownership of interfaces**, and third-party SaaS interfaces are governed by their own vendor contracts rather than by this repository's `catalog/`. Adopting a vendor platform is a DEC entry, not an architecture default. Where a vendor tool is named in this PRD as a *measurement or CI mechanism*, it is cited in R-15, R-16, R-19 or R-20 under its own prefix.

---

## R-23 — Rejected references (never cite)

| Candidate | Why rejected | Substitute |
|---|---|---|
| Brian Foote, *Solid Considered a Harmful* | 404; no Wayback snapshot; the article does not exist | R-SOLID-08 (Martin's own qualification), R-SOLID-10 (Big Ball of Mud) |
| Martin Fowler, *MonolithMacro* bliki | 404 across four casings and three paths. **Commonly hallucinated** | R-MONO-06, R-MONO-07 |
| Martin Fowler, *Cache* and *Flyweight* bliki | 404. Fowler's full `eaaCatalog` contains neither entry | R-RES-06, R-RES-07 |
| Martin Fowler, `artifacts/versionedLinks.html` | 404 | R-MONO-10 |
| Martin Fowler bliki, *Presentation Integration Approaches* | No standalone page; the content is a section of R-MFE-01 | R-MFE-01 |
| Martin Fowler, *Monolithic Repositories* article | 404 | R-MONO-06 |
| brianfoote.blogspot.com root | Resolves but contains no SOLID-criticism post | — |
| ACM DL: Taibi 2022, Parnas 1972 | 403 bot-block. **DOIs are correct; cite the DOI, never the URL** | — |
| All `oreilly.com/library/view/…` links | 403 | Pearson product pages |
| all `dl.acm.org/…` and `cacm.acm.org/…` (automated) | 403 to automated clients | `research.google/pubs/…` or DOI |
| ACM DL abstract for *Micro-Frontends: Principles* | 403 | DOI 10.1145/3561846.3561853 |
| Evan Luton, *ruthlessly monorepo* | Medium 403; three mirrors 404 | R-MONO-16 (Microsoft's directional evidence) is strictly stronger |
| Microsoft VS Code, *why vscode adopts a monorepo* | 404 | R-MONO-16 … R-MONO-19 |
| Microsoft Research, *Scaling Git in the Microsoft Codebase* | 404 | R-MONO-16 … R-MONO-18 |
| Google Cloud, *Inside Google's Journey to One Monorepo* | HTTP 200 but **serves a 404 body** | R-MONO-14 |
| Google Research, Piper paper URL | `pub37748` resolves to an unrelated paper | Cite via R-MONO-14's reference list |
| `research.google/…/pubtools/5716.pdf` | HTTP 200 but **the wrong paper** (recsys sampling-bias) | R-RES-09 |
| `nx.dev/concepts/monorepos`, `/why-monorepo`, `/what-is-nx`, `/reference/enforce-module-boundaries` | 404 | R-MONO-06, R-MONO-07, R-BND-07 |
| `turborepo.com/docs/crafting-your-repository/boundaries` | 404 — no such page; `turbo boundaries` docs are at R-BND-01 | R-BND-01 |
| `bazel.build/concepts/{external,bzlmod,workspaces}` | 404 — moved | R-MONO-08, R-META-21 |
| `sre.google/sre-book/cascading-failures/` | 404 — it is a section of ch. 22 | R-RES-11 |
| `chromium.googlesource.com/…/docs/owners.md` | No such file — it is `docs/code_reviews.md` | R-MONO-38 |
| `www.chromium.org/developers/how-tos/owners-files/` | 404 | R-MONO-38 |
| `trunkbaseddevelopment.com/branches/` | 404 | R-MONO-26 (already cites the site) |
| `direnv.net/docs/*.html` | **All 404.** The docs are man pages under `/man/` | R-DIR-01, R-DIR-02, R-DIR-03 |
| `devenv.sh/reference/config/`, `/reference/direnv/`, `/reference/cli/`, `/background-processes/` | 404 — site restructured | R-DV-03, R-DV-10 |
| `backstage.io/docs/features/techdocs/overview/`, `…/software-model/`, `…/ownership/`, `/reference/components/info/` | 404 | R-META-07, R-META-09 |
| `operatorframework.io/what/*.html` | 404 — site restructured | R-META-05, R-META-06, R-META-07 |
| `nx.dev/features/nx-graph`, `/concepts/graph`, `/reference/dev-graph` | 404 | R-BUILD-08, R-BUILD-15 |
| `nix.dev/manual/nix/command-ref/…` (unversioned) | 404 — the `stable/` segment is required | R-NIX-01 … R-NIX-05 |
| `nixos.org/manual/nix/stable/command-ref/flakes` | 404 — flake commands live in the main reference | R-BUILD-34 |
| `www.pantsbuild.org/docs/*` | **All doc paths 404.** Client-rendered with no server-side routes | R-BUILD-42 … R-BUILD-44 |
| `devbox.sh`, `cachix.com`, `cachix.dev`, `docs.nix.dev`, `secretspec.org`, `sops.secrets.dev` | DNS / connection failure | R-DIR-06, R-DV-01, R-SCRT-01, R-SCRT-04 |
| `webpack.js.org/plugins/module-federation/` | 404 — canonical is `/concepts/module-federation/` | R-MF-01 |
| `webpack.js.org/guides/performance/` | 404 | R-PERF-14 |
| `rsbuild.dev/en/guide/…` | 404 — drop the `/en` prefix | R-MF-18 |
| `rspack.dev/guide/tech/module-federation` | 404 — now `rspack.rs` / `www.rspack.org` | R-MF-17 |
| `single-spa.js.org/docs/building-a-microfrontend-architecture/` | 404 | R-MFE-08 |
| `developer.chrome.com/docs/lighthouse/configure` | 404 — superseded | R-PERF-12, R-PERF-10 |
| `web.dev/articles/code-splitting`, `/lazy-loading-guide`, `/performance-budgets`, `/defining-performance-budgets` | 404 | R-PERF-22, R-PERF-07 |
| `web.dev/articles/performance-budgets` | 404 | R-PERF-07 |
| `modulefederation.io` (no hyphen) | **DNS: does not resolve** | `module-federation.io` (R-MF-07 … R-MF-16) |
| `github.com/web-infra-dev/module-federation-core` | 404 | `github.com/module-federation/core` (R-MF-05) |
| `almanac.httparchive.org/en/2025/javascript` | 404 — the JS chapter was retired and folded into Page Weight | R-PERF-16 |
| `github.com/selectel/bundlesize` | 404 — the successor is BundleWatch | R-PERF-21 |
| `apollographql.com/docs/graphos/routing/operations/query-plans` | 404 | R-AGGR-06 |
| `developer.mozilla.org/en-US/docs/Web/HTTP/2` and `/Reference/Protocols/HTTP/2` | 404 — MDN has no HTTP/2 guide | R-RES-20 (RFC 9113) |
| `kubernetes.io/docs/concepts/workloads/pods/qos-classes/` | 404 — QoS classes are defined inside the resources page | R-COST-05 |
| `docs.autoscaling.sh/vertical-pod-autoscaler/` | DNS failure | R-COST-07 |
| `npmjs.com/package/*` | 403 to automated clients | Cite the tool's own repository instead |
| `teamtopologies.com/key-concepts/{content-types,team-api}` | 404 | R-TT-01, R-TTA-01 (with its third-party caveat) |
| `github.com/sbidoul/import-linter`, `github.com/siddharthkp/import-linter` | 404 — misattributed | R-BND-05 |
| `github.com/Nick-vv/eslint-plugin-boundaries` | 404 — misattributed | R-BND-03 |
| `martinfowler.com/articles/patterns-overview-distributed.html` | 404 | R-BFF-27 |
| `stripe.com/blog/cache-stampede`, `stripe.com/engineering/redis-memcached-at-stripe/` | 404 | R-RES-08 (Redis docs) |
| `aws.amazon.com/builders-library/avoiding-unexpected-request-failures/` | 404 | R-RES-01 |
| `docs.pact.io/pact_jvm` | 404 | R-CDC-07 |
| `openapi.ts-rest.com` | Connection failed (000) | R-CDC-09 |
| `nx.dev/docs/getting-started/why-monorepo` and variants | 404 | R-MONO-06 |
| Fabricated statistic: "median team at 200–1,000 engineers maintains 40–80 repositories" | **Untraceable to Octoverse or any primary source. Rejected as AI-generated** | R-MONO-44 is the only adoption data cited |
| Folklore: "30–50% of changes touch multiple projects" | Unsourced | R-MONO-22 states the refactor-scaling argument qualitatively |
| Fastify vs Express independent benchmark | **None exists.** Only vendor numbers | R-BE-01 with the R-BE-21 caveat |
| Rspack vs Vite memory comparison | **No primary source exists** | R-BUILD-40 — mandate a measurement |
| Build cache hit ratio target | **No neutral source exists** | R-BUILD-16, R-BUILD-19 |
| "Design system as a service" | Industry vernacular, no canonical source | R-MFE-01's custodian model |
| OWASP Subresource Integrity Cheat Sheet | 404 — no such page | R-MFE-17 (MDN SRI) |
| OWASP supply-chain-security project page | 404 on all tried paths | R-MFE-15, R-MFE-16 |

---

## R-24 — Maintenance rule

1. A reference may be cited in the PRD only if it appears above with status `VERIFIED` or `PARTIAL` and its limitation is honoured.
2. Any URL added after 2026-10-14 must be fetched and confirmed before it is added.
3. When a URL is discovered to be dead, move it to R-9 immediately and substitute. Do not leave it in place with a footnote.
4. When two sources disagree, record both and mark which one is a vendor claim (R-MONO-44, R-BUILD-22, R-BUILD-23, R-BE-01, R-BUILD-41) and which is independent (R-MONO-21, R-MFE-04, R-MFE-06, R-MONO-14).
5. When a claim has **no** citable source — build cache hit ratio, bundler memory, Fastify-vs-Express — the PRD must express it as a **named measurement the team must take**, never as an asserted fact. See R-BUILD-19, R-BUILD-40, R-BE-01.

---

## R-25 — Addendum for TDD-CMS-001 (added 2026-10-14)

**Why this section exists.** TDD-CMS-001 needed evidence in six areas where v3.0.0 was thin or where the toolchain moved since the catalogue was frozen. Every URL below was fetched by HTTP on 2026-10-14 and its content read. Status follows the same vocabulary as R-0. Where a source is vendor documentation, it is marked as such and is used only for **the tool's own behaviour and constraints**, never as an independent performance claim.

### R-25a — Module Federation: optimisation flags, size table, bundler coverage

| ID | Title | Author / Org | URL | Status | Establishes |
|---|---|---|---|---|---|
| R-MF-21 | Optimize Runtime Size | Module Federation | https://module-federation.io/guide/advanced/runtime-size-optimization.html | VERIFIED | The `experiments.optimization` capability set: `disableRemote`, `disableShared`, `disableSnapshot`, `target`. **Load-bearing constraint:** `disableShared` "removes shared dependency registration, selection, and loading… **Use it only when the build has no `shared` configuration** and never registers or loads a shared dependency through runtime APIs". `disableRemote` "does not remove the producer-side `exposes`". Measured: 73,154 B → 52,916 B (`disableRemote`) → 50,008 B (`disableShared`); "reductions are not additive". |
| R-MF-22 | Configuration — `experiments` | Module Federation | https://module-federation.io/configure/experiments | VERIFIED | `externalRuntime` / `provideExternalRuntime` semantics: "Ensure the consumer provides this global … otherwise it will not work"; `provideExternalRuntime` is "only for pure consumer scenarios (no `exposes`)". **The published gzip `remoteEntry.js` table** — none 21,437 B · `disableSnapshot` 20,096 B · `target: web` 19,314 B · both 17,998 B · both + `externalRuntime` **5,381 B** · `disableSnapshot` off + `externalRuntime` **8,222 B**. |
| R-MF-23 | Runtime capability optimization options (Vite plugin) | module-federation/vite PR 947 | https://github.com/module-federation/vite/pull/947 | VERIFIED | Maps the optimisation flags to compile-time defines on the Vite surface; **warns** on `disableRemote: true` with non-empty `remotes` and on `disableShared: true` with non-empty `shared`. Also: `provideExternalRuntime` with any `exposes` throws. Bundle-level assertions verify code elimination, not just defines. |
| R-MF-24 | allow disabling unused capabilities (Core v2.8.0) | module-federation/core PR 4901 | https://github.com/module-federation/core/pull/4901 | VERIFIED | The upstream change behind R-MF-21's numbers. Confirms disabled capabilities use lightweight fallbacks and "fail with clear errors if they are invoked", and that the reductions "are not additive because the capability paths share some code". **Vendor source — cited for the tool's own behaviour only.** |

> **Attribution correction carried into TDD-CMS-001 GAP-01/GAP-02.** The optimisation flags live under `experiments.optimization` (`disableSnapshot`, `target`) and `experiments` (`externalRuntime`, `provideExternalRuntime`); `disableRemote` / `disableShared` are capability flags exposed through the same optimisation block. A remote that **has** a non-empty `shared` block must not set `disableShared`, and the published size table shows the ≤ 8 KB target is reached with `externalRuntime` + `target: 'web'` + `disableSnapshot` — not with `disableShared`.

### R-25b — Micro-frontends: cost, budgets, tracing across remotes

| ID | Title | Author / Org | URL | Status | Establishes |
|---|---|---|---|---|---|
| R-MFE-24 | Micro-frontend performance: costs and how to control them | Carlos Cifuentes (neuland) | https://carloscifuentes.dev/micro-frontends/micro-frontend-performance/ | VERIFIED | Practitioner decomposition of MFE cost into duplicated dependencies, extra requests, loading waterfall, **duplicated CSS**, and extra startup work; "a platform budget that nobody owns is ignored — give each remote its own budget and make its pipeline enforce it"; field data must be **tagged by route and by the remote that owns it**, or "a slow remote hides inside a global average". Basis for BUD-06 … BUD-09. |
| R-MFE-25 | Distributed Tracing Across Micro-Frontends | micro-frontend-architecture.com | https://micro-frontend-architecture.com/core-micro-frontend-architecture-tradeoffs/deployment-and-observability/distributed-tracing-across-micro-frontends/ | VERIFIED | The structural requirement behind TDD-CMS-001 D-19: **one tracer, owned by the host**, published on a guarded global; remotes obtain it and never construct a `WebTracerProvider`; `propagateTraceHeaderCorsUrls` must list remote and API origins or `traceparent` is silently dropped; OTLP-over-HTTP from a browser requires the host origin in the collector's CORS allow-list; a duplicated `@opentelemetry/api` copy produces two root spans — i.e. it must be a shared singleton like React. |
| R-MFE-26 | A Comparative Study of Micro-Frontend and Modular Monolith Frontend Architectures | IJCSMC 15(2), 2026 | https://ijcsmc.com/docs/papers/February2026/V15I2202614.pdf | **PARTIAL** | Measured magnitudes only, **never a target**: same React/Vite application built as a shell + 8 remotes vs one modular build — 113.84 s vs 10.65 s build time, ~50.75 MiB vs ~1.85 MiB emitted JS, with Lighthouse favouring the monolith. Thesis-grade venue; methodology is single-implementation. Cited solely to size BUD-06. Substitute for any strong claim: re-measure on our own routes (PRD RES-07, DEC-20). |

### R-25c — Boundary enforcement: what Turbo boundaries can and cannot express

| ID | Title | Author / Org | URL | Status | Establishes |
|---|---|---|---|---|---|
| R-BND-12 | boundaries — reference | Turborepo | https://turborepo.dev/docs/reference/boundaries | VERIFIED | **Still labelled experimental.** Scope is the *package manager workspace*: (1) importing a file outside the package's directory, (2) importing a package not declared in `package.json`. Tag rules express `dependencies` / `dependents` allow/deny and "apply even for dependencies of dependencies". Tag names — **not npm package names** — are the unit of the rules. |
| R-BND-13 | [RFC] Boundaries | vercel/turborepo discussion 9435 | https://github.com/vercel/turborepo/discussions/9435 | VERIFIED | Design intent plus the community's open requests, which mark the boundary of today's capability: **"npm packages in allow/deny … for rules like 'browser packages never depend on pg, drizzle-orm or @aws-sdk/*'"** is a *request*, not a feature; also requests for tsconfig-`paths` alias resolution, a baseline/exclusion file with staleness errors, and ignoring generated files. Provides the `exclusions` mechanism with mandatory `reason`. |

> **Correction carried into TDD-CMS-001 §13.1 / GAP-07.** PRD FR-14 and AC-01 describe `turbo boundaries` and `dependency-cruiser` as two mechanisms for one constraint. They are not redundant over the same ground: boundaries operate on the **package graph by tag**, and cannot today express a **third-party npm deny list** or an **intra-package layer rule**. AC-03 and AC-08 are therefore enforced by `dependency-cruiser` + ESLint alone (paired per RISK-11), and those checks remain mandatory irrespective of Turborepo's maturity.

### R-25d — Clean Architecture: the inner layer as a property, not a diagram

| ID | Title | Author / Org | URL | Status | Establishes |
|---|---|---|---|---|---|
| R-CA-08 | Simplify Your Code: Functional Core, Imperative Shell | Google Testing Blog | https://testing.googleblog.com/2025/10/simplify-your-code-functional-core.html | VERIFIED | Pure, testable business logic separated from the shell that performs effects; core tested with no mocks and no infrastructure. Basis for TDD-CMS-001 D-14, which adds "domain/ is a functional core" to PRD D-10's dependency rule. |
| R-CA-09 | Functional Software Architecture — functional core, imperative shell | functional-architecture.org | https://functional-architecture.org/functional_core_imperative_shell/ | VERIFIED | "The functions in the core never call the shell"; and the honest caveat: the shell "is likely to contain substantial parts of the domain logic and grow quite complex". This caveat is the reason TDD-CMS-001 §9.1 forbids the shell from holding domain state (ALG-1 step 4) rather than merely recommending it. |

### R-25e — Metadata-driven architecture

| ID | Title | Author / Org | URL | Status | Establishes |
|---|---|---|---|---|---|
| R-META-26 | Descriptor Format of Catalog Entities | Backstage | https://backstage.io/docs/features/software-catalog/descriptor-format | VERIFIED | `relations` is **read-only and derived**: "Entity descriptor YAML files are not supposed to contain this field… relations… are to be considered the authoritative source". `spec.providesApis` / `spec.consumesApis` generate the relations. **Load-bearing for PRD §8.2's correction:** "a plugin would do better to consume the relation than `spec.owner` … it could be taken from a CODEOWNERS file nearby". |
| R-META-27 | Well-known Relations between Catalog Entities | Backstage | https://backstage.io/docs/features/software-catalog/well-known-relations/ | VERIFIED | The `ownedBy`/`ownerOf`, `providesApi`/`apiProvidedBy`, `consumesApi`/`apiConsumedBy` pairs, and that relations are directional with an opposite type at the other end. Basis for TDD-CMS-001 ROW-01 … ROW-11. |
| R-META-28 | System Model | Backstage | https://backstage.io/docs/features/software-catalog/system-model | VERIFIED | APIs are "a first class citizen and the primary way to discover existing functionality"; API **visibility** (public / restricted / private); a System "hides its resources and private APIs between the components for any consumers". Basis for treating an interface — not a deployable — as the unit of ownership in TDD-CMS-001 §7. |
| R-META-29 | Creating the catalog graph | Backstage (repository doc) | https://raw.githubusercontent.com/backstage/backstage/master/docs/features/software-catalog/creating-the-catalog-graph.md | VERIFIED | The catalog "should not be considered the ultimate source of truth … advisable to use the Backstage Catalog as a **caching mechanism**", with GitOps and scaffolder-authored PRs as the write path. Independent corroboration of PRD D-09's caveat. Also: a BFF is modelled as **two components** (website + service), and "it's not the api that consumes the other api, it's the component that consumes the other api". |
| R-META-30 | Introduction (language, unification) | CUE | https://cuelang.org/docs/introduction/ | VERIFIED | Types and values are unified; combination is order-independent (associative, commutative, idempotent) over a lattice; provenance is GCL/Borg at Google. **Recorded for PRD DEC-24, not adopted:** the decisive property is that constraints from several teams can be combined *without a schema/data split*, which zod does not give. |
| R-META-31 | How CUE works with JSON Schema | CUE | https://cuelang.org/docs/concept/how-cue-works-with-json-schema/ | VERIFIED | Bidirectional CUE ↔ JSON Schema (`cue import`, `cue def`), and that CUE definitions are **closed by default**, mapping to `additionalProperties`. Supports DEC-24's stated fallback: JSON Schema remains the portable interchange, so a future CUE adoption is additive, not a migration. |

### R-25f — Developer environment: devenv 2.x

| ID | Title | Author / Org | URL | Status | Establishes |
|---|---|---|---|---|---|
| R-DV-15 | devenv 2.0: A Fresh Interface to Nix | Cachix | https://devenv.sh/blog/2026/03/05/devenv-20-a-fresh-interface-to-nix/ | VERIFIED | devenv 2.0 replaces multi-`nix`-CLI invocations with a C FFI backend, gives **incremental evaluation caching** (sub-100 ms when nothing changed), adds native shell reloading, and states "**direnv isn't needed anymore with `devenv shell`** but it's still supported". Breaking changes: `devenv build` emits JSON, `container --copy` removed, native process manager default, `git-hooks` no longer an implicit input. **Vendor source, used for the tool's own behaviour.** |
| R-DV-16 | Binary Caching | Cachix | https://devenv.sh/binary-caching/ | VERIFIED | Built-in Cachix integration; `devenv.cachix.org` is a default pull cache mirroring the official NixOS cache for the `devenv-nixpkgs/rolling` input; on a multi-user install the Nix daemon only honours substituters requested by `trusted-users`. Explains the *mechanism* behind RES-03/RES-04 and why a warm shell is achievable while a cold one is bounded by closure cache-hit rate. |
| R-DV-17 | Direnv integration | Cachix | https://devenv.sh/integrations/direnv/ | VERIFIED | **Corrects the `.envrc` form shown in PRD §9.** Upstream's canonical snippet is `source_url "<pinned raw URL>" "<sha256>"` followed by `use devenv` — i.e. the activation script is itself **pinned by hash**, which satisfies PRD D-11 better than `eval "$(devenv direnvrc)"`. `devenv init --include-envrc` is new in 2.2. Also confirms `direnv allow` is the reviewable trust step DEC-07 relies on. |

> **Correction carried into TDD-CMS-001 GAP-08.** (a) PRD DEC-07's citation of "upstream now recommends `devenv hook`" is stale as of devenv 2.0 — upstream now says direnv is unnecessary with `devenv shell`'s native reload. DEC-07's *reason* (reviewability of the trust decision) is unaffected, but the reference and the `.envrc` snippet must be re-verified against 2.x. (b) The unpinned `eval "$(devenv direnvrc)"` form in PRD §9 and FR-18 conflicts with D-11; the pinned `source_url` + sha256 form does not. (c) `git-hooks` is no longer a default devenv input, so any hook relied on by FR-01/FR-17 verification must be declared explicitly in `devenv.yaml`.

### R-25g — Standards required by TDD Part II (security, errors, deployment)

| ID | Title | Author / Org | URL | Status | Establishes |
|---|---|---|---|---|---|
| R-INT-01 | Problem Details for HTTP APIs (RFC 9457) | IETF / HTTP WG | https://www.rfc-editor.org/rfc/rfc9457.html | VERIFIED | The standard `application/problem+json` shape (obsoletes RFC 7807). Adopted in TDD INT-02 so gateway, aggregator and context failures share one error representation, which is what makes partial responses renderable without per-team error envelopes. |
| R-INT-02 | JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens (RFC 9068) | IETF / OAuth WG | https://www.rfc-editor.org/rfc/rfc9068.html | VERIFIED | The access-token profile a **resource server** validates locally. Basis for TDD §22.2 step 7: a bounded-context service verifies the end-user session itself, with no call back to the shell or aggregator — which is what keeps the composition tier out of the authorisation path (ADR-0015). |
| R-SEC-01 | OWASP API Security Top 10 — 2023 | OWASP | https://owasp.org/API-Security/editions/2023/en/0x11-t10/ | VERIFIED | The authoritative enumeration behind TDD §22.1. Load-bearing for two specific rows: **API1 Broken Object Level Authorisation** motivates per-*object* authorisation and the denial cases in the contract suite (ADR-0020), and **API5 Broken Function Level Authorisation** motivates the deny-by-default route coverage check (ADR-0021). Cited in place of the OWASP pages already listed as REJECTED in R-23. |
| R-DEP-01 | XII. Build, release, run — The Twelve-Factor App | Wiggins / Heroku | https://12factor.net/build-release-run | VERIFIED | Separation of build, release and run. The mechanism behind TDD §23.1's "build once, promote the same artefact, never rebuild per environment", and behind rollback-by-pointer-change for images and config. Pairs with R-CFG-01 (config, which ADR-0001 already separates from versioning). |
