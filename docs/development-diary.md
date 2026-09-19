## Step 2 — Application Configuration

### What I built
Created a centralized configuration layer using Pydantic Settings.

### Why
The project requires database credentials and OpenRouter API
credentials. These should not be hard-coded into individual services.

### Design decision
All environment-specific configuration is loaded through
app/core/config.py.

### Security decision
The actual .env file is excluded from Git.
.env.example is provided as a template for other developers.

### What I learned
Configuration management separates application logic from
environment-specific values and prevents secrets from being
embedded in source code.

## Step 3 — Database Layer

### What I built
Created the asynchronous PostgreSQL database layer using
SQLAlchemy AsyncSession and asyncpg.

### Architecture

FastAPI
    ↓
SQLAlchemy AsyncSession
    ↓
asyncpg
    ↓
PostgreSQL

### Why PostgreSQL
The application needs persistent relational storage for workloads,
cloud providers, carbon data and optimization results.

### Why SQLAlchemy
SQLAlchemy provides an ORM and database abstraction layer,
allowing the application models to remain independent from
raw SQL queries.

### Why asynchronous database access
FastAPI supports asynchronous request handling, and database
operations are I/O-bound. AsyncSession allows database operations
to be performed without blocking the application unnecessarily.

### Why a shared Base
All SQLAlchemy models inherit from a common DeclarativeBase.
This provides centralized metadata that can later be used by
Alembic for database migrations.

### Next step
Configure PostgreSQL and pgvector using Docker Compose.

## Step 4 — PostgreSQL + pgvector with Docker

### What I built
Configured PostgreSQL with pgvector using Docker Compose.

### Why Docker
I wanted the database environment to be reproducible without requiring
PostgreSQL to be installed directly on the host machine.

### Why PostgreSQL
The project requires relational storage for workloads, cloud providers,
carbon information and optimization results.

### Why pgvector
The project also requires vector similarity search for RAG.

Instead of introducing a separate vector database, pgvector allows
embeddings to be stored alongside the application's relational data
inside PostgreSQL.

### Architecture

FastAPI
    ↓
SQLAlchemy AsyncSession
    ↓
PostgreSQL
    ├── relational data
    └── vector data through pgvector

### Docker decision
PostgreSQL is currently exposed on port 5432 so the locally running
FastAPI application can connect to it.

When the FastAPI application is containerized, the database hostname
will change from localhost to the Docker Compose service name.

### Verification
Verified that:
- PostgreSQL container starts successfully
- greencloud database exists
- PostgreSQL accepts connections
- pgvector extension is available

## Step 5 — Workload Domain Model

### What I built
Created the Workload SQLAlchemy model and WorkloadType enum.

### Purpose
The Workload entity represents a computational job submitted to
the GreenCloud Optimizer.

### Fields
- CPU cores
- Memory
- Storage
- Runtime
- Deadline
- Data transfer
- Workload type

### Research connection
The research paper's carbon-aware scheduling approach considers
workload requirements and deadlines when allocating jobs to
cloud resources.

The CEGP policy uses job deadlines when scheduling workloads.

### Design decisions

#### UUID
Used UUID as the primary key to provide globally unique workload
identifiers suitable for distributed/cloud systems.

#### Enum
Used WorkloadType instead of arbitrary strings to restrict
workloads to known categories.

#### Runtime and deadline
Represented scheduling requirements in minutes to simplify the
prototype's scheduling simulation.

#### Data transfer
Included data transfer because cloud workload energy consumption
can involve networking in addition to compute resources.

### Next step
Create the remaining cloud infrastructure models and then
generate the initial Alembic migration.

## Step 6 — Cloud Provider Model

### What I built
Created the CloudProvider entity and CloudProviderType enum.

### Purpose
The CloudProvider entity represents cloud infrastructure that can
potentially execute a submitted workload.

### Main attributes
- Provider
- Region
- CPU capacity
- Memory
- Storage
- CPU power efficiency
- DCiE
- Cost per CPU hour
- Availability status

### Research connection
The research paper evaluates multiple IaaS cloud locations and
considers CPU characteristics, data-center efficiency and carbon
emission characteristics when scheduling workloads.

