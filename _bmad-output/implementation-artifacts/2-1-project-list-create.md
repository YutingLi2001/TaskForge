# Story 2.1: Project List & Create

Status: done

## Story

As a **user**,
I want to **view my projects and create new ones**,
So that **I can organize my work**.

## Acceptance Criteria

1. **Given** I am logged in **When** I navigate to the projects page **Then** I see a list of my projects
2. **Given** I am logged in **When** I create a new project by entering a name **Then** the project is created and appears in my list
3. **Given** I am logged in **Then** only my own projects are visible (not other users')
4. **Given** I am not authenticated **When** I try to access /projects or the API **Then** I am redirected/receive 401
5. **Given** I submit an empty project name **Then** I see a validation error
6. **Given** I have no projects **Then** I see an empty state message

## Tasks / Subtasks

- [x] **Task 1: Project Database Model** (AC: 1, 2, 3)
  - [x] Create `backend/app/models/project.py` with Project model
  - [x] Add fields: id, name, user_id (FK), created_at, updated_at
  - [x] Add relationship to User model
  - [x] Export from `backend/app/models/__init__.py`
  - [x] Create projects table (manual migration or auto-create)

- [x] **Task 2: Project Schemas** (AC: 2, 5)
  - [x] Create `backend/app/schemas/project.py`
  - [x] Add `ProjectCreate` schema (name: str, min_length=1)
  - [x] Add `ProjectResponse` schema (id, name, user_id, created_at, updated_at)
  - [x] Add `ProjectListResponse` schema for list endpoint
  - [x] Export from `backend/app/schemas/__init__.py`

- [x] **Task 3: Projects API Router** (AC: 1, 2, 3, 4)
  - [x] Create `backend/app/routers/projects.py`
  - [x] Implement `GET /api/projects` - list current user's projects
  - [x] Implement `POST /api/projects` - create new project for current user
  - [x] Use `get_current_user` dependency for authentication
  - [x] Filter projects by current user's id
  - [x] Register router in `backend/app/main.py`

- [x] **Task 4: Backend Testing** (AC: 1, 2, 3, 4, 5)
  - [x] Create `backend/tests/api/test_projects_api.py`
  - [x] Test: GET /projects returns empty list for new user
  - [x] Test: POST /projects creates project and returns it
  - [x] Test: GET /projects returns only user's own projects
  - [x] Test: POST /projects with empty name returns 422
  - [x] Test: Unauthenticated requests return 401

- [x] **Task 5: Frontend API Client** (AC: 1, 2)
  - [x] Add `ProjectData` interface to `frontend/src/api/client.ts`
  - [x] Add `projectsApi` object with `list()` and `create()` methods
  - [x] Follow existing authApi pattern

- [x] **Task 6: Projects Page UI** (AC: 1, 2, 5, 6)
  - [x] Create `frontend/src/pages/Projects.tsx`
  - [x] Display list of projects (name, created date)
  - [x] Add "Create Project" form with name input
  - [x] Show loading state while fetching
  - [x] Show empty state when no projects exist
  - [x] Show validation error for empty name
  - [x] Style with Tailwind CSS matching existing design

- [x] **Task 7: Update App Routing** (AC: 1, 4)
  - [x] Add `/projects` route to `frontend/src/App.tsx`
  - [x] Wrap with ProtectedRoute
  - [x] Update Dashboard to link to Projects page (or make Projects the new dashboard)

- [x] **Task 8: Frontend Testing** (AC: 1, 2, 5, 6)
  - [x] Create `frontend/src/pages/Projects.test.tsx`
  - [x] Test: Projects page renders project list
  - [x] Test: Create form submits and adds project to list
  - [x] Test: Empty name shows validation error
  - [x] Test: Empty state displays when no projects

## Dev Notes

### Architecture Compliance

**Backend Structure:**
- Model: `backend/app/models/project.py`
- Schema: `backend/app/schemas/project.py`
- Router: `backend/app/routers/projects.py`
- Tests: `backend/tests/api/test_projects_api.py`

**Frontend Structure:**
- Page: `frontend/src/pages/Projects.tsx`
- API: Add to `frontend/src/api/client.ts`
- Route: Add to `frontend/src/App.tsx`

**Database:** SQLite (dev) / PostgreSQL (prod) via SQLAlchemy

### Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| Authentication | `get_current_user` dependency from Epic 1 |
| User isolation | Filter by `user_id = current_user.id` |
| Validation | Pydantic schemas with min_length |
| API format | `{ "data": [...] }` wrapper |
| Frontend state | useState for projects list |

### Database Schema

**projects table:**
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_projects_user_id ON projects(user_id);
```

### API Endpoint Specs

**GET /api/projects** (Protected)

Request Headers:
```
Authorization: Bearer <access_token>
```

Success Response (200):
```json
{
  "data": [
    {
      "id": 1,
      "name": "My Project",
      "user_id": 1,
      "created_at": "2026-01-21T00:00:00Z",
      "updated_at": "2026-01-21T00:00:00Z"
    }
  ]
}
```

---

**POST /api/projects** (Protected)

Request:
```json
{
  "name": "New Project"
}
```

Success Response (201):
```json
{
  "data": {
    "id": 2,
    "name": "New Project",
    "user_id": 1,
    "created_at": "2026-01-21T00:00:00Z",
    "updated_at": "2026-01-21T00:00:00Z"
  }
}
```

Validation Error (422):
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```

### Component Specifications

**Project Model:**
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="projects")
```

**Projects Router Pattern:**
```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils.auth import get_current_user
from ..models.user import User
from ..models.project import Project
from ..schemas.project import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=dict)
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    return {"data": projects}

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = Project(name=project_data.name, user_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"data": project}
```

**Frontend projectsApi:**
```typescript
export interface ProjectData {
  id: number;
  name: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectData {
  name: string;
}

export const projectsApi = {
  list: () => api.get<ApiResponse<ProjectData[]>>('/projects'),
  create: (data: CreateProjectData) =>
    api.post<ApiResponse<ProjectData>>('/projects', data),
};
```

### References

**Planning Documents:**
- [PRD: FR5, FR6](../planning-artifacts/prd.md)
- [Architecture: Project Structure](../planning-artifacts/architecture.md)
- [Epics: Story 2.1](../planning-artifacts/epics.md#Story-2.1-Project-List--Create)

**Source: Epic 1 Patterns**
- [backend/app/utils/auth.py](../../backend/app/utils/auth.py) - get_current_user dependency
- [backend/app/models/user.py](../../backend/app/models/user.py) - Model pattern
- [backend/app/routers/auth.py](../../backend/app/routers/auth.py) - Router pattern
- [frontend/src/api/client.ts](../../frontend/src/api/client.ts) - API client pattern
- [frontend/src/pages/Login.tsx](../../frontend/src/pages/Login.tsx) - Page/form pattern

## Dev Agent Record

### Agent Model Used

GPT-5 (Codex CLI)

### Completion Notes List

- Added Project model, schemas, and projects router with authenticated list/create endpoints.
- Implemented Projects page UI, API client, and routing from Dashboard.
- Added backend API coverage plus frontend Projects page tests and updated Dashboard tests.
- Hardened project name validation against whitespace-only values and added coverage.
- Redirects unauthorized project list/create responses via logout handler.
- Projects endpoints avoid cross-thread DB sessions for safety.
- Standardized auth error handling on status codes in auth routes and Projects UI.
- Tests: `python -m unittest backend.tests.unit.test_project_model`, `python -m unittest backend.tests.unit.test_project_schema`, `python -m unittest backend.tests.unit.test_projects_router`, `python -m unittest backend.tests.api.test_projects_api`, `npm test` (frontend), `scripts/windows/run-backend-tests.bat`, `scripts/windows/run-frontend-tests.bat`.
  - Additional: `python -m unittest backend.tests.unit.test_project_schema` (post-review fix).

### File List

**Created:**
- backend/app/models/project.py
- backend/app/routers/projects.py
- backend/app/schemas/project.py
- backend/tests/api/test_projects_api.py
- backend/tests/unit/test_project_model.py
- backend/tests/unit/test_project_schema.py
- backend/tests/unit/test_projects_router.py
- frontend/src/pages/Projects.test.tsx
- frontend/src/pages/Projects.tsx

**Modified:**
- backend/app/main.py
- backend/app/models/__init__.py
- backend/app/models/user.py
- backend/app/routers/__init__.py
- backend/app/routers/projects.py
- backend/app/schemas/__init__.py
- backend/app/schemas/project.py
- backend/tests/unit/test_project_schema.py
- frontend/src/App.tsx
- frontend/src/api/client.ts
- frontend/src/components/ProtectedRoute.tsx
- frontend/src/components/PublicRoute.tsx
- frontend/src/components/ProtectedRoute.test.tsx
- frontend/src/components/PublicRoute.test.tsx
- frontend/src/components/Header.test.tsx
- frontend/src/pages/Dashboard.test.tsx
- frontend/src/pages/Dashboard.tsx
- frontend/src/pages/Projects.test.tsx
- frontend/src/pages/Projects.tsx
