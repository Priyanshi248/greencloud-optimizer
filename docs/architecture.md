# GreenCloud Optimizer — System Architecture

## 1. Overview

GreenCloud Optimizer is a cloud-workload optimization platform that combines deterministic carbon-aware optimization with Retrieval-Augmented Generation (RAG) and agentic AI.

The system is designed to select a suitable cloud provider and region for a workload while considering:

- Energy consumption
- Carbon emissions
- Estimated execution cost
- Execution time
- Workload deadline
- Cloud provider efficiency
- Carbon intensity

The AI layer provides natural-language interaction and access to the research knowledge base, while all numerical optimization and environmental calculations remain deterministic.

---

## 2. Architectural Principles

The architecture follows several important principles.

### 2.1 Deterministic optimization

Carbon, energy, cost, execution time, and provider selection are calculated by backend services and optimization algorithms.

The LLM does not perform these calculations.

This prevents the language model from inventing or modifying numerical optimization results.

### 2.2 AI-assisted interaction

The AI layer is responsible for:

- Understanding natural-language requests
- Retrieving relevant research information
- Calling backend optimization tools
- Explaining deterministic optimization results
- Answering questions using the project's knowledge base

### 2.3 Database-backed knowledge

PostgreSQL stores both application data and RAG document embeddings.

The `pgvector` extension enables semantic similarity search directly inside PostgreSQL.

### 2.4 Research-backed implementation

The optimization concepts are inspired by the Green Broker / CEGP research framework.

The project extends those concepts with:

- REST APIs
- PostgreSQL persistence
- pgvector-based RAG
- Embeddings
- OpenRouter-based LLM interaction
- Agentic tool calling
- Docker
- CI/CD
- Natural-language optimization interaction

---

# 3. High-Level Architecture

```text
                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │      REST API       │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
                    ▼                                ▼
          ┌───────────────────┐            ┌───────────────────┐
          │ Optimization      │            │ AI / Agent Layer  │
          │ Service           │            │                   │
          └─────────┬─────────┘            └─────────┬─────────┘
                    │                                │
          ┌─────────┼──────────┐           ┌─────────┴─────────┐
          │         │          │           │                   │
          ▼         ▼          ▼           ▼                   ▼
       Energy    Carbon      Cost        RAG              OpenRouter
       Service   Service    Service      Layer               LLM
          │         │          │           │                   │
          └─────────┴──────────┘           │                   │
                    │                      │                   │
                    ▼                      ▼                   │
             ┌──────────────┐      ┌──────────────┐           │
             │ CEGP / EST   │      │  Embeddings  │           │
             │ Optimization │      │ + pgvector   │           │
             └──────┬───────┘      └──────┬───────┘           │
                    │                      │                   │
                    └──────────┬───────────┴───────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │     PostgreSQL       │
                    │      + pgvector      │
                    └──────────────────────┘
```

# 4. Application Layers
The backend is organized into separate layers.

```text
app/
├── api/
├── agents/
├── algorithms/
├── embeddings/
├── models/
├── repositories/
├── rag/
├── schemas/
└── services/
```
### 4.1 API Layer
The API layer exposes the application's functionality through FastAPI.

Current endpoints include:
```text
GET  /
GET  /health

POST /optimization/run
POST /chat
```
The API layer handles:

Request validation
Dependency injection
Database session management
Calling application services
Returning structured responses

Business logic is kept outside the API routes.

# 5. Optimization Architecture
The optimization pipeline is deterministic.

```text
Workload
   │
   ▼
OptimizationService
   │
   ├──────────────► EnergyService
   │
   ├──────────────► CarbonService
   │
   ├──────────────► CostService
   │
   └──────────────► Execution Time
                         │
                         ▼
                ┌─────────────────┐
                │ CEGP Algorithm  │
                │       or        │
                │  EST Baseline   │
                └────────┬────────┘
                         │
                         ▼
                Selected Provider
                         │
                         ▼
                OptimizationResult
```

