# Story 3.2: Edit Task

Status: review

## Story

As a **user**,
I want to **edit a task's title**,
So that **I can update task details**.

## Acceptance Criteria

1. **Given** I have a task in my project **When** I click an "Edit" button on the task **Then** I can edit the task title inline
2. **Given** I am editing a task title **When** I submit a valid new title **Then** the change is persisted and the UI updates
3. **Given** I am editing a task title **When** I submit an empty title **Then** I see a validation error
4. **Given** I try to edit a task in a project I don't own **Then** the API returns 403 Forbidden
5. **Given** I try to edit a task that doesn't exist **Then** the API returns 404 Not Found
6. **Given** I am not authenticated **When** I try to edit a task **Then** the API returns 401 Unauthorized
7. **Given** I am editing **When** I click "Cancel" **Then** the edit is discarded and the original title is shown
8. **Given** I try to edit a task in a project that doesn't exist **Then** the API returns 404 Not Found

## Tasks / Subtasks

- [x] **Task 1: Backend TaskUpdate Schema** (AC: 2, 3)
  - [x] Add `TaskUpdate` schema to `backend/app/schemas/task.py`
  - [x] Use same validation as `TaskCreate` (title: str, min_length=1, max_length=200, strip whitespace)
  - [x] Export from `backend/app/schemas/__init__.py`

- [x] **Task 2: Backend PUT Endpoint** (AC: 2, 3, 4, 5, 6, 8)
  - [x] Add `PUT /api/projects/{project_id}/tasks/{task_id}` endpoint to `backend/app/routers/tasks.py`
  - [x] Use `get_current_user` dependency for authentication
  - [x] Query project by ID, return 404 if not found
  - [x] Check project ownership, return 403 if not owner
  - [x] Query task by ID, return 404 if not found
  - [x] Verify task belongs to project (extra safety check)
  - [x] Update task title and `updated_at` timestamp
  - [x] Return updated task data with 200

- [x] **Task 3: Backend Testing** (AC: 2, 3, 4, 5, 6, 8)
  - [x] Add tests to `backend/tests/api/test_tasks_api.py`
  - [x] Test: PUT /projects/{pid}/tasks/{tid} updates title and returns updated task
  - [x] Test: PUT with empty title returns 422
  - [x] Test: PUT with whitespace-only title returns 422
  - [x] Test: PUT returns 404 for non-existent task
  - [x] Test: PUT returns 404 for non-existent project
  - [x] Test: PUT returns 403 for project not owned by user
  - [x] Test: PUT returns 401 for unauthenticated request
  - [x] Test: PUT trims whitespace from title

- [x] **Task 4: Frontend API Client** (AC: 2)
  - [x] Add `UpdateTaskData` interface to `frontend/src/api/client.ts`
  - [x] Add `update(projectId: number, taskId: number, data: UpdateTaskData)` method to `tasksApi`
  - [x] Returns `ApiResponse<TaskData>`

- [x] **Task 5: Edit UI for Tasks in ProjectDetail** (AC: 1, 2, 3, 7)
  - [x] Update `frontend/src/pages/ProjectDetail.tsx`
  - [x] Add edit mode state per task (track which task is being edited)
  - [x] Add "Edit" button on each task item
  - [x] Show input field with current title when in edit mode
  - [x] Add "Save" and "Cancel" buttons in edit mode
  - [x] Call `tasksApi.update()` on save
  - [x] Show validation error for empty title
  - [x] Update local tasks state on successful save
  - [x] Handle 403/404 errors gracefully
  - [x] Style with Tailwind CSS matching existing design

- [x] **Task 6: Frontend Testing** (AC: 1, 2, 3, 7)
  - [x] Update `frontend/src/pages/ProjectDetail.test.tsx`
  - [x] Test: Edit button on task toggles edit mode for that task
  - [x] Test: Save submits update and shows new title
  - [x] Test: Empty title shows validation error
  - [x] Test: Cancel discards changes and exits edit mode
  - [ ] Test: Only one task can be in edit mode at a time (optional UX improvement)

## Dev Notes

### Architecture Compliance

**Backend Structure:**
- Schema: `backend/app/schemas/task.py` (add TaskUpdate)
- Endpoint: `backend/app/routers/tasks.py` (add PUT endpoint)
- Tests: `backend/tests/api/test_tasks_api.py` (add update tests)

**Frontend Structure:**
- Page: `frontend/src/pages/ProjectDetail.tsx` (add task edit functionality)
- API: `frontend/src/api/client.ts` (add update method to tasksApi)
- Tests: `frontend/src/pages/ProjectDetail.test.tsx` (add task edit tests)

### Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| Authentication | `get_current_user` dependency |
| Authorization | Verify project ownership via `project.user_id == current_user.id` |
| Nested Routes | `PUT /api/projects/{project_id}/tasks/{task_id}` |
| Validation | Pydantic schema with min_length=1, max_length=200, strip whitespace |
| HTTP Method | PUT for full resource update |
| Timestamp | Auto-update `updated_at` on save |

### API Endpoint Spec

**PUT /api/projects/{project_id}/tasks/{task_id}** (Protected)

Request Headers:
```
Authorization: Bearer <access_token>
```

Request Body:
```json
{
  "title": "Updated Task Title"
}
```

Success Response (200):
```json
{
  "data": {
    "id": 1,
    "title": "Updated Task Title",
    "is_complete": false,
    "project_id": 1,
    "created_at": "2026-01-23T00:00:00Z",
    "updated_at": "2026-01-23T12:00:00Z"
  }
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

Error Response (404 - task not found):
```json
{
  "detail": "Task not found"
}
```

Validation Error (422 - empty title):
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

**TaskUpdate Schema:**
```python
class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title", mode="before")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Task title must be a string")
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Task title cannot be blank")
        return trimmed
```

**Backend PUT Endpoint:**
```python
@router.put("/{task_id}", response_model=TaskDataResponse)
async def update_task(
    project_id: int,
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project_or_404(project_id, current_user, db)
    task = await db.scalar(
        select(Task).where(Task.id == task_id, Task.project_id == project.id)
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = task_data.title
    await db.commit()
    await db.refresh(task)
    return TaskDataResponse(data=TaskResponse.model_validate(task))
```

**Frontend tasksApi update:**
```typescript
export interface UpdateTaskData {
  title: string;
}

export const tasksApi = {
  list: (projectId: number) =>
    api.get<ApiResponse<TaskData[]>>(`/projects/${projectId}/tasks`),
  create: (projectId: number, data: CreateTaskData) =>
    api.post<ApiResponse<TaskData>>(`/projects/${projectId}/tasks`, data),
  update: (projectId: number, taskId: number, data: UpdateTaskData) =>
    api.put<ApiResponse<TaskData>>(`/projects/${projectId}/tasks/${taskId}`, data),
};
```

**ProjectDetail.tsx Task Edit Mode Pattern:**
```tsx
// Add to existing state
const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
const [editTaskTitle, setEditTaskTitle] = useState('');
const [editTaskError, setEditTaskError] = useState<string | null>(null);
const [savingTask, setSavingTask] = useState(false);

const handleEditTask = (task: TaskData) => {
  setEditingTaskId(task.id);
  setEditTaskTitle(task.title);
  setEditTaskError(null);
};

const handleCancelEditTask = () => {
  setEditingTaskId(null);
  setEditTaskTitle('');
  setEditTaskError(null);
};

const handleSaveTask = async (taskId: number) => {
  const trimmed = editTaskTitle.trim();
  if (!trimmed) {
    setEditTaskError('Task title is required.');
    return;
  }
  if (trimmed.length > 200) {
    setEditTaskError('Task title must be 200 characters or less.');
    return;
  }

  setSavingTask(true);
  try {
    const response = await tasksApi.update(project!.id, taskId, { title: trimmed });
    setTasks(tasks.map(t => t.id === taskId ? response.data : t));
    setEditingTaskId(null);
    setEditTaskTitle('');
    setEditTaskError(null);
  } catch (err) {
    if (err instanceof ApiRequestError) {
      if (err.status === 401) {
        logout();
        return;
      }
      if (err.status === 403) {
        setEditTaskError('You do not have permission to edit this task.');
        return;
      }
      if (err.status === 404) {
        setEditTaskError('Task not found.');
        return;
      }
      if (err.status === 422) {
        setEditTaskError('Invalid task title.');
        return;
      }
    }
    setEditTaskError(err instanceof Error ? err.message : 'Failed to update task');
  } finally {
    setSavingTask(false);
  }
};

// In render - Task item with edit mode:
{tasks.map((task) => (
  <li key={task.id} className="flex items-center gap-3 rounded-md border border-gray-200 px-4 py-3">
    {editingTaskId === task.id ? (
      <div className="flex flex-1 items-center gap-2">
        <input
          type="text"
          value={editTaskTitle}
          onChange={(e) => setEditTaskTitle(e.target.value)}
          className="flex-1 rounded-md border border-gray-300 px-2 py-1 text-sm"
          disabled={savingTask}
        />
        <button
          onClick={() => handleSaveTask(task.id)}
          disabled={savingTask}
          className="rounded-md bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          Save
        </button>
        <button
          onClick={handleCancelEditTask}
          disabled={savingTask}
          className="rounded-md border border-gray-300 px-3 py-1 text-sm text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    ) : (
      <>
        <span className={`h-4 w-4 rounded-full ${task.is_complete ? 'bg-green-500' : 'bg-gray-300'}`} />
        <span className={`flex-1 ${task.is_complete ? 'text-gray-500 line-through' : 'text-gray-900'}`}>
          {task.title}
        </span>
        <button
          onClick={() => handleEditTask(task)}
          className="text-sm text-blue-600 hover:underline"
        >
          Edit
        </button>
      </>
    )}
  </li>
))}
{editingTaskId && editTaskError && (
  <p className="mt-2 text-sm text-red-600">{editTaskError}</p>
)}
```

### References

**Planning Documents:**
- [PRD: FR12](../planning-artifacts/prd.md)
- [Architecture: Task Structure](../planning-artifacts/architecture.md)
- [Epics: Story 3.2](../planning-artifacts/epics.md#Story-3.2-Edit-Task)

**Source: Story 3.1 Implementation (Follow These!)**
- [backend/app/routers/tasks.py](../../backend/app/routers/tasks.py) - Add PUT endpoint here
- [backend/app/schemas/task.py](../../backend/app/schemas/task.py) - Add TaskUpdate schema here
- [backend/tests/api/test_tasks_api.py](../../backend/tests/api/test_tasks_api.py) - Add update tests here
- [frontend/src/api/client.ts](../../frontend/src/api/client.ts) - Add update method here
- [frontend/src/pages/ProjectDetail.tsx](../../frontend/src/pages/ProjectDetail.tsx) - Add task edit UI here

**Source: Story 2.3 Patterns (Edit Project)**
- Same edit mode pattern with Save/Cancel buttons
- Same validation approach (empty, whitespace, max length)
- Same error handling pattern (401 logout, 403/404 show error)

### Key Learnings from Previous Stories to Apply

1. **Whitespace validation** - Strip and validate title not blank (from Story 3.1)
2. **Consistent error handling** - Use `ApiRequestError` pattern for 401/403/404/422 (from Story 3.1)
3. **TDD approach** - Write tests first, then implement (from Story 2.3)
4. **Edit mode state** - Track which item is being edited, show input with Save/Cancel (from Story 2.3)
5. **Reuse `get_project_or_404`** - Already exists in tasks.py router

### Epic 2 Retrospective Action Items Applied

1. **Delete operation edge cases** - Not applicable to this story (Story 3.4 will need this)
2. **Spec-driven + TDD approach** - Continue this methodology

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Implementation Plan

1. Add TaskUpdate schema + unit tests for validation rules.
2. Add PUT endpoint with auth/ownership checks and update behavior.
3. Add backend API tests for update scenarios (success + error cases).
4. Add frontend API client update method.
5. Implement task inline edit UI with validation + error handling.
6. Add frontend tests for edit flows; run full test suite.

### Completion Notes List

- Added `TaskUpdate` schema with shared validation behavior and unit tests for update validation.
- Implemented task update endpoint with ownership checks and title trimming.
- Added API tests covering update success and error cases.
- Added task update API client, inline edit UI, and frontend edit tests.
- Resolved frontend lint issues in route guards and projects list.
- Added update error-state tests and backend cross-project update coverage.
- Tests run: `python -m unittest backend.tests.unit.test_task_schema`, `python -m unittest backend.tests.api.test_tasks_api`, `npm test -- --run src/pages/ProjectDetail.test.tsx`, `scripts/windows/run-backend-tests.ps1`, `scripts/windows/run-frontend-tests.ps1`, `npm run lint`, `python -m unittest backend.tests.api.test_tasks_api.TasksApiTests.test_update_task_returns_404_when_task_not_in_project`

### File List

**To Modify:**
- backend/app/schemas/task.py (add TaskUpdate)
- backend/app/schemas/__init__.py (export TaskUpdate)
- backend/app/routers/tasks.py (add PUT endpoint)
- backend/tests/api/test_tasks_api.py (add update tests)
- frontend/src/api/client.ts (add update method to tasksApi)
- frontend/src/pages/ProjectDetail.tsx (add task edit UI)
- frontend/src/pages/ProjectDetail.test.tsx (add task edit tests)

**Modified:**
- backend/app/schemas/task.py
- backend/app/schemas/__init__.py
- backend/tests/unit/test_task_schema.py
- backend/app/routers/tasks.py
- backend/tests/api/test_tasks_api.py
- frontend/src/api/client.ts
- frontend/src/components/ProtectedRoute.tsx
- frontend/src/components/PublicRoute.tsx
- frontend/src/pages/ProjectDetail.tsx
- frontend/src/pages/ProjectDetail.test.tsx
- frontend/src/pages/Projects.tsx

### Change Log

- 2026-01-23: Added TaskUpdate schema and validation unit tests.
- 2026-01-23: Added task update endpoint and API tests.
- 2026-01-23: Added task edit UI, API client update method, and frontend tests.
- 2026-01-23: Fixed frontend lint warnings in auth routes and projects list.
