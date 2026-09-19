## Decision 006 — Centralized Configuration

### Decision
Use Pydantic Settings with a .env file for application configuration.

### Reason
The application contains environment-specific configuration such as
database credentials and OpenRouter API credentials.

These values should not be hard-coded into application source code.

### Benefits
- Keeps secrets outside source code
- Makes local development easier
- Allows different configurations for development and production
- Provides validation of required configuration values

### Security
The .env file is excluded from Git using .gitignore.
.env.example is committed as a safe configuration template.

## Decision 007 — Asynchronous SQLAlchemy

### Decision
Use SQLAlchemy's asynchronous engine and AsyncSession.

### Reason
The backend is built with FastAPI and uses I/O-heavy database
operations. Asynchronous database access fits the application's
request-handling model.

### Technology
SQLAlchemy Async + asyncpg + PostgreSQL.

### Architectural benefit
Database access remains separated from API routes and business
logic.

## Decision 008 — Dockerized PostgreSQL

### Decision
Run PostgreSQL using Docker Compose.

### Reason
A containerized database provides a consistent development environment
and avoids requiring developers to install PostgreSQL directly.

### Decision 009 — PostgreSQL + pgvector

### Decision
Use pgvector as the vector storage layer for RAG.

### Reason
The application already requires PostgreSQL for relational data.
Using pgvector allows both relational and vector data to live within
the same database.

### Trade-off
A dedicated vector database could be considered for a much larger
production system, but PostgreSQL + pgvector keeps this prototype
simpler and reduces infrastructure complexity.

## Decision 010 — Workload as a First-Class Domain Entity

### Decision
Represent each submitted computational workload as a persistent
database entity.

### Reason
The optimizer needs a structured representation of resource
requirements and scheduling constraints before it can evaluate
cloud resources.

### Research connection
The CEGP scheduling policy described in the research paper
operates on jobs/workloads and considers their deadlines during
resource allocation.

---

## Decision 011 — UUID Workload IDs

### Decision
Use PostgreSQL UUIDs for workload identifiers.

### Reason
UUIDs provide globally unique identifiers and avoid coupling
the application to sequential database IDs.

This is more suitable for a system that may eventually operate
across distributed cloud services.

## Decision 012 — Separate Cloud Infrastructure and Carbon Data

### Decision
Store cloud infrastructure information separately from carbon
emission information.

### Reason
Infrastructure characteristics such as CPU capacity, memory,
storage and DCiE do not necessarily change at the same frequency
as regional carbon intensity.

Carbon intensity can be treated as time-dependent data.

### Benefit
This design allows the optimizer to combine:

Cloud infrastructure
+
Current environmental conditions

when making scheduling decisions.

---

## Decision 013 — Include DCiE and CPU Efficiency

### Decision
Include DCiE and CPU power efficiency in the cloud-provider model.

### Reason
These parameters are part of the carbon-aware resource evaluation
described in the research paper.

They allow the optimizer to consider the efficiency of the
underlying infrastructure rather than looking only at raw
electricity consumption.

## Decision 014 — Time-Dependent Carbon Data

### Decision
Store carbon intensity as a separate time-stamped entity.

### Reason
Carbon intensity is an environmental measurement and may vary
over time, unlike relatively stable infrastructure properties.

### Benefit
The optimizer can eventually select resources based on the
carbon intensity expected during workload execution.

---

## Decision 015 — Normalize Carbon Data

### Decision
CarbonData references CloudProvider through provider_id.

### Reason
Provider and region information already exists in CloudProvider.

Duplicating this information in CarbonData could create
inconsistencies.

### Benefit
The database maintains a clear one-to-many relationship:

CloudProvider → CarbonData

---

## Decision 016 — Track Data Source

### Decision
Store the source of every carbon measurement.

### Reason
The prototype will initially use research/simulation data and
may later incorporate external carbon-intensity sources.

Recording the source improves transparency and data provenance.

## Decision 020 — Use pgvector for RAG

### Decision
Store RAG embeddings directly in PostgreSQL using pgvector.

### Reason
PostgreSQL is already required for the application's relational
data. Using pgvector avoids introducing a separate vector database
for the prototype.

### Benefit
The application can perform both relational queries and vector
similarity searches using the same database infrastructure.

---

## Decision 021 — Store Knowledge Chunks as Documents

