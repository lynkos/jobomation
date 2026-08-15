# AI-Assisted Job Discovery and Application Management System

## Background

### Context

Finding suitable early-career software engineering roles is difficult when relying primarily on conventional job boards and keyword searches. Search results frequently contain roles that are nominally “entry level” but are poorly matched because of seniority, compensation, location, technical domain, applicant volume, or application overhead. Conversely, unusually strong matches may use unexpected titles such as *Cyber Security Engineer*, *Research Engineer*, *Infrastructure Engineer*, or *Systems Engineer* and therefore may not appear in conventional searches for entry-level software engineering roles.

The proposed system is a **local-first, AI-assisted job discovery, evaluation, and application-management platform**. It continuously collects job postings from a curated set of employer career pages and other sources, normalizes and deduplicates them, eliminates clearly unsuitable positions, evaluates ambiguous or promising positions against a structured candidate profile, and presents a prioritized set of opportunities through an interactive dashboard.

The system is intended to optimize for **high-quality opportunity discovery rather than application volume**. It should help identify unusual but credible matches that conventional job-search systems may overlook.

The system will additionally track applications and their outcomes, enabling empirical analysis of the job search over time.

The initial implementation will evolve from an existing automated job-application project, but the primary focus will shift from autonomous application submission toward **discovery, decision support, and human-controlled application workflows**.

### Scope

The system will:

* Monitor configured employer career pages and supported job sources.
* Detect newly published, changed, and removed job postings.
* Normalize heterogeneous job postings into a canonical representation.
* Deduplicate postings appearing through multiple sources.
* Extract structured requirements and metadata from job descriptions.
* Apply deterministic eligibility and preference rules.
* Use one or more LLMs for semantic candidate/job comparison where deterministic rules are insufficient.
* Rank jobs using multiple dimensions rather than simple keyword similarity.
* Identify unusual matches whose job titles may not obviously correspond to the candidate's experience.
* Present new and previously evaluated jobs through a local dashboard.
* Allow the user to accept, reject, defer, or otherwise classify recommendations.
* Track application lifecycle and outcomes.
* Record sufficient provenance to explain why a job received a particular evaluation.
* Learn from explicit user feedback over time.
* Store application data locally.
* Support relocation of persistent data, including to external storage.
* Allow different LLM implementations to be evaluated or substituted without redesigning the application.
* Expose selected application capabilities and data through a Model Context Protocol (MCP) server.
* Represent selected job-market relationships as a knowledge graph for graph-aware retrieval and reasoning.
* Allow MCP clients or agents to query both canonical job data and graph relationships without bypassing application-layer constraints.

### Solution Requirements (Goals)

The primary goals are:

**G1 — Discover unusual high-quality matches.**
The system should identify jobs based on their actual responsibilities and requirements rather than relying primarily on job titles.

**G2 — Reduce manual search effort.**
The user should review a small number of promising opportunities rather than manually inspecting hundreds of irrelevant postings.

**G3 — Preserve human application control.**
The system may assist with applications, but consequential decisions and final submission should remain under explicit user control.

**G4 — Explain recommendations.**
For each recommended job, the system should explain relevant strengths, concerns, eligibility issues, and the reason for its ranking.

**G5 — Distinguish eligibility from desirability.**
A highly interesting job with questionable eligibility should not be treated identically to a mediocre job with near-certain eligibility.

**G6 — Support multidimensional ranking.**
Potential dimensions include:

* technical alignment;
* experience/level alignment;
* eligibility;
* career value;
* compensation;
* location;
* personal interest;
* application effort;
* estimated competition;
* posting freshness.

**G7 — Minimize unnecessary LLM usage.**
Straightforward decisions should use deterministic rules. LLM evaluation should primarily address ambiguity, semantic similarity, requirement interpretation, and synthesis.

**G8 — Remain local-first and portable.**
Persistent application state should reside locally. Moving the application's data to another local volume should require little more than configuration changes.