### 5.1 Energy Service

The energy service estimates workload energy consumption using:

CPU cores
Runtime
CPU power efficiency
Data-center infrastructure efficiency (DCiE)

The current prototype uses:
```text
runtime_hours = runtime_minutes / 60

cpu_energy =
    cpu_cores × runtime_hours × cpu_power_efficiency

total_energy =
    cpu_energy / DCiE
```

### 5.2 Carbon Service

Carbon emissions are calculated from estimated energy consumption and the provider's carbon intensity.

carbon_emissions = energy_consumption × carbon_intensity

Carbon intensity is retrieved from the database.

The service uses the latest available carbon measurement for the provider.

### 5.3 Cost Service

The current prototype estimates workload cost using:

estimated_cost = cpu_cores × runtime_hours × cost_per_cpu_hour

This provides a deterministic cost metric that can participate in optimization.

# 6. CEGP Optimization

The project implements a deterministic CEGP-inspired optimization algorithm.

Each provider is represented by candidate metrics:
```text
Provider
├── Energy consumption
├── Carbon emissions
├── Estimated cost
└── Execution time
```

Providers that cannot satisfy the workload deadline are removed before optimization.

The remaining metrics are normalized and combined using configurable weights.

The current prototype uses:

Carbon weight = 0.6
Energy weight = 0.3
Cost weight   = 0.1

The candidate with the lowest resulting score is selected.

These weights are a prototype implementation choice and should not be interpreted as an exact reproduction of the mathematical formulation of the research paper.

# 7. EST Baseline

The project also implements an execution-time-oriented baseline.

The EST baseline:

Removes providers that violate the workload deadline.
Compares feasible providers by estimated execution time.
Selects the provider with the shortest execution time.

Energy, carbon, and cost are still calculated and reported, but they are not the optimization objective of the baseline.

This provides a reference point for comparing the carbon-aware CEGP-inspired approach with a scheduling strategy focused primarily on execution time.

# 8. Cloud Provider Model

Cloud providers are stored in PostgreSQL.

The provider model contains information such as:
```text
Provider
├── Provider type
├── Provider name
├── Region
├── CPU capacity
├── Memory capacity
├── Storage capacity
├── CPU power efficiency
├── DCiE
├── Cost per CPU hour
├── Execution time factor
└── Active status
```

The execution-time factor allows the prototype to represent different execution characteristics between cloud providers.

# 9. Carbon Data

Carbon measurements are stored separately from provider information.
```text
CloudProvider
      │
      │ 1:N
      ▼
CarbonData
```
A carbon record contains:

```text
CarbonData
├── Provider ID
├── Carbon intensity
├── Measurement time
├── Source
└── Created timestamp
```

This allows carbon intensity to change independently from provider metadata.

The current prototype uses seeded simulation data rather than a live electricity-grid carbon API.

# 10. RAG Architecture

The project includes a Retrieval-Augmented Generation pipeline.
```text
Research PDF
     │
     ▼
PDF Extraction
     │
     ▼
Document Chunking
     │
     ▼
Embedding Generation
     │
     ▼
PostgreSQL + pgvector
```

at query time:

```text
User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
pgvector Similarity Search
      │
      ▼
Relevant Document Chunks
      │
      ▼
Context
      │
      ▼
OpenRouter LLM
      │
      ▼
Grounded Answer
```

# 11. Embedding Architecture

The embedding service uses an OpenAI-compatible client configured to communicate with OpenRouter.

The embedding model is configured through:

EMBEDDING_MODEL

The generated vectors are stored in PostgreSQL using the pgvector extension.

The current vector dimension is:

1536

The database performs cosine-distance similarity search to retrieve relevant research chunks.

# 12. RAG Knowledge Base

The current knowledge base contains the research document used as the basis for the GreenCloud Optimizer implementation.

The ingestion pipeline:

Reads the PDF.
Extracts its text.
Splits the text into overlapping chunks.
Generates an embedding for every chunk.
Stores the chunks and embeddings in PostgreSQL.