### Important design decision
Infrastructure information and carbon information are modeled
separately.

Cloud infrastructure characteristics are relatively stable,
while carbon intensity can change over time.

This separation will allow the project to support dynamic carbon
data in the future.

### Interview takeaway
The optimizer should not treat a cloud provider as a single
static object. Infrastructure characteristics and environmental
conditions are separate dimensions of the optimization problem.

### Next step
Create the CarbonData model to represent the environmental
characteristics of each cloud region.

## Step 7 — Carbon Data Model

### What I built
Created the CarbonData SQLAlchemy model.

### Purpose
CarbonData stores the environmental characteristics of a cloud
provider region.

### Main fields
- Provider ID
- Carbon intensity
- Measurement time
- Data source
- Creation timestamp

### Research connection
The research paper identifies CO2 emission rate as an important
factor in carbon-efficient cloud scheduling.

The paper's experimental setup assigns different CO2 emission
rates to different cloud locations.

### Important design decision
Carbon information is stored separately from CloudProvider.

### Why
Infrastructure characteristics and carbon intensity have different
lifecycles.

Infrastructure information can remain relatively stable while
carbon intensity can change over time.

### Relationship

CloudProvider
    |
    └── CarbonData (one-to-many)

A provider region can therefore have multiple carbon measurements
at different points in time.

### Normalization decision
CarbonData references CloudProvider using provider_id instead of
duplicating provider and region information.

### Future capability
This design allows the optimizer to eventually use time-dependent
carbon intensity when selecting where and when to execute workloads.

### Next step
Create the OptimizationResult model.

## Step 8 — Optimization Result Model

### What I built
Created the OptimizationResult database model.

### Purpose
OptimizationResult stores the outcome of an optimization run,
including the selected cloud provider, algorithm used, estimated
energy consumption, carbon emissions, cost and execution time.

### Why
The system should not only produce a decision. It should also
preserve the metrics behind that decision so that results can
be inspected, compared and displayed later.

### Research connection
The research paper evaluates carbon-aware scheduling using
metrics including energy consumption and CO2 emissions.

The paper also compares CEGP with an Earliest Start Time (EST)
baseline.

### Design decision
The algorithm used for each result is stored explicitly.

This allows the system to compare results generated by CEGP
against the baseline algorithm.

### Important separation
The database model stores calculated results.

The actual energy, carbon and optimization calculations will
remain inside dedicated services and algorithm modules.

### Next step
Configure database relationships and create the initial
Alembic migration.

## Decision 017 — Persist Optimization Results

### Decision
Store every optimization result in PostgreSQL.

### Reason
An optimization system should provide traceability for its decisions.

Persisting results allows us to:
- inspect previous decisions
- compare algorithms
- analyze energy and carbon metrics
- display historical results
- evaluate optimization performance

---

## Decision 018 — Store Algorithm Used

### Decision
Store the algorithm name with every optimization result.

### Reason
The project will implement both the CEGP approach and a baseline
approach.

Storing the algorithm makes experimental comparison possible.

### Research connection
The research paper evaluates CEGP against an Earliest Start Time
(EST) approach.

---

## Decision 019 — Separate Calculation from Persistence

### Decision
OptimizationResult stores calculated values but does not perform
the calculations itself.

### Reason
Database models should represent data rather than contain the
application's business logic.

Energy, carbon and optimization calculations will be implemented
in dedicated services and algorithm modules.

## Step 9 — Document Model and RAG Storage

### What I built
Created the Document model for the RAG knowledge base.

### Purpose
The Document model stores individual chunks of knowledge together
with their source information and embedding vector.

### RAG architecture

Source document
    ↓
Text extraction
    ↓
Chunking
    ↓
Embedding
    ↓
PostgreSQL + pgvector
    ↓
Similarity retrieval
    ↓
LLM context

### Why store chunks
RAG retrieves relevant sections rather than passing an entire
research paper to the language model.

### Why PostgreSQL + pgvector
The project already uses PostgreSQL for application data.
pgvector allows semantic vector search to be implemented within
the same database.

### Important design decision
For the prototype, a Document row represents one retrievable
knowledge chunk rather than creating separate tables for source
documents and chunks.

