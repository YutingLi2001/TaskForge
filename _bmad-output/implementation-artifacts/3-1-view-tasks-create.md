# Story 3.1: View Tasks & Create

Status: ready-for-dev

## Story

As a **user**,
I want to **view tasks in my project and create new ones**,
So that **I can track my work**.

## Acceptance Criteria

1. **Given** I am on a project detail page **When** I view the tasks section **Then** I see all tasks for that project
2. **Given** I am on a project detail page **When** I create a new task by entering a title **Then** the task is added to the list
3. **Given** I create a task **Then** it defaults to incomplete status (is_complete: false)
4. **Given** I try to view tasks for a project I don't own **Then** the API returns 403 Forbidden
5. **Given** I try to view tasks for a project that doesn't exist **Then** the API returns 404 Not Found
6. **Given** I am not authenticated **When** I try to access tasks **Then** the API returns 401 Unauthorized
7. **Given** I submit an empty task title **Then** I see a validation error
8. **Given** a project has no tasks **Then** I see an empty state message

## Tasks / Subtasks

- [ ] **Task 1: Task Database Model** (AC: 1, 2, 3)
  - [ ] Create `backend/app/models/task.py` with Task model
  - [ ] Add fields: id, title, is_complete (default False), project_id (FK), created_at, updated_at
  - [ ] Add relationship to Project model
  - [ ] Update Project model with tasks relationship (back_populates)
  - [ ] Export from `backend/app/models/__init__.py`
  - [ ] Create tasks table (auto-create via SQLAlchemy)

- [ ] **Task 2: Task Schemas** (AC: 2, 7)
  - [ ] Create `backend/app/schemas/task.py`
  - [ ] Add `TaskCreate` schema (title: str, min_length=1, strip whitespace)
  - [ ] Add `TaskResponse` schema (id, title, is_complete, project_id, created_at, updated_at)
  - [ ] Add `TaskListResponse` and `TaskDataResponse` for API response wrapper
  - [ ] Export from `backend/app/schemas/__init__.py`

- [ ] **Task 3: Tasks API Router** (AC: 1, 2, 3, 4, 5, 6)
  - [ ] Create `backend/app/routers/tasks.py`
  - [ ] Implement `GET /api/projects/{project_id}/tasks` - list tasks for project
  - [ ] Implement `POST /api/projects/{project_id}/tasks` - create task in project
  - [ ] Use `get_current_user` dependency for authentication
  - [ ] Verify project exists (404 if not)
  - [ ] Verify project ownership (403 if not owner)
  - [ ] Register router in `backend/app/main.py`

- [ ] **Task 4: Backend Testing** (AC: 1, 2, 3, 4, 5, 6, 7)
  - [ ] Create `backend/tests/api/test_tasks_api.py`
  - [ ] Test: GET /projects/{id}/tasks returns empty list for project with no tasks
  - [ ] Test: POST /projects/{id}/tasks creates task with is_complete=false
  - [ ] Test: GET /projects/{id}/tasks returns tasks for project
  - [ ] Test: POST /projects/{id}/tasks with empty title returns 422
  - [ ] Test: POST /projects/{id}/tasks with whitespace-only title returns 422
  - [ ] Test: GET/POST returns 404 for non-existent project
  - [ ] Test: GET/POST returns 403 for project not owned by user
  - [ ] Test: GET/POST returns 401 for unauthenticated request

- [ ] **Task 5: Frontend API Client** (AC: 1, 2)
  - [ ] Add `TaskData` interface to `frontend/src/api/client.ts`
  - [ ] Add `CreateTaskData` interface
  - [ ] Add `tasksApi` object with `list(projectId)` and `create(projectId, data)` methods
  - [ ] Follow existing projectsApi pattern

- [ ] **Task 6: Tasks UI in ProjectDetail** (AC: 1, 2, 7, 8)
  - [ ] Update `frontend/src/pages/ProjectDetail.tsx`
  - [ ] Add state for tasks list, loading, error
  - [ ] Fetch tasks on mount using project ID
  - [ ] Display task list (title, completion status indicator)
  - [ ] Add "Create Task" form with title input
  - [ ] Show loading state while fetching
  - [ ] Show empty state when no tasks exist
  - [ ] Show validation error for empty title
  - [ ] Handle 403/404 errors gracefully
  - [ ] Style with Tailwind CSS matching existing design

- [ ] **Task 7: Frontend Testing** (AC: 1, 2, 7, 8)
  - [ ] Update `frontend/src/pages/ProjectDetail.test.tsx`
  - [ ] Test: ProjectDetail renders task list
  - [ ] Test: Create task form submits and adds task to list
  - [ ] Test: Empty title shows validation error
  - [ ] Test: Empty state displays when no tasks
  - [ ] Test: Tasks loading state displays