Duplicate source ingestion is prevented by checking the source name before inserting the document again.

# 13. AI / Agent Architecture

The AI layer contains three major components:
```text
GreenCloudAgent
      │
      ├── RAG Tool
      │
      ├── Optimization Tool
      │
      └── OpenRouter LLM
```
The agent can use backend capabilities instead of performing calculations itself.

# 14. Optimization Tool

The optimization tool provides the AI agent with access to the deterministic optimization engine.

The flow is:
```text
User Request
     │
     ▼
GreenCloudAgent
     │
     ▼
Optimization Tool
     │
     ▼
OptimizationService
     │
     ▼
CEGP / EST
     │
     ▼
Structured Optimization Result
     │
     ▼
LLM Explanation
```

The tool returns structured information such as:

Provider
Region
Algorithm
Energy consumption
Carbon emissions
Estimated cost
Execution time
Carbon score

The LLM explains these values but does not modify or recalculate them.

# 15. RAG Tool

The RAG tool gives the agent access to the project's research knowledge base.
```text
User Question
      │
      ▼
GreenCloudAgent
      │
      ▼
RAG Tool
      │
      ▼
Semantic Retrieval
      │
      ▼
Relevant Research Chunks
      │
      ▼
OpenRouter LLM
      │
      ▼
Answer
```

This allows questions about concepts such as:

Green Broker
Carbon Emission Directory
Green Offer Directory
CEGP
Carbon-aware scheduling
Energy efficiency
Cloud carbon emissions

to be answered using retrieved research context.

# 16. Separation of AI and Deterministic Logic

A key design decision is to keep numerical computation outside the language model.
```text
                AI Layer
                   │
        ┌──────────┴──────────┐
        │                     │
     RAG Tool          Optimization Tool
        │                     │
        ▼                     ▼
   Research Data       Deterministic Engine
                              │
                     ┌────────┼────────┐
                     ▼        ▼        ▼
                   Energy   Carbon    Cost
                              │
                              ▼
                         CEGP / EST
```
The LLM is therefore used for:

Natural-language understanding
Tool selection
Retrieval
Explanation

The backend is responsible for:

Numerical calculations
Optimization
Deadline filtering
Provider selection
Persistence

This separation makes the system more predictable and testable.

# 17. Database Architecture

PostgreSQL is the primary application database.

Current major tables are:

workloads
cloud_providers
carbon_data
optimization_results
documents

Relationships include:
```text
Workload
   │
   └──────────────► OptimizationResult ◄──────── CloudProvider
                                                    │
                                                    ▼
                                               CarbonData
```

The documents table is used by the RAG subsystem.

Its embedding column uses:

pgvector.Vector(1536)
# 18. Repository Layer

Repositories provide database access for application entities.

The repository layer is intended to keep SQL/database operations separate from business logic.

Examples include:

DocumentRepository
WorkloadRepository
ProviderRepository
CarbonRepository

The RAG retrieval pipeline currently uses DocumentRepository for vector similarity search.

# 19. Docker Architecture

The application can run using Docker Compose.
```text
┌──────────────────────────────────────────┐
│              Docker Compose              │
│                                          │
│  ┌────────────────┐   ┌───────────────┐  │
│  │   FastAPI      │   │  PostgreSQL   │  │
│  │     API        │──►│   + pgvector  │  │
│  │                │   │               │  │
│  └────────────────┘   └───────────────┘  │
│                                          │
└──────────────────────────────────────────┘
```

The PostgreSQL container provides:

Application database
Vector storage
pgvector similarity search

The API container provides:

FastAPI
Application services
Optimization engine
RAG pipeline
AI agent

Database migrations are executed using Alembic when the API container starts.

# 20. CI/CD Architecture

GitHub Actions is used for continuous integration.