### Source tracking
Each chunk stores its source name and source type to maintain
knowledge provenance.

### Embedding dimension
The initial schema uses a 1536-dimensional vector.

This dimension must match the output dimension of the embedding
model selected for the OpenRouter integration.

### Next step
Create database migrations and verify all application models
against PostgreSQL.

## Step 10 — Database Relationships and Alembic Configuration

### What I built

Configured relationships between the SQLAlchemy domain models
and connected Alembic to the application's SQLAlchemy metadata.

### Relationships

CloudProvider
    |
    ├── CarbonData
    |
    └── OptimizationResult

Workload
    |
    └── OptimizationResult

### Why relationships

The relationships allow the application to navigate related
entities without repeatedly writing manual database queries.

A cloud provider can have multiple carbon measurements because
carbon intensity can change over time.

A workload can have multiple optimization results because the
system will eventually compare different optimization approaches,
such as CEGP and the baseline algorithm.

### Why Alembic

Alembic provides version-controlled database migrations.

Instead of manually creating database tables, schema changes
are represented as migration files.

This makes the database schema reproducible across development,
testing and deployment environments.

### Configuration

Alembic was configured to:

- load the database URL from the application's environment configuration
- use SQLAlchemy Base.metadata
- discover all application models
- connect to the PostgreSQL database
- support autogeneration of migrations

### Verification

Alembic successfully connected to PostgreSQL.

The autogeneration check detected the following tables:

- cloud_providers
- documents
- workloads
- carbon_data
- optimization_results

This confirmed that SQLAlchemy metadata is correctly connected
to Alembic.

### Interview takeaway

Alembic provides a controlled history of database schema changes,
while SQLAlchemy models remain the source of the application's
database structure.

## Step 12 — Deterministic Calculation Services

### What I built

Created separate services for energy and cost estimation.

### Energy Service

EnergyService estimates workload energy consumption using
workload CPU requirements, execution time, CPU power efficiency
and data-center efficiency (DCiE).

### Cost Service

CostService estimates execution cost using CPU requirements,
execution time and the provider's CPU-hour price.

### Important architecture decision

Energy and cost calculations are implemented as deterministic
Python services rather than being delegated to the LLM.

### Why

Optimization decisions require reproducible numerical results.
An LLM should not invent or approximate infrastructure metrics.

The AI layer will later consume these deterministic results and
use them for orchestration and explanation.

### Architecture

Workload + Provider
        ↓
┌───────────────────┐
│ Calculation Layer │
├───────────────────┤
│ EnergyService     │
│ CostService       │
│ CarbonService     │
└─────────┬─────────┘
          ↓
Optimization Engine

## Step 13 — Carbon Emissions Calculation

### What I built

Extended CarbonService to calculate estimated CO2 emissions
from energy consumption and carbon intensity.

### Formula

CO2 emissions (kg)
=
Energy consumption (kWh)
×
Carbon intensity (kg CO2/kWh)

### Architecture

EnergyService
      ↓
Energy consumption
      ↓
CarbonService
      +
Carbon intensity
      ↓
CO2 emissions

### Important design decision

The carbon calculation is deterministic and implemented in
Python.

The LLM is not responsible for calculating or inventing
environmental metrics.

### Why

The optimization engine requires reproducible numerical
results that can be tested and audited.

The AI layer will later consume these results for orchestration
and natural-language explanation.

## Step 14 — EST Baseline Algorithm

### What I built

Implemented an Earliest Start Time inspired baseline for
comparison with the carbon-aware CEGP implementation.

### Purpose

A baseline is required to evaluate whether carbon-aware
scheduling changes the selected execution location and the
resulting energy and carbon metrics.

### Baseline behavior

The prototype baseline:

1. removes candidates that violate the workload deadline
2. selects the feasible candidate with the shortest execution time

Carbon emissions, energy consumption and cost are recorded for
comparison but are not optimization objectives.

### Research connection

The research paper compares the CEGP scheduling approach against
an EST baseline.

### Important implementation note

The prototype uses execution time as a simplified availability
proxy for the EST comparison.

This is an engineering simplification and is not presented as an
exact reproduction of the paper's complete simulation environment.