**G9 — Maintain model independence.**
Evaluation logic should not depend directly on one commercial or local LLM provider.

**G10 — Produce useful job-search analytics.**
The system should eventually answer questions such as:

* What percentage of applications receive responses?
* Which role families produce the most interviews?
* Does application freshness correlate with response?
* Do high model-fit scores correlate with interview selection?
* Do referrals measurably affect outcomes?
* Which recommendation models most closely match user judgments?

**G11 — Remain extensible.**
Adding a new employer, job source, evaluator, ranking strategy, or UI should not require substantial changes to unrelated components.

**G12 — Provide a standards-based AI integration surface.**
The system should expose a useful subset of its data and operations through MCP so that compatible clients and agents can query Jobomation without coupling directly to its internal Python APIs or SQLite schema.

**G13 — Support graph-aware job-market reasoning.**
The system should represent relationships among jobs, companies, skills, locations, and role families in a knowledge graph that can support traversal, contextual retrieval, and LLM-assisted reasoning.

**G14 — Keep MCP and graph features grounded in canonical application state.**
MCP tools/resources and graph projections should derive from canonical Jobomation models and persisted state rather than becoming independent sources of truth.

### Out of scope (Non-goals)

The initial system will not:

* autonomously submit applications without user review;
* indiscriminately mass-apply to jobs;
* attempt to defeat CAPTCHAs or anti-bot systems;
* fabricate or embellish candidate qualifications;
* automatically answer legally or personally consequential application questions without explicit user approval;
* optimize primarily for total application count;
* guarantee completeness across all jobs available on the Internet;
* require cloud deployment;
* require a distributed architecture;
* require a vector database;
* require LLM fine-tuning;
* require a separate frontend/backend architecture;
* attempt to predict interview probability with unsupported precision.

Automated form filling may be considered later, but final submission remains a separate concern from job discovery and ranking.

### Assumptions

* The system initially serves one user.
* It runs primarily on a single macOS workstation.
* Python is the primary implementation language.
* SQLite is the initial persistent database.
* Internet connectivity is available during collection and external-model inference.
* Local inference should remain possible for some or all AI functionality.
* Job-source availability and formats may change without notice.
* Some employer websites will require browser automation rather than simple HTTP requests.
* Job descriptions frequently contain ambiguous, inconsistent, or incomplete metadata.
* Applicant counts reported by third-party job platforms may be missing or unreliable and should not be treated as ground truth.
* Candidate preferences will change over time.
* The ranking algorithm will therefore require versioning and iteration.
* Explicit user feedback is considered higher-quality preference evidence than inferred preferences.

## Overview

The system is organized as a pipeline with persistent state between stages:

<div align="center">
  <img src="assets/pipeline.svg" alt="Pipeline overview"/>
</div>

A job should move through the pipeline asynchronously. Collection should not require immediate LLM evaluation, and evaluation should not require the dashboard to be running.

Persistent state acts as the boundary between major stages.

The central conceptual distinction is between:

1. **Job facts** — what the source says.
2. **Extracted facts** — structured interpretation of the posting.
3. **Candidate facts** — known candidate experience and constraints.
4. **Evaluation** — interpretation of candidate/job compatibility.
5. **Preference** — whether the user personally wants the job.
6. **Application state** — what happened after the decision to apply.

These should remain distinct in both the database and application architecture.

## Detailed design

### System-context diagram(s)

At the system level:

```text
                         External Systems
        ┌────────────────────────────────────────────┐
        │                                            │
        │  Greenhouse  Lever  Workday  Custom Sites  │
        │      │        │       │          │         │
        └──────┼────────┼───────┼──────────┼─────────┘
               │        │       │          │
               └────────┴───┬───┴──────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │                       │
                │   Job Intelligence    │
                │       System          │
                │                       │
                └───────┬──────┬────────┘
                        │      │
                  ┌─────┘      └──────┐
                  ▼                   ▼
          ┌──────────────┐     ┌──────────────┐
          │ Local Models │     │ External LLM │
          │              │     │ APIs         │
          └──────────────┘     └──────────────┘
                  │                   │
                  └─────────┬─────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Local SQLite │
                    │   Database   │
                    └──────┬───────┘
                           │
                           ▼
                      ┌─────────┐
                      │  User   │
                      └─────────┘
```