### Decision
Represent each retrievable knowledge chunk as a Document record.

### Reason
The project deadline requires a focused RAG implementation.
Separate source-document and chunk tables would add complexity
without providing significant benefit for the MVP.

### Stored information
- Source name
- Source type
- Chunk index
- Text content
- Embedding vector

---

## Decision 022 — Track Knowledge Provenance

### Decision
Store source information with every knowledge chunk.

### Reason
AI-generated explanations should be traceable to the research
material used by the retrieval system.

This also makes the RAG pipeline easier to debug.

## Decision 023 — Use Alembic for Database Migrations

### Decision

Use Alembic to manage PostgreSQL schema migrations.

### Reason

The application contains multiple related database models and
will continue evolving during development.

Manually modifying the database schema would make development
and deployment difficult to reproduce.

Alembic provides version-controlled migrations that allow the
database schema to evolve alongside the application code.

### Design

SQLAlchemy Models
        ↓
Base.metadata
        ↓
Alembic Autogenerate
        ↓
Migration
        ↓
PostgreSQL

### Interview takeaway

Database schema changes should be treated as version-controlled
application changes rather than manual database operations.

## Decision 024 — Keep Carbon Data Separate from Provider Data

### Decision

Store carbon-intensity measurements in a separate CarbonData
entity instead of storing a single carbon-intensity value directly
inside CloudProvider.

### Reason

Cloud infrastructure characteristics and carbon intensity have
different lifecycles.

Infrastructure characteristics such as CPU capacity and DCiE
change relatively slowly, while carbon intensity can vary over
time.

### Benefit

This allows the optimizer to use historical or time-specific
carbon measurements when making scheduling decisions.

### Research connection

The research paper treats carbon emissions as an important
factor in carbon-aware scheduling.

### Interview takeaway

Environmental data should be modeled as time-varying data rather
than as a static property of a cloud provider.

## Decision 025 — Keep Numerical Calculations Deterministic

### Decision

Energy, cost and carbon calculations will be performed by
dedicated deterministic services rather than by the LLM.

### Reason

Numerical optimization requires reproducibility and traceability.

The LLM may be used to explain results or orchestrate tools,
but it should not generate authoritative infrastructure metrics.

### Architecture

AI Layer
    ↓
Tool / Service
    ↓
Deterministic Calculation
    ↓
Verified Result
    ↓
AI Explanation

## Decision 026 — Deterministic Carbon Calculation

### Decision

Calculate CO2 emissions using a deterministic service.

### Formula

CO2 emissions =
energy consumption × carbon intensity

### Reason

Carbon emissions are a quantitative optimization metric and
must be reproducible.

The LLM should not independently calculate environmental
metrics because generated numerical values cannot be treated
as authoritative infrastructure measurements.

### Architecture

EnergyService
    ↓
Energy (kWh)
    ↓
CarbonService
    ↓
CO2 emissions (kg)
    ↓
Optimization Engine

## Decision 027 — Implement a Baseline Alongside CEGP

### Decision

Implement an EST-inspired baseline in addition to the CEGP
optimization algorithm.

### Reason

An optimization algorithm should be evaluated relative to a
baseline rather than presented in isolation.

### Comparison

EST focuses on execution timing.

CEGP considers carbon emissions, energy consumption and cost
while enforcing the workload deadline.

### Research connection

The research paper compares CEGP with an EST scheduling approach.

### Limitation

The prototype uses execution time as an availability proxy and
therefore does not claim to reproduce the paper's full simulation
environment.

## Decision 028 — Use an Optimization Orchestration Service

### Decision

Create OptimizationService as the orchestration layer between
database repositories/models, calculation services and algorithms.

### Reason

Individual services should have focused responsibilities.

OptimizationService coordinates those components without duplicating
their internal logic.

### Benefit

The same calculation and algorithm components can later be used by:

- REST APIs
- automated workflows
- the AI agent
- tests
- future scheduling interfaces

### Architecture

API / Agent
     ↓
OptimizationService
     ↓
Calculation + Algorithm Layers
     ↓
PostgreSQL

## Decision 029 — Expose optimization through FastAPI

### Decision:  
Expose the deterministic optimization engine through a dedicated FastAPI endpoint.

### Reason:
The optimizer needs a clean interface for external clients, future frontend integration, and the AI agent.

