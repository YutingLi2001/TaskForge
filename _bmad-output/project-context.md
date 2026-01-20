---
project_name: 'TaskForge'
user_name: 'Yuting'
date: '2026-01-19'
status: 'complete'
---

# Project Context for AI Agents

_Critical rules and patterns for implementing TaskForge. Follow these exactly._

---

## Technology Stack

- **Backend:** FastAPI, Uvicorn, SQLAlchemy, PostgreSQL, python-jose, passlib, bcrypt
- **Frontend:** React 18+, TypeScript, Tailwind CSS, Vite
- **Infrastructure:** Docker

## Python/FastAPI Rules

- Use Pydantic schemas for all request/response models
- Async endpoints for I/O operations
- Dependency injection for DB sessions
- JWT in Authorization header: `Bearer <token>`

## React/TypeScript Rules

- Functional components only (no class components)
- `useState`/`useEffect` for state (no external state library)
- Store JWT in localStorage
- Use native `fetch()` for API calls

## Naming Conventions

| Area | Convention | Example |
|------|------------|---------|
| DB Tables | snake_case, plural | `users`, `projects`, `tasks` |
| DB Columns | snake_case | `user_id`, `created_at` |
| API Endpoints | /api/plural | `/api/projects`, `/api/tasks` |
| React Components | PascalCase | `ProjectList.tsx` |
| Python Functions | snake_case | `get_user_by_id()` |
| TS Functions | camelCase | `fetchProjects()` |

## API Response Format

```json
{ "data": {...} }        // Success
{ "detail": "..." }      // Error (FastAPI default)
```

## Critical Rules (Don't Miss)

- Always hash passwords with bcrypt before storing
- JWT tokens must have expiration
- Validate user owns resource before CRUD operations
- Protected routes require valid JWT
- Return 401 for invalid/expired tokens, 403 for unauthorized access
