# GreenCloud Optimizer — Research Notes

## 1. Research Basis

GreenCloud Optimizer is inspired by research on green cloud computing and carbon-aware cloud resource scheduling.

The research basis focuses on improving cloud resource allocation by considering environmental characteristics of cloud resources in addition to traditional scheduling objectives.

The project uses these concepts as the foundation for a practical software implementation.

The goal is not to claim an exact reproduction of the complete research system. Instead, the project implements selected concepts from the research framework and extends them with a modern software and AI architecture.

---

# 2. Core Research Concepts

The main concepts relevant to the implementation are:

- Green Broker
- Green Offer Directory
- Carbon Emission Directory
- Carbon-aware resource selection
- Carbon-efficient scheduling
- CEGP scheduling
- Energy efficiency
- CPU power efficiency
- Data-center infrastructure efficiency
- Carbon intensity
- Deadline-aware scheduling
- Execution-time-based scheduling

These concepts form the basis of the deterministic optimization layer.

---

# 3. Green Broker Concept

The Green Broker acts as an intermediary between workload requirements and available cloud resources.

Conceptually:

```text
Workload Requirements
        │
        ▼
   Green Broker
        │
        ▼
Available Cloud Offers
        │
        ▼
Environmental /
Performance Evaluation
        │
        ▼
Selected Resource
```

The broker considers characteristics of available resources before selecting a suitable resource for a workload.

In GreenCloud Optimizer, the OptimizationService plays a similar application-level role.

It:

Receives a workload.
Retrieves available providers.
Retrieves carbon information.
Calculates energy consumption.
Calculates carbon emissions.
Calculates estimated cost.
Estimates execution time.
Passes candidate metrics to the optimization algorithm.
Selects a feasible provider.
Stores the resulting optimization decision.

# 4. Green Offer Directory

The research framework includes the concept of maintaining information about available green cloud offers.

A cloud offer can contain information about resource characteristics and environmental efficiency.

GreenCloud Optimizer represents this concept through the CloudProvider model.

Current provider information includes:

CloudProvider
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

This provides the optimization engine with a structured representation of available cloud resources.

# 5. Carbon Emission Directory

Carbon information is represented separately from provider metadata.

CloudProvider
      │
      │
      ▼
CarbonData

Each carbon record contains:

CarbonData
├── Provider ID
├── Carbon intensity
├── Measurement time
├── Source
└── Created timestamp

The separation is intentional.

Provider characteristics such as CPU efficiency and cost describe the resource, while carbon intensity represents an environmental measurement associated with that resource or region.

The current implementation retrieves the latest available carbon measurement for a provider.

# 6. Carbon Intensity

Carbon intensity represents the amount of carbon emissions associated with electricity consumption.

GreenCloud Optimizer uses carbon intensity when estimating the environmental impact of a workload.

The implementation uses:

carbon emissions = energy consumption × carbon intensity

This creates a direct relationship between workload energy requirements and estimated emissions.

The current prototype uses seeded carbon-intensity values.

It does not yet consume a live electricity-grid carbon API.

# 7. Energy Consumption Model

The project estimates workload energy consumption using CPU requirements, runtime, CPU power efficiency, and DCiE.

The current implementation follows:

runtime_hours = runtime_minutes / 60

cpu_energy = cpu_cores × runtime_hours × cpu_power_efficiency

total_energy = cpu_energy / DCiE

This provides a deterministic estimate that can be used by the optimization layer.

# 8. CPU Power Efficiency

CPU power efficiency is represented as a provider-level parameter.

It is used to estimate the amount of energy associated with CPU execution.

The current prototype therefore allows two providers running the same workload to produce different energy estimates.

For example:

Same workload
      │
      ├── Provider A
      │      └── CPU efficiency A
      │
      └── Provider B
             └── CPU efficiency B

This enables resource efficiency to become part of provider selection.

# 9. DCiE

Data Center Infrastructure Efficiency (DCiE) is represented as a provider-level parameter.

The current model uses DCiE when converting estimated CPU energy into total facility energy.

Total energy = CPU energy / DCiE

This allows the prototype to account for infrastructure overhead rather than considering CPU energy alone.

# 10. Deadline-Aware Scheduling

A workload contains a deadline:

deadline_minutes

Before optimization, candidate providers that cannot satisfy the deadline are removed.

Conceptually:

All Providers
      │
      ▼
Deadline Constraint
      │
      ├── Violates deadline → Reject
      │
      └── Meets deadline → Candidate

This prevents an environmentally efficient provider from being selected if it cannot satisfy the workload's execution requirement.