The CI pipeline performs:
```text
Git Push
   │
   ▼
GitHub Actions
   │
   ├── Setup Python
   │
   ├── Install dependencies
   │
   ├── Start PostgreSQL + pgvector
   │
   ├── Enable pgvector
   │
   ├── Run Alembic migrations
   │
   └── Run pytest
```

The pipeline verifies both the database schema and automated tests.

This helps detect:

Migration failures
Dependency problems
Database integration issues
Algorithm regressions
Service-level regressions

# 21. Request Flow: Optimization

A typical optimization request follows this path:
```text
POST /optimization/run
        │
        ▼
Optimization API
        │
        ▼
Load Workload
        │
        ▼
OptimizationService
        │
        ├── Load active providers
        │
        ├── Retrieve carbon intensity
        │
        ├── Calculate energy
        │
        ├── Calculate carbon
        │
        ├── Calculate cost
        │
        ├── Estimate execution time
        │
        ▼
    CEGP / EST
        │
        ▼
Selected Provider
        │
        ▼
OptimizationResult
        │
        ▼
PostgreSQL
        │
        ▼
FastAPI Response
```
# 22. Request Flow: AI Chat

A natural-language request follows:
```text
POST /chat
     │
     ▼
GreenCloudAgent
     │
     ├───────────────┐
     │               │
     ▼               ▼
Optimization       RAG
   Tool            Tool
     │               │
     ▼               ▼
Deterministic     pgvector
Engine            Retrieval
     │               │
     └───────┬───────┘
             ▼
       OpenRouter LLM
             │
             ▼
      Natural-language
           response
```
When an optimization request is made for a specific workload, the backend optimization result is treated as authoritative.

The LLM is used to explain the result rather than generate the result.

23. Research Concepts vs Project Extensions

The implementation distinguishes between concepts derived from the research basis and functionality added for the software platform.

Research-inspired concepts
Green Broker architecture
Green Offer Directory
Carbon Emission Directory
Carbon-aware scheduling
CEGP scheduling
Energy efficiency
Carbon intensity
DCiE
CPU power efficiency
Deadline-aware scheduling
EST baseline
Project extensions
FastAPI REST API
PostgreSQL persistence
pgvector semantic retrieval
Embedding pipeline
RAG question answering
Agentic AI
OpenRouter integration
Tool calling
Dockerized deployment
GitHub Actions CI
Automated tests
Natural-language optimization interface
Structured optimization results

The extensions provide a software implementation around the research concepts rather than claiming to reproduce the entire research system.

# 24. Technology Stack
```text
Layer	                                Technology
Backend	                                FastAPI
Language	                            Python
Database	                            PostgreSQL
Vector Database	                        PostgreSQL + pgvector
ORM	                                    SQLAlchemy
Migrations	                            Alembic
AI API	                                OpenRouter
LLM	                                    Configurable through LLM_MODEL
Embeddings	                            Configurable through EMBEDDING_MODEL
RAG	                                    Custom retrieval pipeline
PDF Processing	                        pypdf
Containerization	                    Docker
Orchestration	                        Docker Compose
CI	                                    GitHub Actions
Testing	                                pytest
```

# 25. Current Design Boundary

The current prototype focuses on the backend optimization and AI architecture.

It does not yet claim to provide:

Live electricity-grid carbon intensity
Real-time cloud pricing
Real cloud deployment/migration of workloads
Production-grade cloud provider APIs
Production-scale scheduling
Guaranteed reproduction of research-paper numerical results

These can be added as future extensions.

# 26. Future Architecture Extensions

Potential future additions include:
```text
Live Carbon APIs
       │
       ▼
Real-time Carbon Service

Cloud Provider APIs
       │
       ▼
Real Resource / Price Data

Monitoring
       │
       ▼
Historical Energy & Carbon Analytics

Advanced Agent
       │
       ▼
Multi-step Optimization Workflows
```
Additional optimization objectives could also be introduced, such as:

Cost constraints
Carbon budgets
SLA constraints
Resource availability
Renewable-energy availability

These extensions should preserve the separation between deterministic calculations and AI-generated explanations.