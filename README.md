# ClinicFlow AI

## AI-Powered Multi-Tenant Clinic Operations, Workflow Automation & Product Intelligence Platform

ClinicFlow AI is a full-stack B2B SaaS platform designed to demonstrate how clinic operations can be managed through configurable workflows, secure APIs, AI-assisted operations, controlled MCP tools, monitoring, and automated software delivery.

It is **not a hospital chatbot**. The platform focuses on the complete operational lifecycle:

**Clinic onboarding → authentication → clinic operations → workflow configuration → automated execution → AI assistance → monitoring → testing → CI/CD → Docker deployment**

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Application Modules](#application-modules)
- [AI and MCP Architecture](#ai-and-mcp-architecture)
- [Workflow Automation](#workflow-automation)
- [Security](#security)
- [Database](#database)
- [Monitoring](#monitoring)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [GitHub Actions CI](#github-actions-ci)
- [Project Structure](#project-structure)
- [Local Setup](#local-setup)
- [Service URLs](#service-urls)
- [Example AI Queries](#example-ai-queries)
- [Engineering Highlights](#engineering-highlights)
- [Future Enhancements](#future-enhancements)
- [Author](#author)

---

# Overview

ClinicFlow AI is built as a realistic clinic-management and automation platform with a multi-tenant foundation.

A clinic can manage:

- Patients
- Doctors
- Appointments
- Workflow configurations
- Workflow execution history
- AI-assisted operational queries

The backend provides secure APIs and tenant-aware data access. The AI layer uses LangGraph for orchestration and connects to controlled clinic-data operations through the Model Context Protocol (MCP).

The system is containerized with Docker Compose and monitored using Prometheus and Grafana. GitHub Actions automatically validates backend tests, frontend builds, and Docker image builds.

---

# Key Features

## 1. Multi-Tenant Clinic Architecture

Each clinic is represented as a tenant.

Tenant-aware services use the authenticated user's clinic context so operational data is scoped to the appropriate clinic.

This provides the foundation for a SaaS architecture where multiple clinics can use the same application while keeping their data logically separated.

---

## 2. Authentication

ClinicFlow uses JWT-based authentication.

Capabilities include:

- User registration
- Login
- JWT access tokens
- Token expiration
- Token revocation
- Redis-backed login rate limiting
- Active-user validation
- Role-based access control

---

## 3. Role-Based Access Control

The backend supports role-aware authorization.

Different users can receive different levels of access to clinic operations.

The authorization layer is separated from authentication so that:

**Authentication answers:**

> Who are you?

**Authorization answers:**

> What are you allowed to do?

---

## 4. Clinic Operations

The application provides operational management for:

### Patients

- Create patients
- View patients
- Search patients
- Maintain patient information
- Track active/inactive status

### Doctors

- Create and manage doctors
- Store specialization
- Store license information
- Track active status

### Appointments

- Create appointments
- Associate patients and doctors
- Track appointment status
- View scheduled appointments

---

## 5. Workflow Configuration

Clinic administrators can configure workflows instead of hard-coding every operational process.

A workflow contains configuration such as:

- Internal workflow name
- Display name
- Description
- Enabled/disabled state
- Schedule type
- Schedule time

The current scheduler supports database-driven daily workflow execution.

---

## 6. Workflow Execution History

Every workflow execution can be tracked.

The history layer provides visibility into:

- Workflow name
- Execution status
- Start/end information
- Execution results
- Errors where applicable

This separates **workflow configuration** from **workflow execution**, making the automation system easier to monitor and extend.

---

## 7. AI Operations Assistant

The AI assistant can answer operational questions using controlled clinic data.

Examples:

- "How many active patients are there?"
- "Show today's appointments."
- "Find Rahul Kumar."
- "Show Rahul Kumar's appointments."
- "Give me today's clinic summary."

The AI layer does not directly receive unrestricted database access.

Instead, it uses defined tools through MCP.

---

# Architecture

```text
                         ┌─────────────────────────┐
                         │      React Frontend      │
                         │         :5173            │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     FastAPI Backend      │
                         │         :8000            │
                         └──────┬─────┬─────┬──────┘
                                │     │     │
                ┌───────────────┘     │     └────────────────┐
                ▼                     ▼                      ▼
       ┌────────────────┐     ┌─────────────┐       ┌────────────────┐
       │   PostgreSQL   │     │    Redis    │       │   MCP Server   │
       │   + pgvector   │     │    :6379    │       │     :8001      │
       │     :5433      │     └─────────────┘       └───────┬────────┘
       └────────────────┘                                    │
                                                             ▼
                                                    ┌────────────────┐
                                                    │    LangGraph   │
                                                    │    AI Agent    │
                                                    └───────┬────────┘
                                                            │
                                                            ▼
                                                    ┌────────────────┐
                                                    │ Ollama / Qwen  │
                                                    └────────────────┘


                         Monitoring Layer
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
             ┌─────────────┐         ┌─────────────┐
             │ Prometheus  │         │   Grafana   │
             │    :9090    │         │    :3000    │
             └─────────────┘         └─────────────┘
```

---

# Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| AI orchestration | LangGraph |
| LLM | Ollama, Qwen |
| Tool connectivity | Model Context Protocol (MCP) |
| Database | PostgreSQL 18 |
| Vector database | pgvector |
| Embeddings | nomic-embed-text |
| Cache / security state | Redis |
| Authentication | JWT |
| Authorization | RBAC |
| Scheduling | APScheduler |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| API testing | Pytest |
| Containers | Docker, Docker Compose |
| Monitoring | Prometheus, Grafana |
| CI | GitHub Actions |
| Web server | Uvicorn / Nginx |

---

# Application Modules

The backend is organized around separate responsibilities rather than putting everything into one application file.

```text
backend/app/
│
├── api/
│   ├── auth
│   ├── patients
│   ├── doctors
│   ├── appointments
│   ├── workflows
│   ├── workflow history
│   └── AI
│
├── ai/
│   └── LangGraph agent
│
├── core/
│   ├── configuration
│   ├── security
│   ├── authentication dependencies
│   ├── RBAC
│   ├── tenant handling
│   ├── rate limiting
│   └── token revocation
│
├── db/
│   ├── database session
│   ├── dependencies
│   └── base model
│
├── models/
│   ├── Clinic
│   ├── User
│   ├── Doctor
│   ├── Patient
│   ├── Appointment
│   ├── WorkflowConfiguration
│   ├── WorkflowExecution
│   └── AuditLog
│
├── schemas/
│   └── request/response validation
│
└── services/
    ├── authentication
    ├── workflows
    ├── scheduler
    └── related business services
```

---

# AI and MCP Architecture

The AI assistant follows a controlled tool-use architecture.

```text
User Question
     │
     ▼
React AI Interface
     │
     ▼
FastAPI AI Endpoint
     │
     ▼
LangGraph Agent
     │
     ├── Understand intent
     │
     ├── Select operation
     │
     └── Call controlled tool
             │
             ▼
        MCP Client
             │
             ▼
        MCP Server
             │
             ├── Active patient count
             ├── Patient search
             ├── Patient appointments
             └── Today's appointments
             │
             ▼
         PostgreSQL
```

## Why MCP?

MCP provides a structured boundary between the AI agent and application operations.

Instead of allowing the LLM to generate arbitrary database queries, the system exposes specific tools.

Current read-only MCP operations include:

### Active patient count

Returns the number of active patients for a clinic.

### Patient search

Searches patients within the current clinic.

### Patient appointments

Retrieves appointments for a selected patient.

### Today's appointments

Retrieves appointments scheduled for the current day.

This approach provides a controlled interface for AI-driven operations.

---

# LangGraph Agent

LangGraph is used to orchestrate the AI agent.

The agent maintains state containing:

- Conversation messages
- Clinic ID
- Clinic-related data

The agent identifies operational intent and routes the request to the corresponding tool.

Examples:

```text
"How many active patients are there?"
        ↓
active_patient_count
```

```text
"Show today's appointments."
        ↓
today_appointments
```

```text
"Find Rahul Kumar."
        ↓
patient_search
```

```text
"Show Rahul Kumar's appointments."
        ↓
patient_appointments
```

---

# Workflow Automation

ClinicFlow uses database-driven workflow configuration.

Example:

```text
Workflow:
    daily_clinic_summary

Display name:
    Daily Clinic Summary

Schedule:
    Daily at 08:00

Status:
    Enabled
```

The scheduler loads enabled workflows from the database and creates jobs dynamically.

The execution layer then dispatches the workflow to its appropriate executor.

This design makes it possible to add additional workflow types later without redesigning the complete scheduler.

---

# Security

Security is implemented at multiple layers.

## JWT Authentication

JWT tokens contain authentication claims and expiration information.

The backend validates:

- Token signature
- Token type
- Subject
- Issued-at information
- Expiration
- Token identifier

---

## Token Revocation

Redis is used to track revoked tokens.

This allows a token to become invalid before its natural expiration time, such as after logout.

---

## Login Rate Limiting

Redis-backed rate limiting helps prevent repeated login attempts from being executed without restriction.

---

## RBAC

Role-based dependencies protect restricted API operations.

---

## Tenant Isolation

Clinic context is taken from the authenticated user rather than accepting arbitrary clinic ownership from a normal client request.

This reduces the risk of cross-tenant data access.

---

## Audit Logging

Important application operations are recorded in the audit log layer.

This provides an operational trail for relevant actions.

---

# Database

The application currently uses PostgreSQL with pgvector support.

Main tables:

```text
clinics
    │
    ├── users
    ├── doctors
    ├── patients
    │       │
    │       └── appointments
    │
    ├── appointments
    ├── workflow_configurations
    │       │
    │       └── workflow_executions
    │
    └── audit_logs
```

Alembic manages schema migrations.

The current migration history includes creation of:

- Clinics
- Users
- Doctors
- Patients
- Appointments
- Workflow executions
- Workflow configurations
- Audit logs
- Workflow configuration uniqueness constraints

---

# Monitoring

ClinicFlow exposes application metrics through Prometheus instrumentation.

The monitoring stack is:

```text
FastAPI
   │
   ▼
/metrics
   │
   ▼
Prometheus
   │
   ▼
Grafana
```

The project includes a Grafana dashboard named:

**ClinicFlow AI - System Monitoring**

The dashboard can be used to observe application traffic and service behavior.

---

# Testing

The backend has an automated Pytest suite.

Current verified result:

```text
158 passed
1 warning
```

The tests cover areas including:

- Authentication
- JWT behavior
- RBAC
- Tenant isolation
- Patients
- Doctors
- Appointments
- Workflows
- Workflow history
- Scheduler behavior
- Audit logging
- MCP integration
- AI agent behavior
- API behavior
- Security-related behavior

The test database can be recreated using Alembic migrations and the deterministic CI seed in:

```text
tests/ci_seed.sql
```

The CI seed contains deterministic, non-production test fixtures rather than a development database dump.

---

# Docker Deployment

ClinicFlow is containerized using Docker Compose.

The complete application stack contains:

```text
1. PostgreSQL + pgvector
2. Redis
3. MCP Server
4. FastAPI Backend
5. React Frontend
6. Prometheus
7. Grafana
```

Start the complete stack with:

```powershell
docker compose up -d
```

To rebuild application images:

```powershell
docker compose up -d --build
```

Check service status:

```powershell
docker compose ps
```

Stop the stack:

```powershell
docker compose down
```

Persistent Docker volumes are used for:

- PostgreSQL data
- Redis data
- Prometheus data
- Grafana data

---

# GitHub Actions CI

The repository includes a GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

The CI pipeline validates:

### Backend Tests

- Starts PostgreSQL + pgvector
- Starts Redis
- Runs Alembic migrations
- Loads deterministic CI seed
- Starts MCP server
- Runs the full Pytest suite

### Frontend Build

Runs:

```text
npm ci
npm run build
```

### Backend Docker Build

Builds:

```text
backend/Dockerfile
```

### MCP Docker Build

Builds:

```text
mcp_server/Dockerfile
```

### Frontend Docker Build

Builds:

```text
frontend/Dockerfile
```

The current GitHub Actions workflow has been successfully verified with all five jobs passing.

---

# Project Structure

```text
ClinicFlow-AI/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   │
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── package-lock.json
│
├── mcp_server/
│   ├── server.py
│   ├── http_server.py
│   └── Dockerfile
│
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
│       └── provisioning/
│
├── tests/
│   ├── ci_seed.sql
│   └── test_*.py
│
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
├── pytest.ini
├── .env.example
├── .dockerignore
├── .gitignore
└── README.md
```

---

# Local Setup

## Prerequisites

Install:

- Python 3.11+
- Node.js
- Docker Desktop
- Git
- Ollama

The project was developed and verified using Docker Desktop and a local Ollama installation.

---

## 1. Clone the repository

```powershell
git clone https://github.com/Suriya1903/ClinicFlow-AI.git
cd ClinicFlow-AI
```

---

## 2. Create Python environment

```powershell
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
pip install -r requirements.txt
```

---

## 3. Configure environment

Copy:

```text
.env.example
```

to:

```text
.env
```

Then configure the local database password and other environment settings.

**Do not commit `.env` to Git.**

---

## 4. Prepare Ollama

Make sure Ollama is running and the configured models are available.

The project uses:

```text
qwen3:4b
nomic-embed-text
```

---

## 5. Start Docker services

```powershell
docker compose up -d --build
```

Check:

```powershell
docker compose ps
```

---

## 6. Run migrations

For a local environment where Alembic is being run from Windows, ensure `DATABASE_URL` points to the Docker PostgreSQL host port.

Example:

```text
postgresql+psycopg://postgres:<password>@localhost:5433/clinicflow_db
```

Then:

```powershell
alembic upgrade head
```

---

## 7. Run tests

```powershell
pytest -q
```

Expected verified result:

```text
158 passed
```

---

# Service URLs

When running locally:

| Service | URL |
|---|---|
| React Frontend | http://localhost:5173 |
| FastAPI Backend | http://localhost:8000 |
| Backend Health | http://localhost:8000/health |
| MCP Server | http://localhost:8001/mcp |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| PostgreSQL | localhost:5433 |
| Redis | localhost:6379 |

---

# Example AI Queries

After logging into the application, the AI interface can be used for operational questions.

### Active patients

```text
How many active patients are there?
```

### Today's appointments

```text
Show today's appointments.
```

### Patient search

```text
Find Rahul Kumar.
```

### Patient appointments

```text
Show Rahul Kumar's appointments.
```

### Clinic summary

```text
Give me today's clinic summary.
```

The agent interprets the request and uses the appropriate controlled MCP operation.

---

# Engineering Highlights

ClinicFlow AI demonstrates several production-oriented engineering concepts:

- Multi-tenant SaaS architecture
- REST API design
- JWT authentication
- RBAC authorization
- Redis-backed security controls
- Database migrations with Alembic
- PostgreSQL relational modeling
- pgvector readiness for vector workloads
- LangGraph agent orchestration
- MCP-based tool integration
- Local LLM execution with Ollama
- Database-driven workflow scheduling
- Workflow execution history
- Audit logging
- React frontend
- Docker multi-service architecture
- Prometheus metrics
- Grafana monitoring
- Automated Pytest testing
- Deterministic CI database fixtures
- GitHub Actions CI
- Automated Docker image builds

---

# Future Enhancements

Possible future extensions include:

- Additional workflow executors
- More advanced AI evaluation metrics
- RAG-powered clinic knowledge retrieval
- Semantic search over clinic documents
- Vector-based patient/operational knowledge retrieval
- More granular permissions
- OAuth/OpenID Connect integration
- Production secrets management
- Kubernetes deployment
- Horizontal scaling
- Distributed workflow execution
- Advanced product analytics
- Automated AI quality monitoring

These are extension points rather than requirements for the current working implementation.

---

# Author

**Suriya MG**

B.Tech Computer Science and Engineering  
Vellore Institute of Technology

GitHub:

https://github.com/Suriya1903/ClinicFlow-AI

---

## Project Summary

ClinicFlow AI combines:

**Full-stack development + AI agents + MCP + workflow automation + security + databases + monitoring + Docker + automated testing + CI/CD**

into a single end-to-end software engineering project.

The project is designed to demonstrate not only how to build an AI feature, but how to integrate AI into a secure, testable, observable, and deployable application architecture.