Internally, the major modules are:

```text
jobintel/
├── collectors/
├── normalization/
├── extraction/
├── deduplication/
├── filtering/
├── evaluation/
├── ranking/
├── candidate/
├── applications/
├── analytics/
├── dashboard/
├── persistence/
├── scheduling/
├── mcp/
├── knowledge_graph/
└── config/
```

The exact package organization remains subject to implementation experience.

### APIs

#### Internal job-source interface

All collectors should expose a common abstraction:

```python
class JobSource(Protocol):
    async def fetch_jobs(self) -> list[RawJob]:
        ...
```

Source-specific implementations may include:

```text
GreenhouseSource
LeverSource
AshbySource
SmartRecruitersSource
WorkdaySource
CustomHTMLSource
SearchSource
```

`RawJob` preserves source-specific data without requiring downstream components to understand the source.

#### Normalization interface

```python
class JobNormalizer(Protocol):
    def normalize(self, raw_job: RawJob) -> Job:
        ...
```

Normalization converts heterogeneous source data into the canonical job schema.

#### Evaluation interface

Evaluation should be model-independent:

```python
class JobEvaluator(Protocol):
    async def evaluate(
        self,
        candidate: CandidateProfile,
        job: Job,
        extracted: ExtractedRequirements,
    ) -> JobEvaluation:
        ...
```

#### LLM provider interface

```python
T = TypeVar("T")

class LLMProvider(Protocol):
    async def generate_structured(
        self,
        messages: list[Message],
        output_schema: type[T],
    ) -> T:
        ...
```

Possible implementations:

```text
OpenAIProvider
AnthropicProvider
GeminiProvider
OllamaProvider
OpenAICompatibleProvider
```

The evaluator should depend on `LLMProvider`, not directly on an SDK.

#### MCP server interface

Jobomation should expose a standards-based MCP server over selected application-layer capabilities.

Initial tools may include:

```text
search_jobs(...)
get_job(...)
list_targets()
query_job_graph(...)
```

Representative behavior:

* `search_jobs(...)` queries canonical persisted jobs using structured criteria such as title, company, location, active/filter state, skills, or evaluation metadata.
* `get_job(...)` retrieves the canonical representation of a specific job together with available extracted requirements and evaluation context.
* `list_targets()` exposes configured collection targets and source types.
* `query_job_graph(...)` performs bounded graph traversal or relationship queries over the job-market knowledge graph.

Initial resources may include:

```text
job://<source>/<id>
schema://jobs
graph://job/<id>
graph://skill/<name>
```

The MCP layer should delegate to existing application services and repositories rather than implementing independent persistence, filtering, ranking, or business logic.

The initial MCP surface should be primarily read/query oriented. Any future mutating tools must preserve Jobomation's human-control guarantees and authorization boundaries.

#### MCP client / agent integration

At least one MCP-compatible client or agent should be able to connect to the server and answer queries such as:

```text
Find currently active infrastructure jobs that match Python + Terraform and explain why.
```

The client should obtain evidence through MCP tools/resources rather than receiving direct database access.

The MCP integration is an interface layer, not a replacement for deterministic filtering, canonical storage, evaluation, or ranking.

#### User-action interface

The dashboard should expose application-layer operations such as:

```python
review_job(job_id, decision)
mark_applied(job_id, metadata)
update_application_stage(application_id, stage)
dismiss_job(job_id, reason)
override_evaluation(job_id, feedback)
```