# 11. CEGP-Inspired Optimization

The project implements a deterministic CEGP-inspired scheduling algorithm.

The algorithm evaluates feasible candidates using:

Carbon emissions
Energy consumption
Estimated cost

Execution time is used for deadline feasibility.

The current prototype normalizes the candidate metrics and combines them using configurable weights.

Current prototype weights:

Carbon = 0.6
Energy = 0.3
Cost   = 0.1

The candidate with the lowest resulting score is selected.

These weights are an implementation choice for the prototype.

They should not be described as the exact weighting formula of the research paper.

# 12. EST Baseline

The project includes an execution-time-oriented baseline called EST.

The baseline first removes candidates that violate the deadline.

It then selects the feasible provider with the lowest estimated execution time.

Providers
    │
    ▼
Deadline Filtering
    │
    ▼
Feasible Providers
    │
    ▼
Minimum Execution Time
    │
    ▼
Selected Provider

Energy, carbon, and cost are still calculated for the selected candidate.

The baseline exists to provide a comparison point for the carbon-aware optimization approach.

# 13. Research Concept → Implementation Mapping
Research concept	GreenCloud Optimizer implementation
Green Broker	OptimizationService
Green Offer Directory	CloudProvider model
Carbon Emission Directory	CarbonData model
Carbon intensity	CarbonService
Energy estimation	EnergyService
CPU efficiency	cpu_power_efficiency
Data-center efficiency	dcie
Deadline-aware scheduling	Deadline filtering
CEGP scheduling	CEGPAlgorithm
Execution-time scheduling	ESTBaseline
Resource selection	OptimizationService
Optimization result	OptimizationResult

This mapping represents the relationship between the research concepts and the implemented prototype.

# 14. What Was Implemented From the Research

The following research-inspired concepts were directly incorporated into the deterministic backend:

Resource-aware provider selection

The system evaluates multiple cloud providers instead of treating all cloud resources as equivalent.

Carbon-aware selection

Carbon emissions are explicitly calculated and incorporated into the CEGP-inspired score.

Energy-aware selection

Energy consumption is calculated for each candidate provider.

Deadline constraints

Providers that cannot satisfy the workload deadline are excluded.

Execution-time baseline

An EST baseline provides a separate scheduling strategy for comparison.

Provider environmental characteristics

CPU efficiency, DCiE, and carbon intensity are represented as data rather than hard-coded into the optimization algorithm.

# 15. What Was Extended Beyond the Research Concepts

The project adds a software platform and AI layer around the research-inspired optimization logic.

Major extensions include:

REST API

FastAPI exposes optimization functionality through HTTP endpoints.

PostgreSQL

Provider, workload, carbon, and optimization information is persisted in PostgreSQL.

pgvector

The project uses PostgreSQL's pgvector extension to store and search document embeddings.

Embeddings

Research documents are converted into vector representations for semantic retrieval.

RAG

The research knowledge base can be queried through Retrieval-Augmented Generation.

Agentic AI

The GreenCloud Agent can access backend capabilities through tools.

OpenRouter

The language-model layer uses OpenRouter through an OpenAI-compatible API.

Docker

The API and PostgreSQL database can be run as containers using Docker Compose.

CI

GitHub Actions automatically installs dependencies, prepares PostgreSQL with pgvector, applies migrations, and runs tests.

# 16. Why RAG Was Added

The optimization engine contains deterministic rules and calculations, but users may also want to ask conceptual questions about green cloud computing.

For example:

What is CEGP?
How does carbon-aware scheduling work?
What is a Green Broker?
Why does DCiE matter?

These questions are different from numerical optimization requests.

RAG allows the system to retrieve relevant sections from the research knowledge base before generating an answer.

Therefore:

Optimization
    → Deterministic calculation

Research questions
    → RAG + LLM

This separation prevents the LLM from becoming the source of numerical optimization decisions.

# 17. Why Agentic AI Was Added

A normal chatbot could simply generate answers from retrieved documents.

However, GreenCloud Optimizer also contains executable backend capabilities.

The agent therefore provides a way for natural-language requests to access these capabilities.

For example:

User:
"Optimize this workload using CEGP."

        │
        ▼

GreenCloud Agent

        │
        ▼

Optimization Tool

        │
        ▼

OptimizationService

        │
        ▼

CEGP Algorithm

        │
        ▼

Structured Result

        │
        ▼

LLM Explanation

The agent does not independently calculate the result.

It invokes the deterministic backend and uses the returned result as the authoritative source.

# 18. AI Safety Boundary in the Architecture