## Step 15 — Optimization Service Integration

### What I built

Created OptimizationService as the orchestration layer connecting
the workload, cloud provider, carbon data, deterministic calculation
services and optimization algorithms.

### Workflow

1. Retrieve active cloud providers.
2. Retrieve the latest carbon intensity for each provider.
3. Calculate energy consumption.
4. Calculate carbon emissions.
5. Calculate estimated cost.
6. Build candidate metrics.
7. Execute CEGP or EST.
8. Persist the resulting optimization result.

### Architecture

Workload
    ↓
OptimizationService
    ↓
Calculation Services
    ↓
Candidate Metrics
    ↓
CEGP / EST
    ↓
OptimizationResult
    ↓
PostgreSQL

### Important design decision

OptimizationService orchestrates the workflow but does not contain
the mathematical implementation of CEGP or the individual metric
calculations.

This keeps orchestration separate from business logic and algorithms.

### AI boundary

The optimization workflow is deterministic.

OpenRouter and the AI agent will be introduced later for
natural-language interaction, tool orchestration and RAG-based
explanations rather than numerical decision-making.

## Step 16 — Exposing the Optimization Engine through FastAPI

### What I implemented

I exposed the GreenCloud optimization engine through a FastAPI endpoint:

`POST /optimization/run`

The endpoint accepts a workload UUID and an optimization algorithm (`cegp` or `est`) and returns the persisted optimization result.

### Why I implemented this

The optimization logic should not be accessible only through internal Python code. A production-style system needs a clean API layer through which other components, such as a frontend or AI agent, can interact with the optimizer.

The API therefore acts as the boundary between external requests and the internal optimization services.

### Architecture

Client / Swagger
       ↓
FastAPI
       ↓
Optimization API
       ↓
OptimizationService
       ↓
EnergyService + CarbonService + CostService
       ↓
CEGP / EST
       ↓
PostgreSQL

## Step 17 — Adding Provider-Specific Execution Characteristics

### What I implemented

I added an `execution_time_factor` attribute to the cloud provider model.

This factor represents the relative execution performance of a provider for the prototype workload.

The estimated execution time is calculated as:

execution time = workload runtime × provider execution time factor

### Why I implemented this

Initially, every cloud provider used the same workload runtime. As a result, the EST baseline could not meaningfully distinguish providers based on execution time.

Adding a provider-specific execution factor allows the EST baseline to model differences in execution performance.

### Important limitation

The execution factors used in the prototype are simulated values. They are not claimed to represent actual AWS, Azure, or GCP benchmark measurements.

In a production implementation, these values could be obtained from historical workload measurements or provider benchmarking data.

### Database migration

The new field was introduced through a separate Alembic migration rather than modifying the already-applied database migration.

This preserves a clean migration history and reflects how the database schema evolved during development.

### Design principle

Provider-specific execution characteristics are stored in the cloud provider layer because execution performance is a resource/provider characteristic rather than an optimization algorithm rule.

## Step 18 — End-to-End CEGP and EST Execution

### What I tested

I executed both optimization strategies against the same seeded workload through the `OptimizationService`.

The two algorithms were:

- CEGP — carbon/energy/cost-aware optimization
- EST — execution-time-based baseline with deadline filtering

### Observed result

For the current prototype dataset, both algorithms selected the same provider.

The workload has a runtime of 60 minutes and a deadline of 120 minutes.

The provider-specific execution factors produce:

- AWS: 66 minutes
- Azure: 54 minutes
- GCP: 60 minutes

All three providers satisfy the 120-minute deadline.

The selected provider had:

- Energy consumption: approximately 3.7647 kWh
- Carbon emissions: approximately 0.1882 kg CO₂
- Estimated cost: $2.00
- Execution time: 54 minutes

### Interpretation

The convergence of CEGP and EST is an observed result for this particular simulated dataset. It should not be interpreted as proof that one algorithm is universally better than the other.

The purpose of implementing both algorithms is to expose their different decision criteria:

CEGP considers environmental and economic metrics together, while EST primarily considers execution time subject to deadline feasibility.

### Limitation

The current provider characteristics and carbon-intensity values are simulated prototype data. A larger dataset containing real or historical measurements would be required for meaningful empirical evaluation.