Whether these become HTTP endpoints is deliberately undecided. A Python dashboard may initially invoke the application service directly.

### Data storage

SQLite is the initial persistence layer.

A configurable path determines database location:

```python
DATABASE_PATH=~/JobIntel/data/jobs.sqlite3
```

or:

```python
DATABASE_PATH=/Volumes/ExternalSSD/JobIntel/jobs.sqlite3
```

No application code should assume a fixed physical database location.

Recommended initial database settings include WAL mode, foreign-key enforcement, appropriate busy timeouts, short write transactions, and explicit indexes for frequent queries.

#### Core entities

Likely entities include:

```text
jobs
raw_jobs
job_sources
companies
locations
job_requirements
job_skills

candidate_profiles
candidate_experiences
candidate_skills
candidate_preferences

evaluations
evaluation_dimensions
evaluation_feedback

applications
application_events

collector_runs
model_invocations

knowledge_nodes
knowledge_edges
knowledge_graph_versions
```

The knowledge-graph tables may initially be implemented in SQLite as a projection over canonical application state. A dedicated graph database is optional and should be justified by query complexity, scale, or operational requirements rather than assumed up front.

#### Job

Representative fields:

```text
id
company_id
source_id
source_job_id
canonical_url

title
description
location
remote_type
employment_type

salary_min
salary_max
salary_currency

posted_at
first_seen_at
last_seen_at
removed_at

description_hash
status
```

#### Raw job

Raw source material should be retained separately:

```text
id
source_id
source_job_id
retrieved_at
payload
payload_hash
parser_version
```

This allows normalization/parsing bugs to be corrected without reacquiring historical postings.

#### Job-market knowledge graph

The system should maintain a graph representation of selected job-market entities and relationships.

Initial node types:

```text
Job
Company
Skill
Location
RoleFamily
```

Initial relationships:

```text
Job     -[:REQUIRES]->        Skill
Job     -[:PREFERS]->         Skill
Job     -[:POSTED_BY]->       Company
Job     -[:LOCATED_IN]->      Location
Job     -[:HAS_ROLE_FAMILY]-> RoleFamily
Skill   -[:RELATED_TO]->      Skill
```

Additional relationships may be introduced only when they have a clear retrieval, ranking, analytics, or reasoning use case.

The graph should be treated as a derived representation of canonical application state. Canonical jobs, extracted requirements, and other persisted records remain the source of truth.

Graph construction should therefore be repeatable and versioned. Changes to extraction logic, ontology, or graph-building rules should permit the graph to be rebuilt without corrupting historical application data.

Possible uses include:

* discovering jobs through related skills rather than title keywords;
* identifying unusual but credible role-family matches;
* traversing from a candidate skill to related skills and then to jobs;
* explaining why a job was surfaced;
* providing structured context to LLMs and MCP clients.

A dedicated graph database such as Neo4j may be evaluated later. The initial design should not require one.

#### Evaluation

An evaluation should be immutable or effectively versioned.

```text
id
job_id
candidate_profile_version

evaluator_version
model_provider
model_name
prompt_version

eligibility
eligibility_confidence

technical_fit
experience_fit
career_fit
location_fit
compensation_fit
interest_score
competition_risk

overall_score
priority

strengths
concerns
unusual_fit_reason

created_at
```

Re-evaluation creates a new evaluation rather than destroying historical results.

#### Application event model

Application status should preferably be event-backed:

```text
DISCOVERED
REVIEWED
APPLICATION_STARTED
SUBMITTED
OA
RECRUITER_SCREEN
TECHNICAL_INTERVIEW
FINAL_INTERVIEW
OFFER
REJECTED
GHOSTED
WITHDRAWN
```

An `application_events` table preserves transitions and timestamps, enabling later funnel analysis.

### Code and pseudo-code

The primary collection/evaluation loop may resemble:

```python
async def process_source(source: JobSource) -> None:
    raw_jobs = await source.fetch_jobs()

    for raw in raw_jobs:
        persist_raw(raw)

        job = normalize(raw)

        existing = find_existing_job(job)

        if existing:
            update_last_seen(existing)

            if content_changed(existing, job):
                update_job(existing, job)
                queue_for_evaluation(existing.id)

            continue

        job = persist_job(job)

        duplicate = find_semantic_duplicate(job)

        if duplicate:
            associate_duplicate(job, duplicate)
            continue

        queue_for_evaluation(job.id)
```

Evaluation:

```python
async def evaluate_job(job_id: JobId) -> None:
    job = repository.get_job(job_id)
    candidate = candidate_repository.current_profile()

    extracted = extract_requirements(job)

    deterministic = rule_engine.evaluate(
        candidate,
        job,
        extracted,
    )

    if deterministic.hard_reject:
        save_evaluation(
            evaluation_from_rules(deterministic)
        )
        return

    semantic = await evaluator.evaluate(
        candidate,
        job,
        extracted,
    )

    evaluation = ranking_engine.combine(
        deterministic,
        semantic,
        candidate.preferences,
    )

    save_evaluation(evaluation)
```

The dashboard inbox query becomes approximately:

```sql
SELECT ...
FROM jobs
JOIN latest_evaluations
WHERE review_state = 'UNREVIEWED'
ORDER BY
    priority DESC,
    overall_score DESC,
    posted_at DESC;
```

#### Knowledge-graph projection

A graph projection may be rebuilt or incrementally updated from canonical records:

```python
def project_job_to_graph(job_id: JobId) -> None:
    job = repository.get_job(job_id)
    extracted = requirement_repository.get_latest(job_id)

    upsert_node("Job", job.id, title=job.title)
    upsert_node("Company", job.company_id)
    add_edge("Job", job.id, "POSTED_BY", "Company", job.company_id)

    if job.location:
        location_id = canonicalize_location(job.location)
        upsert_node("Location", location_id)
        add_edge("Job", job.id, "LOCATED_IN", "Location", location_id)

    for skill in extracted.required_skills:
        skill_id = canonicalize_skill(skill)
        upsert_node("Skill", skill_id)
        add_edge("Job", job.id, "REQUIRES", "Skill", skill_id)
```

Graph queries should be bounded and deterministic where possible. LLMs may synthesize or explain graph results, but should not fabricate missing nodes or edges.

#### Evaluation caching

LLM evaluation should be cacheable using a key derived from:

```text
job_description_hash
candidate_profile_version
evaluator_version
prompt_version
model_name
```

If all inputs are unchanged, the evaluation does not need to be repeated.

#### Deterministic constraint representation

Requirements should not initially be represented as simple booleans.

For example:

```python
class ConstraintSeverity(Enum):
    HARD_FAIL = auto()
    STRONG_NEGATIVE = auto()
    WEAK_NEGATIVE = auto()
    NEUTRAL = auto()
    POSITIVE = auto()
    STRONG_POSITIVE = auto()
```

This allows:

```text
"5+ years required"
```

to be treated differently from:

```text
"3 years preferred"
```

and:

```text
"experience with Kubernetes preferred"
```

to be treated differently from:

```text
"production Kubernetes administration required"
```

#### Recommendation feedback

Explicit feedback should be recorded:

```python
class ReviewDecision(Enum):
    APPLY = auto()
    MAYBE = auto()
    DISMISS = auto()
```

Optional dismissal reasons:

```text
BAD_FIT
TOO_SENIOR
BAD_LOCATION
BAD_COMPENSATION
LOW_INTEREST
APPLICATION_TOO_EXPENSIVE
COMPANY_NOT_INTERESTING
DUPLICATE
OTHER
```

This dataset may later support personalized learning-to-rank.

### Degree of constraint

The architecture intentionally constrains some decisions while leaving others replaceable.

#### Fixed or strongly preferred

**Python**