## Dev Notes

### Architecture Compliance

**Backend Structure:**
- Model: `backend/app/models/task.py`
- Schema: `backend/app/schemas/task.py`
- Router: `backend/app/routers/tasks.py`
- Tests: `backend/tests/api/test_tasks_api.py`

**Frontend Structure:**
- API: Add to `frontend/src/api/client.ts`
- Page: Update `frontend/src/pages/ProjectDetail.tsx`
- Tests: Update `frontend/src/pages/ProjectDetail.test.tsx`

**Database:** SQLite (dev) / PostgreSQL (prod) via SQLAlchemy

### Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| Authentication | `get_current_user` dependency from Epic 1 |
| Authorization | Verify project ownership via `project.user_id == current_user.id` |
| Nested Routes | `/api/projects/{project_id}/tasks` |
| Validation | Pydantic schemas with min_length, strip whitespace |
| API format | `{ "data": [...] }` wrapper |
| Default status | `is_complete = False` on creation |

### Database Schema

**tasks table:**
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR NOT NULL,
    is_complete BOOLEAN DEFAULT FALSE NOT NULL,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_tasks_project_id ON tasks(project_id);
```

### API Endpoint Specs

**GET /api/projects/{project_id}/tasks** (Protected)

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
      "title": "My Task",
      "is_complete": false,
      "project_id": 1,
      "created_at": "2026-01-23T00:00:00Z",
      "updated_at": "2026-01-23T00:00:00Z"
    }
  ]
}
```

Error Response (401 - not authenticated):
```json
{
  "detail": "Not authenticated"
}
```

Error Response (403 - not owner):
```json
{
  "detail": "Not authorized to access this project"
}
```

Error Response (404 - project not found):
```json
{
  "detail": "Project not found"
}
```

---

**POST /api/projects/{project_id}/tasks** (Protected)

Request:
```json
{
  "title": "New Task"
}
```

Success Response (201):
```json
{
  "data": {
    "id": 2,
    "title": "New Task",
    "is_complete": false,
    "project_id": 1,
    "created_at": "2026-01-23T00:00:00Z",
    "updated_at": "2026-01-23T00:00:00Z"
  }
}
```

Validation Error (422):
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```

### Component Specifications

**Task Model:**
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    is_complete = Column(Boolean, default=False, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="tasks")
```

**Task Schemas:**
```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(min_length=1)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Task title cannot be blank")
        return trimmed

class TaskResponse(BaseModel):
    id: int
    title: str
    is_complete: bool
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class TaskListResponse(BaseModel):
    data: list[TaskResponse]

class TaskDataResponse(BaseModel):
    data: TaskResponse
```

**Tasks Router Pattern:**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils.auth import get_current_user
from ..models.user import User
from ..models.project import Project
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskResponse, TaskListResponse, TaskDataResponse

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])