## Step 19 — Research Paper Ingestion into the RAG Knowledge Base

### What I implemented

I built the document ingestion pipeline for the GreenCloud Optimizer knowledge base.

The pipeline takes a PDF research document, extracts its text, splits the text into overlapping chunks, generates embeddings, and stores the chunks and embeddings in PostgreSQL using pgvector.

### Pipeline

Research Paper PDF
        ↓
      pypdf
        ↓
   DocumentChunker
        ↓
   EmbeddingService
        ↓
1536-dimensional vectors
        ↓
 DocumentRepository
        ↓
 PostgreSQL + pgvector


### Duplicate protection

A source-existence check was added before ingestion.
If a document with the same source name has already been ingested, the pipeline skips it instead of creating duplicate chunks.

### Why embeddings are stored

Keyword search can fail when a user uses different terminology from the source document.
Vector embeddings allow the system to retrieve semantically related content even when the wording differs.

### Technology choices

pypdf — PDF text extraction
OpenRouter embedding API — embedding generation
text-embedding-3-small — 1536-dimensional embeddings
PostgreSQL — persistent document storage
pgvector — vector similarity search

### Result

The research paper can now serve as the knowledge source for the GreenCloud Optimizer's future RAG assistant.

The LLM will not be given the entire document directly. Instead, relevant chunks will be retrieved from the vector database and supplied as context when answering questions.

## Step 20 — Semantic RAG Retrieval

### What I implemented

I implemented a semantic retrieval layer that converts a user's query into an embedding and searches the PostgreSQL vector database for the most relevant document chunks.

### Retrieval pipeline

User Query
    ↓
EmbeddingService
    ↓
Query Embedding
    ↓
pgvector Cosine Similarity
    ↓
Top-K Document Chunks

### Why semantic retrieval

The user may ask a question using terminology that does not exactly match the wording in the research paper.

Vector similarity allows the system to retrieve conceptually related content rather than relying only on exact keyword matches.

### Separation of responsibilities

The retriever does not generate answers.

It is responsible only for finding relevant knowledge.

The future LLM layer will receive the retrieved chunks as context and generate a natural-language response.

### Result

The research paper can now be queried semantically through the vector database.

The number of retrieved chunks is configurable through the limit parameter.

### Benefit:
The retrieval system can be tested independently, and the LLM cannot silently replace the evidence retrieval process with unsupported knowledge.

## Step 21 — Semantic RAG Retrieval

### What was implemented

The GreenCloud Optimizer knowledge base was extended with semantic retrieval using PostgreSQL and pgvector.

The research paper *Green Cloud Framework for Improving Carbon Efficiency* was processed through the following pipeline:

PDF
→ text extraction
→ chunking
→ embedding generation
→ PostgreSQL + pgvector
→ semantic similarity search

The paper was divided into 39 chunks. Each chunk was converted into a 1536-dimensional embedding using the configured OpenRouter embedding model and stored in the `documents` table.

A `RAGRetriever` was implemented to:

1. Accept a natural-language query.
2. Generate an embedding for the query.
3. Compare the query embedding with stored document embeddings.
4. Use pgvector cosine distance to rank the chunks.
5. Return the most semantically relevant chunks.

### Verification

The query:

"How does carbon-aware scheduling reduce carbon emissions in cloud computing?"

returned five relevant chunks from the research paper.

The retrieved content included references to:

- Carbon Efficient Green Policy (CEGP)
- Carbon Aware Green Cloud Architecture
- Carbon Emission Directory
- energy and CO₂ reduction
- cloud provider selection based on carbon footprint

This confirmed that semantic retrieval was functioning correctly rather than simply performing keyword matching.

### Why this architecture was chosen

PostgreSQL with pgvector was selected instead of introducing a separate vector database because the project already uses PostgreSQL for workloads, cloud providers, carbon data, and optimization results.

This keeps the architecture simpler while allowing structured application data and vector-based knowledge retrieval to coexist in the same database.

### Important design boundary

RAG retrieval is responsible only for retrieving relevant knowledge.

It does not perform the project's deterministic energy, carbon, cost, or scheduling calculations.