The primary implementation language.

**SQLite**

The initial persistent datastore due to portability, simplicity, and single-user/local-first operation.

**Canonical internal schemas**

Collectors and LLMs must not leak source/provider-specific representations throughout the codebase.

**Human-controlled submission**

Application submission remains an explicit user decision.

**Provider-independent LLM interface**

Business logic must not directly depend on a specific model vendor.

**Raw-data preservation**

Source data should remain available for debugging and reprocessing.

**Canonical-state-backed MCP and graph layers**

MCP tools/resources and knowledge-graph projections must derive from canonical application services and persisted state rather than becoming independent systems of record.

#### Intentionally unconstrained

The following remain implementation choices:

* dashboard framework;
* Plotly/Dash versus another UI;
* ORM;
* HTTP library;
* browser-automation framework;
* scheduling framework;
* local LLM runtime;
* external LLM provider;
* exact ranking algorithm;
* embeddings;
* vector search;
* notification mechanism;
* API framework;
* deployment packaging;
* MCP client implementation;
* knowledge-graph storage engine;
* graph-query implementation.

Technology should be introduced when requirements justify it rather than because it appears in the initial architecture.

### Test plan

Testing should occur at several levels.

#### Unit tests

Test deterministic components extensively:

```text
normalization
salary parsing
location parsing
experience extraction
constraint classification
ranking calculations
hashing/caching
application state transitions
configuration handling
```

Representative requirement tests should include adversarial wording:

```text
"3+ years required"
"3 years preferred"
"2-4 years preferred"
"BS plus 2 years or equivalent experience"
"recent graduates encouraged to apply"
"5 years experience, including internships"
```

#### Collector contract tests

Each collector should be tested against saved fixtures rather than requiring live network access.

For example:

```text
tests/fixtures/greenhouse/
tests/fixtures/lever/
tests/fixtures/workday/
```

A source website changing should break one collector, not silently corrupt downstream data.

#### Integration tests

Test:

```text
raw posting
→ normalization
→ persistence
→ filtering
→ evaluation
→ ranking
→ dashboard query
```

against a temporary SQLite database.

#### MCP contract tests

Test the MCP server independently from any particular LLM client.

Cover:

```text
tool discovery and schemas
resource discovery and URI handling
valid structured queries
invalid arguments
unknown job/resource identifiers
database/repository failures
serialization
bounded graph queries
```

Tests should verify that MCP tools return the same underlying application data and business-rule outcomes as direct application-layer calls.

#### Knowledge-graph tests

Test graph construction and traversal using deterministic fixtures.

Verify:

* canonical entities produce the expected nodes and edges;
* duplicate skills/companies/locations are canonicalized correctly;
* graph rebuilds are reproducible;
* removed or changed jobs update graph state correctly;
* graph queries do not invent relationships;
* bounded traversals return stable results.

Representative graph queries should include:

```text
jobs requiring Python
jobs related to Terraform through related skills
infrastructure-role jobs in a target location
jobs posted by a specific company
```

#### MCP client / agent integration tests

Run at least one MCP-compatible client or agent against a test server and verify end-to-end behavior for representative natural-language requests.

The test should ensure that answers are grounded in tool/resource results and that failures are surfaced rather than silently replaced with unsupported model output.

#### LLM evaluation tests

Create a fixed benchmark set of job descriptions manually labeled:

```text
excellent match
reasonable match
borderline
poor match
clearly ineligible
```

Run candidate models against the same set.

Measure:

* agreement with human judgment;
* false-negative rate;
* false-positive rate;
* structured-output reliability;
* latency;
* inference cost;
* consistency across repeated runs.

False negatives deserve particular attention because the system's purpose is partly to discover unconventional matches.

#### Ranking evaluation

User decisions provide implicit ground truth.

Possible metrics include:

```text
Precision@K
Recall of manually identified strong matches
NDCG
pairwise ranking agreement
```