A major design decision is the separation between AI-generated text and deterministic numerical results.

The LLM is not responsible for:

Calculating energy consumption
Calculating carbon emissions
Calculating cost
Filtering deadline violations
Selecting the optimization candidate
Inventing provider metrics

The backend is responsible for those operations.

The LLM is responsible for:

Natural-language interaction
Research retrieval
Tool orchestration
Explaining backend results

This creates a clear boundary between probabilistic AI behavior and deterministic engineering logic.

# 19. Current Prototype Dataset

The current prototype contains simulated provider data.

Example providers include:

AWS
Region: us-west-2

Azure
Region: sweden-central

GCP
Region: us-central1

The values for:

CPU efficiency
DCiE
Cost
Carbon intensity
Execution time factor

are seeded prototype values.

They are intended to demonstrate the optimization pipeline rather than represent live commercial cloud-provider measurements.

# 20. Observed Prototype Behavior

For the current seeded workload and provider dataset, the CEGP-inspired algorithm selects Azure in the sweden-central region.

The selected result is based on the deterministic metrics currently stored in the prototype database.

The current dataset also produces the same selected provider for the EST baseline.

This should be described as an observation from the current simulated dataset, not as proof that CEGP is universally superior to EST.

A meaningful evaluation would require a larger workload/provider dataset and repeated experiments.

# 21. Evaluation Strategy

Future evaluation should compare scheduling strategies across multiple workloads.

Potential metrics include:

Carbon emissions
Energy consumption
Execution time
Cost
Deadline violations

A possible evaluation process is:

Generate / collect workloads
          │
          ▼
Evaluate with EST
          │
          ▼
Evaluate with CEGP
          │
          ▼
Compare metrics
          │
          ▼
Analyze trade-offs

The purpose of the comparison is to understand the trade-offs between environmental efficiency, execution time, and cost.

# 22. Limitations

The current prototype has several limitations.

Simulated carbon data

Carbon intensity is currently seeded rather than obtained from a live carbon-intensity service.

Simulated provider metrics

Provider efficiency, cost, and execution factors are prototype values.

Simplified energy model

The current energy model primarily uses CPU requirements, runtime, CPU efficiency, and DCiE.

It does not model every hardware or workload-level energy component.

Simplified execution model

Execution time is represented using a provider-specific execution-time factor rather than measured execution on actual cloud infrastructure.

Limited optimization objectives

The current CEGP-inspired score considers carbon, energy, and cost while using execution time primarily as a deadline constraint.

Prototype scale

The current dataset is small and does not represent large-scale cloud scheduling.

# 23. Future Research Extensions

Possible future extensions include:

Live carbon-aware scheduling

Integrate real-time carbon-intensity APIs.

Real cloud pricing

Retrieve current pricing information from cloud provider APIs.

Larger workload datasets

Evaluate the algorithms using diverse workload profiles.

Multi-objective optimization

Introduce configurable optimization objectives such as:

Carbon budget
Cost budget
SLA requirements
Execution time
Renewable-energy availability
Historical analytics

Store historical optimization decisions and analyze trends.

Adaptive scheduling

Allow workload scheduling decisions to change as carbon intensity changes over time.

Real cloud execution

Connect the optimization engine to actual cloud resources.

Experimental evaluation

Compare CEGP-inspired scheduling against additional scheduling strategies across repeated workloads.

# 24. Key Research-to-Engineering Insight

The main engineering idea behind GreenCloud Optimizer is:

Research concepts
       │
       ▼
Deterministic optimization engine
       │
       ▼
Backend API
       │
       ├──────────────► PostgreSQL
       │
       └──────────────► AI Agent
                              │
                              ▼
                         RAG + LLM

The research concepts provide the optimization foundation.

The software architecture turns those concepts into reusable backend services.

The AI layer provides a natural-language interface without replacing the deterministic optimization engine.

This separation allows the system to combine research-backed scheduling with modern AI engineering practices.

# 25. Summary

GreenCloud Optimizer can therefore be viewed as three interconnected layers:

┌──────────────────────────────────────────┐
│              AI INTERFACE                │
│                                          │
│        Agent + RAG + OpenRouter          │
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│           OPTIMIZATION ENGINE            │
│                                          │
│     CEGP + EST + Energy + Carbon + Cost  │
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│              DATA LAYER                  │
│                                          │
│      PostgreSQL + pgvector + Alembic     │
└──────────────────────────────────────────┘

The resulting system combines research-inspired carbon-aware scheduling with a production-oriented backend architecture and an AI-assisted interface.