Those calculations remain inside the deterministic services and optimization algorithms.

## Step 22 — RAG + LLM Grounded Generation

### What was implemented

The semantic retrieval pipeline was integrated with the OpenRouter LLM to create a complete Retrieval-Augmented Generation (RAG) workflow.

The implemented flow is:

User Query
→ Query Embedding
→ pgvector Similarity Search
→ Relevant Research Chunks
→ Context Construction
→ OpenRouter LLM
→ Grounded Natural-Language Response

A dedicated `RAGService` was introduced to orchestrate this process.

### Components

- `EmbeddingService` generates the query embedding.
- `RAGRetriever` performs semantic similarity search.
- `DocumentRepository` retrieves the most relevant document chunks.
- `RAGService` constructs the research context and coordinates generation.
- `LLMService` communicates with OpenRouter.

### Verification

The system was tested with the question:

"What is the Carbon Efficient Green Policy and how does it help reduce carbon emissions?"

The system retrieved relevant sections of the research paper and generated an answer covering:

- Carbon Efficient Green Policy (CEGP)
- Green Broker
- Carbon Emission Directory
- CO2 emission rate
- DCiE
- VM power efficiency
- Green Offers
- QoS constraints

The generated response also correctly treated the reported energy and carbon reductions as results from the paper's simulation-based evaluation rather than results produced by the GreenCloud Optimizer prototype.

### Architectural boundary

The LLM is used for knowledge-grounded explanation and natural-language interaction.

It does not perform the deterministic calculations used by the optimization engine.

Energy consumption, carbon emissions, cost, execution time, and provider selection remain responsibilities of the deterministic application services and optimization algorithms.

This separation prevents the LLM from inventing numerical optimization results.

## Step 23 — Initial GreenCloud Agent

### What was implemented

An agent orchestration layer was introduced to connect the RAG system and deterministic optimization engine.

The initial agent supports two paths:

1. Knowledge questions → RAGService
2. Optimization questions → deterministic optimization tool

The optimization tool retrieves the requested workload and delegates execution to `OptimizationService`.

### Verification

Two end-to-end tests were performed.

#### Knowledge path

A question about the Carbon Efficient Green Policy was routed through the RAG pipeline.

The resulting answer was grounded in the research paper and referenced concepts including:

- CEGP
- Green Broker
- Carbon Emission Directory
- EDF scheduling
- carbon footprint

#### Optimization path

The seeded ML Training Demo workload was passed to the optimization tool.

The deterministic CEGP engine produced:

- Energy: 3.7647 kWh
- Carbon emissions: 0.1882 kg
- Estimated cost: 2.00
- Execution time: 54 minutes
- Carbon score: 0.05

The LLM was then used only to explain the returned result.

### Architectural principle

The agent does not perform numerical optimization itself.

The LLM acts as an orchestration and explanation layer, while the deterministic optimization engine remains responsible for provider selection and numerical calculations.

### Current limitation

The first agent implementation uses keyword-based routing.

The next iteration will replace this routing mechanism with OpenRouter function/tool calling so that the model can select between the available tools based on the user's intent.

## Step 24 — Agentic Tool Calling and Deterministic Optimization Integration

### Objective

The next stage was to connect the GreenCloud Optimizer's AI agent with the deterministic optimization engine.

The goal was not to let the LLM perform optimization calculations itself. Instead, the LLM acts as an orchestration layer that can decide when the deterministic optimization tool should be invoked.

### Implementation

An agent-facing optimization tool was implemented in:

`app/agents/tools.py`

The tool:

1. Accepts a workload UUID and optimization algorithm.
2. Retrieves the workload from PostgreSQL.
3. Delegates optimization to `OptimizationService`.
4. Executes the selected deterministic algorithm such as CEGP or EST.
5. Retrieves the selected cloud provider from PostgreSQL.
6. Returns a structured JSON-friendly result to the AI agent.

The returned information includes:

- optimization result ID
- workload ID
- provider ID
- provider name
- provider type
- cloud region
- algorithm used
- energy consumption
- carbon emissions
- estimated cost
- execution time
- carbon score

### Why the provider lookup was added