More important than any single metric is:

> Are jobs the user actually wants to review consistently near the top?

#### Regression testing

Interesting historical postings should become permanent regression cases.

If a known unusually strong match is ranked poorly after changing prompts/models/rules, the test suite should expose the regression.

#### Portability testing

Periodically test:

```text
1. Shut down application.
2. Copy database to another directory/volume.
3. Change DATABASE_PATH.
4. Restart.
5. Verify complete functionality and history.
```

This is a first-class requirement rather than an incidental property.

## Alternatives

### Conventional job-board search

**Advantages:** no development effort; broad coverage.

**Disadvantages:** poor semantic matching, noisy entry-level classification, duplicated postings, weak personalization, and limited control over ranking.

Rejected as the primary discovery mechanism, but third-party job boards may remain supplemental sources.

### Fully autonomous application agent

**Advantages:** maximizes application throughput and minimizes manual work.

**Disadvantages:** reduced control, risk of incorrect application answers, poor handling of ambiguous requirements, potentially low-quality applications, and misalignment with the objective of selective high-quality applications.

Rejected as the initial architecture.

### PostgreSQL

**Advantages:** stronger concurrent-write behavior, richer server/database functionality, excellent extensibility, mature full-text search, straightforward future vector-search integration.

**Disadvantages:** requires database-server administration and complicates the desired single-file/local-portability model.

SQLite is preferred initially. Database abstraction should avoid making future migration unnecessarily difficult.

### Dedicated graph database

**Advantages:** native graph traversal, expressive graph query languages, visualization/tooling, and straightforward representation of multi-hop relationships.

**Disadvantages:** adds another datastore and operational dependency, duplicates some canonical state, and may be unnecessary at single-user/local scale.

A dedicated graph database such as Neo4j is optional. The initial graph may be stored or projected using SQLite/in-memory structures, provided the graph abstraction does not preclude later migration.

### React/Next.js frontend

**Advantages:** maximum UI flexibility and mature frontend ecosystem.

**Disadvantages:** introduces another language/runtime/toolchain and frontend/backend boundary.

Remains a viable future choice. A Python-native dashboard such as Dash may provide faster initial development.

### Dash/Plotly

**Advantages:** Python-native, well suited to analytical dashboards, rapid development, integrated visualization.

**Disadvantages:** less flexible than a dedicated frontend for highly customized interaction and visual design.

Currently a strong candidate but not an architectural requirement.

### Entirely local LLM inference

**Advantages:** privacy, zero per-request API expense, offline evaluation, reproducibility.

**Disadvantages:** potentially weaker nuanced reasoning and greater local inference latency.

Viable and should be benchmarked.

### Entirely external LLM inference

**Advantages:** access to frontier models and generally strong semantic reasoning.

**Disadvantages:** cost, network dependency, privacy considerations, provider dependency.

Viable but not required.

### Hybrid LLM inference

Use deterministic filtering followed by inexpensive/local inference and frontier-model evaluation for promising or ambiguous jobs.

This is currently the preferred conceptual strategy, subject to empirical testing.

### Fine-tuned model

Not justified initially. Prompted instruction models should first establish baseline performance. Fine-tuning should be considered only after a sufficiently large labeled dataset exists and measurable shortcomings justify it.

## Cross-cutting concerns

**Privacy.** Candidate data may include employment history, compensation preferences, citizenship/work-authorization information, application history, and other personal information. Sensitive information should not be sent to external models unless required. Evaluation prompts should include only information necessary for the task.

**Security.** Secrets such as API keys must not be stored in source control or the SQLite database in plaintext application records. Environment variables, OS keychain facilities, or another appropriate secret-management mechanism should be used.

**Explainability.** Recommendations should expose reasons rather than only scores. The user must be able to determine why a job was promoted or rejected.

**Auditability.** Evaluations should retain model, prompt, candidate-profile, and evaluator versions.