def get_project_or_404(project_id: int, current_user: User, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    return project

@router.get("", response_model=TaskListResponse)
def list_tasks(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = get_project_or_404(project_id, current_user, db)
    tasks = db.query(Task).filter(Task.project_id == project.id).all()
    return TaskListResponse(data=[TaskResponse.model_validate(t) for t in tasks])

@router.post("", response_model=TaskDataResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = get_project_or_404(project_id, current_user, db)
    task = Task(title=task_data.title, project_id=project.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskDataResponse(data=TaskResponse.model_validate(task))
```

**Frontend tasksApi:**
```typescript
export interface TaskData {
  id: number;
  title: string;
  is_complete: boolean;
  project_id: number;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskData {
  title: string;
}

export const tasksApi = {
  list: (projectId: number) =>
    api.get<ApiResponse<TaskData[]>>(`/projects/${projectId}/tasks`),
  create: (projectId: number, data: CreateTaskData) =>
    api.post<ApiResponse<TaskData>>(`/projects/${projectId}/tasks`, data),
};
```

**ProjectDetail.tsx Tasks Section Pattern:**
```tsx
// Add to existing ProjectDetail component
const [tasks, setTasks] = useState<TaskData[]>([]);
const [tasksLoading, setTasksLoading] = useState(true);
const [newTaskTitle, setNewTaskTitle] = useState('');
const [taskError, setTaskError] = useState<string | null>(null);

// Fetch tasks when project loads
useEffect(() => {
  if (!project) return;

  setTasksLoading(true);
  tasksApi.list(project.id)
    .then((response) => {
      setTasks(response.data);
    })
    .catch((err) => {
      if (err instanceof ApiRequestError && err.status === 401) {
        logout();
      }
    })
    .finally(() => setTasksLoading(false));
}, [project]);

const handleCreateTask = async (e: React.FormEvent) => {
  e.preventDefault();
  const trimmed = newTaskTitle.trim();
  if (!trimmed) {
    setTaskError('Task title is required.');
    return;
  }

  try {
    const response = await tasksApi.create(project!.id, { title: trimmed });
    setTasks([...tasks, response.data]);
    setNewTaskTitle('');
    setTaskError(null);
  } catch (err) {
    if (err instanceof ApiRequestError) {
      if (err.status === 401) {
        logout();
        return;
      }
    }
    setTaskError(err instanceof Error ? err.message : 'Failed to create task');
  }
};

// In render - Tasks section:
<section className="mt-8 rounded-lg bg-white p-6 shadow-md">
  <h2 className="text-lg font-semibold text-gray-900">Tasks</h2>

  {/* Create Task Form */}
  <form onSubmit={handleCreateTask} className="mt-4 flex gap-2">
    <input
      type="text"
      value={newTaskTitle}
      onChange={(e) => setNewTaskTitle(e.target.value)}
      placeholder="New task title"
      className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm"
    />
    <button type="submit" className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
      Add Task
    </button>
  </form>
  {taskError && <p className="mt-2 text-sm text-red-600">{taskError}</p>}

  {/* Task List */}
  {tasksLoading ? (
    <p className="mt-4 text-sm text-gray-600">Loading tasks...</p>
  ) : tasks.length === 0 ? (
    <p className="mt-4 text-sm text-gray-500">No tasks yet. Add one above!</p>
  ) : (
    <ul className="mt-4 space-y-2">
      {tasks.map((task) => (
        <li key={task.id} className="flex items-center gap-3 rounded-md border border-gray-200 px-4 py-3">
          <span className={`h-4 w-4 rounded-full ${task.is_complete ? 'bg-green-500' : 'bg-gray-300'}`} />
          <span className={task.is_complete ? 'text-gray-500 line-through' : 'text-gray-900'}>
            {task.title}
          </span>
        </li>
      ))}
    </ul>
  )}
</section>
```

### References

**Planning Documents:**
- [PRD: FR10, FR11](../planning-artifacts/prd.md)
- [Architecture: Task Structure](../planning-artifacts/architecture.md)
- [Epics: Story 3.1](../planning-artifacts/epics.md#Story-3.1-View-Tasks--Create)

**Source: Epic 2 Patterns (Follow These!)**
- [backend/app/models/project.py](../../backend/app/models/project.py) - Model pattern to follow
- [backend/app/schemas/project.py](../../backend/app/schemas/project.py) - Schema pattern to follow
- [backend/app/routers/projects.py](../../backend/app/routers/projects.py) - Router pattern to follow
- [frontend/src/api/client.ts](../../frontend/src/api/client.ts) - API client pattern to follow
- [frontend/src/pages/ProjectDetail.tsx](../../frontend/src/pages/ProjectDetail.tsx) - Page to update

**Source: Epic 1 Patterns**
- [backend/app/utils/auth.py](../../backend/app/utils/auth.py) - get_current_user dependency

### Key Learnings from Epic 2 to Apply

1. **Whitespace validation** - Strip and validate title not blank (from Story 2.1)
2. **Consistent error handling** - Use `ApiRequestError` pattern for 401/403/404 (from Story 2.2)
3. **TDD approach** - Write tests first, then implement (from Story 2.3)
4. **Authorization helper** - Create `get_project_or_404` helper to DRY up project ownership checks

### Epic 2 Retrospective Action Items Applied

1. **Delete operation edge cases** - Not applicable to this story (Story 3.4 will need this)
2. **Spec-driven + TDD approach** - Continue this methodology

## Dev Agent Record

### Agent Model Used

(To be filled by dev agent)

### Implementation Plan

(To be filled by dev agent)

### Completion Notes List

(To be filled by dev agent)

### File List

**To Create:**
- backend/app/models/task.py
- backend/app/schemas/task.py
- backend/app/routers/tasks.py
- backend/tests/api/test_tasks_api.py

**To Modify:**
- backend/app/models/__init__.py
- backend/app/models/project.py (add tasks relationship)
- backend/app/schemas/__init__.py
- backend/app/routers/__init__.py
- backend/app/main.py
- frontend/src/api/client.ts
- frontend/src/pages/ProjectDetail.tsx
- frontend/src/pages/ProjectDetail.test.tsx

### Change Log

(To be filled by dev agent)