Initially, the optimization tool returned only the selected provider UUID.

Although this was sufficient for application-level processing, it was not useful for a natural-language AI response because the agent would receive a value such as:

`62c29bd9-6bfe-49fa-a3ca-6df8a6225223`

Instead of expecting the LLM to infer what the UUID represents, the tool now performs a database lookup and explicitly returns:

- provider name
- provider type
- region

This keeps the source of provider information deterministic and database-backed.

### Agent Architecture

The resulting flow is:

User request

↓

GreenCloud Agent

↓

OpenRouter tool calling

↓

`optimize_workload`

↓

`OptimizationService`

↓

CEGP / EST

↓

Energy + Carbon + Cost calculations

↓

Selected Cloud Provider

↓

Structured tool result

↓

LLM-generated explanation

### Important Design Principle

The LLM does not calculate:

- energy consumption
- carbon emissions
- cloud cost
- execution time
- optimization scores

These values are generated by deterministic application services and algorithms.

The LLM is responsible for interpreting the user's request, invoking the appropriate tool, and explaining the returned result.

### Application-Authoritative Workload ID

During testing, the agent initially attempted to generate or modify the workload UUID when calling the optimization tool.

This created a potential reliability problem because a UUID is an application identifier and should not be generated by the language model.

The agent was therefore modified so that when the application provides a workload ID, that ID is treated as authoritative.

The LLM can still request the optimization tool, but the application-controlled workload ID is used for execution.

### Testing

The complete agent flow was tested using the seeded `ML Training Demo` workload.

The agent successfully:

1. Received the optimization request.
2. Invoked the `optimize_workload` tool.
3. Retrieved the workload.
4. Retrieved active cloud providers.
5. Retrieved their latest carbon data.
6. Executed the CEGP optimization algorithm.
7. Stored the optimization result in PostgreSQL.
8. Retrieved the selected provider details.
9. Returned the structured result to the LLM.
10. Generated a natural-language explanation.

The prototype selected Azure in the current simulated provider dataset, with the `sweden-central` region.

The resulting optimization metrics were approximately:

- Energy consumption: `3.7647 kWh`
- Carbon emissions: `0.1882 kg`
- Estimated cost: `2.00`
- Execution time: `54 minutes`

These values are outputs of the deterministic prototype for the current simulated dataset.

### Outcome

The GreenCloud Optimizer now has a functional agentic layer capable of connecting natural-language requests with deterministic optimization functionality.

The architecture can therefore be represented as:

User
  ↓
GreenCloud Agent
  ↓
OpenRouter
  ↓
Tool Calling
  ↓
Optimization Tool
  ↓
Optimization Service
  ↓
CEGP / EST
  ↓
PostgreSQL
  ↓
Structured Result
  ↓
LLM Explanation

## Step 25 — FastAPI AI Chat Interface

### Objective

The agentic AI layer was exposed through the FastAPI application so that the GreenCloud Optimizer could be accessed through a standard API rather than only through development scripts.

### Implementation

A chat request/response schema was created in:

`app/schemas/chat.py`

The request contains:

- `message` — natural-language user request
- `workload_id` — optional application-controlled workload UUID

The response contains:

- `answer` — natural-language response generated by the GreenCloud AI assistant

A new API router was implemented in:

`app/api/chat.py`

The endpoint is:

`POST /chat`

The endpoint creates a `GreenCloudAgent` using the current database session and forwards the user's request to the agent.

The router was registered in:

`app/main.py`

### API Flow

POST /chat
    ↓
ChatRequest
    ↓
GreenCloudAgent
    ↓
RAG or Optimization Tool
    ↓
OpenRouter
    ↓
ChatResponse

### RAG Test

The endpoint was tested with:

{
    "message": "What is CEGP?"
}

The request successfully returned HTTP 200 and produced a research-grounded explanation of CEGP using the GreenCloud knowledge base.

### Optimization Test

The endpoint was then tested with:

{
    "message": "Optimize this workload using CEGP and explain the result.",
    "workload_id": "fdba722a-d373-4019-850a-0f722207af24"
}

The request successfully returned HTTP 200.

The agent invoked the deterministic optimization engine and returned the resulting provider and optimization metrics through the LLM-generated explanation.