**Reproducibility.** Deterministic stages should produce reproducible results. Model nondeterminism should be recorded and evaluated rather than ignored.

**Cost.** LLM invocation counts, tokens, latency, and estimated external inference cost should be tracked.

**Performance.** Expensive processing should occur asynchronously and should not block dashboard interaction. Cached evaluations should prevent unnecessary repeated inference.

**Reliability.** Failure to collect from one source should not prevent other sources from processing. Collector failures should be isolated and recorded.

**Source volatility.** Employer sites and ATS implementations can change. Collectors should therefore remain modular and observable.

**Data quality.** Missing salary, location, posting date, and experience requirements are expected. Missing values must remain explicitly unknown rather than being fabricated.

**Model drift.** Changing models or model versions may materially change rankings. Evaluation provenance and benchmark tests should expose such changes.

**Candidate-profile evolution.** The candidate profile must be versioned. New experience, skills, preferences, or constraints should permit reevaluation without destroying previous results.

**Bias and false precision.** Scores are ranking aids, not objective probabilities. An `88` technical-fit score should not be presented as an 88% probability of suitability or interview selection.

**User attention.** The dashboard should optimize for decision-making rather than engagement. It should favor finite queues such as **New**, **High Priority**, **Maybe**, and **Reviewed** rather than infinite-scroll discovery.

**Portability.** Persistent state should not depend on absolute paths beyond explicit configuration. Database relocation and backup should remain straightforward.

**MCP safety and authority.** MCP is an interface into Jobomation, not an authority escalation mechanism. Tools should expose only intended operations, validate inputs, and preserve explicit human control over consequential actions.

**Graph provenance.** Graph nodes and edges should be traceable to canonical records, extraction outputs, or explicit ontology rules. LLM-generated hypotheses must not be persisted as factual graph relationships without an explicit validation step.

**Observability.** Structured logs and execution records should make it possible to answer:

```text
When was this company last checked?
Did collection succeed?
How many postings were found?
Which were new?
Why was this job filtered?
Which model evaluated it?
Why did it receive this ranking?
```

## Milestones / Rollout Plan

A practical rollout sequence is:

1. **Canonical collection vertical slice** — collector → raw preservation → normalization → SQLite → dashboard.
2. **Deterministic decision support** — structured extraction, eligibility/preference rules, filtering, and explanations.
3. **Semantic evaluation and ranking** — candidate profile, provider-independent LLM interface, cached/versioned evaluations, ranking inbox.
4. **MCP interface** — expose job search, retrieval, targets, schemas, and related contextual resources through MCP.
5. **Knowledge graph** — project jobs, companies, skills, locations, and role families into a graph and add bounded traversal/query support.
6. **MCP + graph agent workflow** — allow an MCP-compatible client or agent to answer grounded job-search questions using canonical data and graph traversal.
7. **Feedback and analytics** — review decisions, application lifecycle, ranking evaluation, and job-search funnel analytics.
8. **Application assistance** — optional form-filling or other user-approved assistance without autonomous submission.

Each milestone should preserve an end-to-end useful system rather than requiring the entire envisioned architecture to be complete before Jobomation is usable.

## References

References will be populated as implementation decisions are made. Expected reference categories include:

* SQLite documentation
* Python documentation
* selected ORM documentation
* selected dashboard framework documentation
* ATS/job-source API documentation
* browser-automation documentation
* LLM provider API documentation
* local inference runtime documentation
* structured-output/schema documentation
* ranking/recommender-system literature
* learning-to-rank literature

Architectural decisions that warrant significant trade-off analysis should eventually be captured as separate ADRs, for example:

```text
ADR-001: SQLite as initial persistence layer
ADR-002: Human approval required for application submission
ADR-003: Provider-independent LLM abstraction
ADR-004: Dashboard technology
ADR-005: Job-source collection strategy
ADR-006: Local vs external model routing
ADR-007: Ranking model
```