### Design:

HTTP Request
    ↓
FastAPI API Layer
    ↓
OptimizationService
    ↓
Deterministic Services
    ↓
CEGP / EST

## Decision 030 — Model provider-specific execution performance

### Decision: 
Add `execution_time_factor` to the CloudProvider model.

### Reason: 
The EST baseline requires execution-time differences between providers to make a meaningful provider selection.

### Formula:
execution_time = workload runtime × provider execution_time_factor

### Important:
The prototype values are simulated and are not presented as real-world cloud-provider benchmarks.

### Database decision:
The field was introduced through a separate Alembic migration because the initial database migration had already been applied.

### Benefit:
The model can later be extended with measured or historical performance data without changing the EST algorithm itself.

## Decision 031 — Do not claim algorithm superiority from the prototype dataset

### Observation:
CEGP and EST selected the same provider for the current seeded workload.

### Decision:  
Treat this as an observed prototype result rather than evidence that either algorithm is superior.

### Reason:  
The current dataset contains only three simulated providers and one demonstration workload. It is insufficient for a general performance comparison.

### Evaluation principle:
Future evaluation should compare multiple workloads, provider configurations, carbon-intensity conditions, deadlines, energy consumption, and costs.

### Goal:
Demonstrate the difference between optimization objectives without artificially forcing different algorithm outcomes.
 
## Decision 032 — Use PostgreSQL + pgvector for RAG storage

### Decision:
Store document chunks and their embeddings in the existing PostgreSQL database using pgvector.

### Reason:
The project already uses PostgreSQL for workloads, providers, carbon data, and optimization results. Using pgvector avoids introducing a separate vector database for the prototype.

### Architecture:

Documents
   ↓
Chunks
   ↓
Embeddings
   ↓
PostgreSQL + pgvector

### Additional decision:
Prevent duplicate ingestion by checking whether a source has already been stored.

### Benefit:
The same database can contain both structured optimization data and unstructured RAG knowledge while maintaining a clear separation at the repository/service level.

## Decision 033 — Separate retrieval from generation

### Decision:
Keep the RAG retriever independent from the LLM.

### Reason:
Retrieval and answer generation are different responsibilities.

### Architecture:

Query
  ↓
Embedding
  ↓
Vector Search
  ↓
Relevant Context
  ↓
LLM
  ↓
Answer

## Decision 034 — Use PostgreSQL + pgvector for semantic retrieval

### Decision: 
Store research-document embeddings in PostgreSQL using pgvector.

### Reason:
- PostgreSQL is already the primary application database.
- pgvector provides vector similarity search without introducing another database.
- The same database can store structured optimization data and unstructured knowledge chunks.
- This keeps the prototype architecture manageable.

### Validation:
39 research-paper chunks were successfully embedded and stored. A semantic query successfully returned five relevant chunks using cosine-distance similarity.

### Boundary:
The RAG system retrieves contextual knowledge but does not replace deterministic optimization calculations.

## 035 — Separate RAG Retrieval from LLM Generation

### Decision:
Use a dedicated RAG service to combine semantic retrieval with LLM generation.

### Reason:
- Retrieval and generation have different responsibilities.
- Retrieved research context provides grounding for the LLM.
- The architecture allows the retrieval system and LLM provider to be changed independently.
- The deterministic optimization engine remains independent from the generative AI layer.

### Validation:
A test question successfully retrieved relevant research-paper chunks and produced a grounded answer through OpenRouter.

### Boundary:
The LLM is not responsible for numerical energy, carbon, cost, or optimization calculations.

## 036 — Keep deterministic optimization outside the LLM

### Decision:
The GreenCloud agent may invoke the optimization engine but must not implement or reproduce its calculations.

### Reason:
- Numerical optimization should be deterministic and testable.
- LLM-generated calculations can be inconsistent.
- The optimization engine already contains the CEGP and EST implementations.
- Separating orchestration from computation makes the system easier to validate.

### Validation:
The agent successfully invoked CEGP and returned the values produced by `OptimizationService`.

### Future extension:
Replace keyword-based routing with model-driven function/tool calling while retaining deterministic backend tools.

## Decision 037 — Use Agentic Tool Calling for Optimization

Date: 2026-09-19

### Decision

The GreenCloud Optimizer will use LLM tool calling to connect the AI agent with deterministic application capabilities.

