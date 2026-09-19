# GreenCloud Optimizer

GreenCloud Optimizer is an AI-assisted, carbon-aware cloud workload optimization platform that helps select suitable cloud providers based on carbon emissions, energy consumption, cost, execution time, and workload deadlines.

The project combines green cloud computing, deterministic optimization, RAG, and agentic AI.

---

## Live Demo

| Service              | Link                                           |
| -------------------- | ---------------------------------------------- |
| **Live Application** | https://greencloud-optimizer.vercel.app/       |
| **Backend API**      | https://greencloud-optimizer.onrender.com      |
| **Swagger API Docs** | https://greencloud-optimizer.onrender.com/docs |

---

## Table of Contents

* [About](#about)
* [Problem Statement](#problem-statement)
* [Features](#features)
* [System Architecture](#system-architecture)
* [Tech Stack](#tech-stack)
* [Project Structure](#project-structure)
* [Optimization Approach](#optimization-approach)
* [RAG and AI](#rag-and-ai)
* [Getting Started](#getting-started)
* [API Documentation](#api-documentation)
* [Current Status](#current-status)
* [Future Scope](#future-scope)

---

## About

GreenCloud Optimizer is a cloud workload optimization platform designed around the principles of **green cloud computing and carbon-aware scheduling**.

The platform evaluates available cloud providers using multiple factors such as:

* Carbon emissions
* Energy consumption
* Estimated cost
* Execution time
* Workload deadlines
* CPU power efficiency
* Data-center efficiency
* Carbon intensity

The project combines a **deterministic optimization engine** with **RAG and agentic AI**, allowing users to both optimize workloads and ask research-based questions about green cloud computing.

---

## Problem Statement

Cloud workloads can have different environmental and operational impacts depending on the provider, region, infrastructure efficiency, and execution conditions.

Traditional workload scheduling generally focuses on factors such as cost or execution time.

GreenCloud Optimizer explores a different approach:

> **Can cloud workloads be placed using both operational requirements and environmental considerations?**

The system therefore evaluates cloud providers using carbon, energy, cost, execution time, and deadline constraints.

---

## Features

### Carbon-Aware Optimization

Evaluates cloud providers based on estimated carbon emissions and energy consumption.

### CEGP-Inspired Scheduling

Implements a deterministic, CEGP-inspired optimization strategy using normalized:

* Carbon emissions
* Energy consumption
* Cost

### EST Baseline

Provides an execution-time-oriented baseline for comparing provider selection strategies.

### Deadline-Aware Scheduling

Providers that cannot satisfy the workload deadline are excluded before optimization.

### RAG-Based Research Assistant

Research documents are processed into embeddings and stored in PostgreSQL using pgvector, enabling semantic retrieval of relevant research context.

### Agentic AI

The GreenCloud Agent can use backend tools for:

* Research retrieval
* Workload optimization

### Deterministic Optimization + AI

The AI layer does not perform the numerical optimization itself.

The backend calculates the optimization result, while the AI layer retrieves context, orchestrates tools, and explains the result.

### Containerized Architecture

The application and PostgreSQL database can be run using Docker Compose.

### Automated Testing and CI

The project uses pytest for testing and GitHub Actions for automated CI checks.

---

## System Architecture

```text
                           User
                             |
                             v
                     +---------------+
                     |    FastAPI    |
                     |    REST API   |
                     +-------+-------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
     +-------------------+          +-------------------+
     | Optimization      |          | AI / Agent Layer  |
     | Service           |          |                   |
     +---------+---------+          +---------+---------+
               |                              |
       +-------+-------+              +-------+-------+
       |       |       |              |               |
       v       v       v              v               v
     Energy  Carbon   Cost           RAG         OpenRouter
     Service Service Service         Layer           LLM
       |       |       |              |
       +-------+-------+              |
               |                      |
               v                      v
        +-------------+        +-------------+
        | CEGP / EST  |        |  pgvector   |
        | Optimization|        | Embeddings  |
        +------+------+        +------+------+
               |                      |
               +----------+-----------+
                          |
                          v
                 +-------------------+
                 |    PostgreSQL     |
                 |    + pgvector     |
                 +-------------------+
```

The architecture separates the **deterministic optimization engine** from the **probabilistic AI layer**.

---

## Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic

### Database

* PostgreSQL
* pgvector

### AI / ML

* RAG
* OpenRouter
* OpenAI-compatible Embeddings API
* Agentic AI

### DevOps

* Docker
* Docker Compose
* GitHub Actions

### Testing

* pytest

---

## Project Structure

```text
greencloud-optimizer/
│
├── app/
│   ├── agents/
│   ├── algorithms/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── embeddings/
│   ├── enums/
│   ├── models/
│   ├── rag/
│   ├── repositories/
│   ├── schemas/
│   └── services/
│
├── alembic/
├── data/
│   ├── knowledge_base/
│   └── seed/
│
├── docs/
├── scripts/
├── tests/
│
├── .github/
│   └── workflows/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
├── .env.example
└── README.md
```

---

## Optimization Approach

### CEGP-Inspired Optimization

The current optimization strategy considers three primary objectives:

```text
Carbon Emissions
       |
       +---- 60%
       |
Energy Consumption
       |
       +---- 30%
       |
Estimated Cost
       |
       +---- 10%
```

Candidate providers are normalized and evaluated using a weighted score.

Providers that violate the workload deadline are removed before optimization.

### EST Baseline

EST provides an execution-time-oriented comparison.

The process is:

1. Remove providers that violate the deadline.
2. Compare estimated execution times.
3. Select the feasible provider with the lowest execution time.

Both approaches return information about:

* Energy consumption
* Carbon emissions
* Cost
* Execution time

---

## RAG and AI

### RAG Pipeline

```text
Research PDF
     |
     v
Document Chunking
     |
     v
Embeddings
     |
     v
PostgreSQL + pgvector
     |
     v
Semantic Retrieval
     |
     v
Relevant Context
     |
     v
OpenRouter LLM
     |
     v
Grounded Response
```

### Agentic Workflow

```text
User Request
     |
     v
GreenCloud Agent
     |
     +-----------> RAG Tool
     |
     +-----------> Optimization Tool
                         |
                         v
                Deterministic Engine
                         |
                         v
                  Structured Result
                         |
                         v
                   AI Explanation
```

This separation ensures that numerical calculations remain deterministic while the AI layer handles research, orchestration, and explanation.

---

## Getting Started

### Prerequisites

* Python 3.11+
* Docker Desktop
* Git
* OpenRouter API key

### Clone the Repository

```bash
git clone https://github.com/Priyanshi248/greencloud-optimizer.git
cd greencloud-optimizer
```

### Create Virtual Environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file

### Start PostgreSQL

```bash
docker compose up -d postgres
```

### Run Migrations

```bash
alembic upgrade head
```

### Start the Application

```bash
uvicorn app.main:app --reload
```

---

## API Documentation

Interactive API documentation is available through Swagger

### Main Endpoints

| Method | Endpoint            | Description                    |
| ------ | ------------------- | ------------------------------ |
| GET    | `/health`           | API health check               |
| POST   | `/optimization/run` | Run workload optimization      |
| POST   | `/chat`             | Interact with the AI assistant |

Example optimization request:

```json
{
  "workload_id": "YOUR_WORKLOAD_ID",
  "algorithm": "cegp"
}
```

Example AI request:

```json
{
  "message": "What is CEGP?"
}
```

---

## Testing

Run the test suite using:

```bash
pytest -v
```

Tests currently cover:

* Energy calculations
* Carbon calculations
* Cost calculations
* CEGP optimization
* EST baseline
* Database connectivity
* Optimization service

---

## Why GreenCloud Optimizer?

Cloud computing is optimized traditionally around factors such as cost and execution time, while environmental impact is often overlooked.
GreenCloud Optimizer addresses this by incorporating carbon emissions and energy consumption into cloud workload optimization, alongside cost, execution time, and workload deadlines.

The goal is to make cloud resource selection more sustainable, efficient, and constraint-aware through a combination of deterministic optimization and AI-assisted decision support.
* Adaptive scheduling based on changing carbon intensity
* Large-scale real-world evaluation
