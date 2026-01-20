---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - "_bmad-output/planning-artifacts/prd.md"
  - "_bmad-output/planning-artifacts/product-brief-TaskForge-2026-01-19.md"
workflowType: 'architecture'
project_name: 'TaskForge'
user_name: 'Yuting'
date: '2026-01-19'
status: 'complete'
completedAt: '2026-01-19'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
- User auth: Registration, login, logout, protected routes
- Project CRUD: List, create, view, edit, delete
- Task CRUD: List, create, edit, toggle status, delete

**Non-Functional Requirements:**
- Performance: Page load <3s, API <500ms
- Security: bcrypt passwords, JWT with expiration, HTTPS
- Reliability: Data persistence, graceful error handling

### Scale & Complexity

- Primary domain: Full-stack web application
- Complexity level: Low
- Estimated components: ~6 (Auth, Users, Projects, Tasks, API, Frontend)

### Technical Constraints

- Stack defined: FastAPI (Python), React (TypeScript), PostgreSQL, Docker, AWS Lightsail

### Cross-Cutting Concerns

- Authentication: JWT validation on all protected endpoints
- Error handling: Consistent API error responses

## Starter Template Evaluation

### Primary Technology Domain

Full-stack web application with Python backend and React frontend.

### Decision: No Starter Template

**Rationale:** Stack is already fully defined (FastAPI + React + PostgreSQL). Clean minimal setup preferred for learning purposes.

**Initialization Commands:**

Backend:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose passlib bcrypt
```

Frontend:
```bash
npm create vite@latest frontend -- --template react-ts
```

**Architectural Decisions Provided by Setup:**
- Language: Python 3.x (backend), TypeScript (frontend)
- Build: Vite for frontend bundling
- No additional framework conventions imposed

## Core Architectural Decisions

### Data Architecture
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Manual SQL (no Alembic)

### Authentication & Security
- **Auth Method:** JWT tokens
- **Password Hashing:** bcrypt
- **Token Storage:** localStorage (frontend)

### API & Communication
- **Pattern:** REST API
- **HTTP Client:** Native fetch()
- **Response Format:** JSON

### Frontend Architecture
- **Framework:** React 18+ with TypeScript
- **State Management:** useState + useEffect (no external library)
- **Styling:** Tailwind CSS
- **Build Tool:** Vite

### Infrastructure
- **Containerization:** Docker
- **Deployment:** Deferred (local development first)

## Implementation Patterns

### Naming Conventions

| Area | Convention | Example |
|------|------------|---------|
| DB Tables | snake_case, plural | `users`, `projects`, `tasks` |
| DB Columns | snake_case | `user_id`, `created_at` |
| API Endpoints | /api/plural | `/api/projects`, `/api/tasks` |
| React Components | PascalCase | `ProjectList.tsx` |
| Python Functions | snake_case | `get_user_by_id()` |
| TS Functions | camelCase | `fetchProjects()` |

### API Response Format

```json
{ "data": {...} }        // Success
{ "detail": "..." }      // Error (FastAPI default)
```

### File Organization

- Backend: `backend/app/` → `models/`, `routers/`, `schemas/`
- Frontend: `frontend/src/` → `components/`, `pages/`, `api/`

## Project Structure

```
TaskForge/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   └── task.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   └── task.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   └── tasks.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── auth.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   │   ├── Layout.tsx
│   │   │   ├── ProjectList.tsx
│   │   │   └── TaskList.tsx
│   │   └── pages/
│   │       ├── Login.tsx
│   │       ├── Register.tsx
│   │       ├── Projects.tsx
│   │       └── ProjectDetail.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Architecture Validation

### Validation Summary

| Check | Status |
|-------|--------|
| Decision Compatibility | ✅ Pass |
| Pattern Consistency | ✅ Pass |
| Structure Alignment | ✅ Pass |
| FR Coverage (14/14) | ✅ Pass |
| NFR Coverage | ✅ Pass |

### Requirements Mapping

- **Auth (FR1-5):** `routers/auth.py` + `utils/auth.py` + `Login.tsx`/`Register.tsx`
- **Projects (FR6-9):** `routers/projects.py` + `Projects.tsx`/`ProjectDetail.tsx`
- **Tasks (FR10-14):** `routers/tasks.py` + `TaskList.tsx`

**Architecture Status:** READY FOR IMPLEMENTATION ✅