The LLM will not directly perform optimization calculations. Instead, it can invoke explicitly defined application tools such as:

- `optimize_workload`
- `search_greencloud_knowledge`

### Reason

The project requires an agentic AI component while maintaining numerical reliability.

Allowing an LLM to calculate energy consumption, carbon emissions, cost, or optimization scores would introduce unnecessary uncertainty and make the system difficult to validate.

Tool calling provides a separation between:

- AI reasoning and orchestration
- deterministic computation
- database operations

### Result

The agent can now receive a natural-language optimization request and invoke the deterministic GreenCloud optimization engine.

---

## Decision 038 — Keep Provider Information Database-Backed

Date: 2026-09-19

### Decision

The optimization tool will return the selected provider's human-readable information in addition to its UUID.

The returned provider information includes:

- provider name
- provider type
- region

### Reason

The optimization engine identifies providers using database UUIDs, while the AI assistant needs meaningful information for its response.

Returning provider metadata directly from PostgreSQL prevents the LLM from having to infer provider identity from a UUID.

### Result

The agent can explain optimization results using factual provider information retrieved from the database.

---

## Decision 039 — Application-Provided Workload IDs Are Authoritative

Date: 2026-09-19

### Decision

When a workload ID is supplied by the application, the agent must use that workload ID for optimization execution.

The LLM is not responsible for generating, modifying, or correcting application workload UUIDs.

### Reason

Database identifiers are application state and must remain under application control.

During agent testing, relying on the LLM to reproduce the UUID introduced the possibility of malformed or incorrect identifiers.

### Result

The agent can still determine when the optimization tool should be called, but the application controls which workload is actually optimized.

This provides a clearer trust boundary:

LLM
 ↓
Determines which tool to call
 ↓
Application
 ↓
Controls workload identity
 ↓
Deterministic optimization

## Decision 040 — Return Structured Tool Results to the Agent

Date: 2026-09-19

### Decision

The optimization tool returns structured JSON-compatible data instead of a pre-written natural-language response.

### Reason

The agent needs access to the underlying optimization metrics so that the LLM can generate an explanation appropriate to the user's question.

Structured results also keep computation separate from presentation.

### Result

The tool returns fields including:

optimization result ID
workload ID
provider ID
provider name
provider type
region
algorithm
energy consumption
carbon emissions
estimated cost
execution time
carbon score

The LLM is therefore responsible for explaining the result, while the application remains responsible for producing the result.

## Decision 041 — Expose the Agent Through a Dedicated Chat API

**Date:** 2026-09-19

### Decision

The GreenCloud AI assistant will be exposed through a dedicated:

`POST /chat`

FastAPI endpoint.

### Reason

The agentic layer needs a stable application interface through which a future frontend or external client can communicate with the system.

The API also separates the presentation/client layer from the internal agent implementation.

### Request

The endpoint accepts:

- natural-language message
- optional workload UUID

### Response

The endpoint returns a natural-language answer generated by the GreenCloud agent.

### Result

The RAG and optimization capabilities can now be accessed through the application's API.

---

## Decision 042 — Separate Optimization Execution From General RAG Tool Selection

**Date:** 2026-09-19

### Decision

Optimization requests with an application-provided workload ID follow a deterministic optimization path rather than allowing the LLM to perform additional tool selection after optimization.

General knowledge questions continue to use LLM-driven RAG tool selection.

### Reason

Testing showed that allowing another unrestricted tool-selection step after optimization could cause the LLM to request an additional knowledge search instead of producing the optimization explanation.

The optimization workflow has a known deterministic sequence:

Workload
 ↓
Optimization Engine
 ↓
Result
 ↓
Explanation

There is no need for another tool-selection step between the deterministic result and its explanation.

### Result

The architecture preserves agentic behavior where it is useful while making numerical optimization execution predictable and reproducible.

## Decision 043 — Use Optional Workload Context in Chat Requests

Date: 2026-09-19

### Decision

workload_id is optional in the /chat request schema.

### Reason

Not every user request concerns a specific workload.

For example:

### What is CEGP?

requires research retrieval but does not require a workload.

Whereas:

Optimize this workload using CEGP.

requires a workload identifier.

### Result

The same /chat interface can support both:

research/knowledge questions
workload-specific optimization requests