The current simulated workload produced:

Selected provider: Azure
Region: sweden-central
Energy consumption: approximately 3.7647 kWh
Carbon emissions: approximately 0.1882 kg
Estimated cost: 2.00
Execution time: 54 minutes
Carbon score: 0.05

### Design Correction During Testing

The initial implementation allowed the LLM to perform another tool-selection step after the optimization result had already been generated.

This caused an optimization request to incorrectly produce another knowledge-search request instead of a final optimization explanation.

The agent was therefore separated into two paths:

### Optimization path

When an application-provided workload ID is present and the request contains optimization-related intent:

User
 ↓
GreenCloud Agent
 ↓
Deterministic Optimization Tool
 ↓
CEGP
 ↓
Structured Result
 ↓
OpenRouter
 ↓
Final Explanation

### Knowledge path

For general GreenCloud questions:

User
 ↓
GreenCloud Agent
 ↓
OpenRouter Tool Selection
 ↓
RAG Retrieval
 ↓
OpenRouter
 ↓
Final Answer

This separation makes the optimization path more deterministic while retaining agentic behavior for knowledge-based queries.

### Outcome

The GreenCloud Optimizer now exposes both its research assistant and optimization agent through a working FastAPI endpoint.

The project has therefore progressed from individual backend components to an integrated AI-enabled backend.

## Step 26 — Dockerized Application and Database Integration

### Objective

The GreenCloud Optimizer backend was containerized so that the FastAPI application and PostgreSQL database can run together using Docker Compose.

### Implementation

A `Dockerfile` was created for the FastAPI application.

The Docker image:

- Uses Python 3.11
- Installs project dependencies
- Copies the application source
- Includes Alembic migrations
- Includes project scripts and data
- Starts the FastAPI application using Uvicorn

Docker Compose was configured with two services:

FastAPI API
     ↓
PostgreSQL + pgvector

The PostgreSQL service uses the pgvector/pgvector:pg16 image.

### Database Networking

The local development environment uses:

localhost:5433

for PostgreSQL access from the host machine.

Inside Docker Compose, the API connects to PostgreSQL using:

postgres:5432

where postgres is the Docker Compose service name.

### Automatic Migrations

The API container was configured to run:

alembic upgrade head

before starting Uvicorn.

This ensures that the database schema is updated automatically when the application container starts.

### Outcome

The GreenCloud API and PostgreSQL database successfully run together through Docker Compose.


## Step 27 — GitHub Actions Continuous Integration

### Objective

A GitHub Actions CI pipeline was added to automatically validate the GreenCloud Optimizer whenever changes are pushed to the main branch or a pull request is created.

### CI Pipeline

The workflow performs the following steps:

Checkout repository
        ↓
Set up Python 3.11
        ↓
Install dependencies
        ↓
Start PostgreSQL + pgvector
        ↓
Configure test environment
        ↓
Enable pgvector extension
        ↓
Run Alembic migrations
        ↓
Run pytest

### Pytest Configuration

A pytest.ini file was added to ensure that:

automated tests are collected only from tests/
the project root is available for Python imports
asynchronous tests are handled automatically using pytest-asyncio

The configuration is:

[pytest]
testpaths = tests
pythonpath = .
asyncio_mode = auto
CI Database Configuration

The GitHub Actions workflow creates a fresh PostgreSQL database for each CI run.

Because the application uses pgvector for semantic retrieval, the workflow explicitly enables the PostgreSQL vector extension before running Alembic migrations:

CREATE EXTENSION IF NOT EXISTS vector;

This ensures that the VECTOR(1536) column used by the RAG document store can be created during migration.

### Testing

The local automated test suite successfully passed:

9 passed

The same test suite was then executed in the GitHub Actions environment using PostgreSQL and pgvector.

The GitHub Actions workflow completed successfully with all checks green.

### Outcome

The project now has a reproducible continuous integration pipeline that validates:

Python dependencies
PostgreSQL connectivity
pgvector availability
Alembic migrations
deterministic optimization algorithms
energy calculations
carbon calculations
cost calculations
baseline scheduling

This provides automated verification of the backend whenever code is pushed to GitHub.