# Story 3.3: Toggle Task Status

Status: ready-for-dev

## Story

As a **user**,
I want to **mark tasks as complete or incomplete**,
So that **I can track my progress**.

## Acceptance Criteria

1. **Given** I have a task in my project **When** I click on the task's status indicator **Then** the task toggles between complete and incomplete
2. **Given** I toggle a task's status **When** the API responds successfully **Then** the UI updates to reflect the new status
3. **Given** I have a completed task **Then** it displays with visual distinction (strikethrough, different color)
4. **Given** I have an incomplete task **Then** it displays normally without completion styling
5. **Given** I try to toggle a task in a project I don't own **Then** the API returns 403 Forbidden
6. **Given** I try to toggle a task that doesn't exist **Then** the API returns 404 Not Found
7. **Given** I am not authenticated **When** I try to toggle a task **Then** the API returns 401 Unauthorized
8. **Given** I try to toggle a task in a project that doesn't exist **Then** the API returns 404 Not Found

## Tasks / Subtasks

- [ ] **Task 1: Backend TaskStatusUpdate Schema** (AC: 1, 2)
  - [ ] Add `TaskStatusUpdate` schema to `backend/app/schemas/task.py`
  - [ ] Schema contains single field: `is_complete: bool`
  - [ ] Export from `backend/app/schemas/__init__.py`

- [ ] **Task 2: Backend PATCH Endpoint** (AC: 1, 2, 5, 6, 7, 8)
  - [ ] Add `PATCH /api/projects/{project_id}/tasks/{task_id}` endpoint to `backend/app/routers/tasks.py`
  - [ ] Use `get_current_user` dependency for authentication
  - [ ] Query project by ID, return 404 if not found
  - [ ] Check project ownership, return 403 if not owner
  - [ ] Query task by ID, return 404 if not found
  - [ ] Verify task belongs to project (extra safety check)
  - [ ] Update task `is_complete` and `updated_at` timestamp
  - [ ] Return updated task data with 200

- [ ] **Task 3: Backend Testing** (AC: 1, 2, 5, 6, 7, 8)
  - [ ] Add tests to `backend/tests/api/test_tasks_api.py`
  - [ ] Test: PATCH /projects/{pid}/tasks/{tid} toggles is_complete from false to true
  - [ ] Test: PATCH /projects/{pid}/tasks/{tid} toggles is_complete from true to false
  - [ ] Test: PATCH returns 404 for non-existent task
  - [ ] Test: PATCH returns 404 for non-existent project
  - [ ] Test: PATCH returns 403 for project not owned by user
  - [ ] Test: PATCH returns 401 for unauthenticated request
  - [ ] Test: PATCH returns 404 when task doesn't belong to specified project

- [ ] **Task 4: Frontend API Client** (AC: 1, 2)
  - [ ] Add `ToggleTaskStatusData` interface to `frontend/src/api/client.ts`
  - [ ] Add `toggleStatus(projectId: number, taskId: number, data: ToggleTaskStatusData)` method to `tasksApi`
  - [ ] Returns `ApiResponse<TaskData>`

- [ ] **Task 5: Toggle UI for Tasks in ProjectDetail** (AC: 1, 2, 3, 4)
  - [ ] Update `frontend/src/pages/ProjectDetail.tsx`
  - [ ] Replace static status indicator with clickable checkbox/button
  - [ ] On click, call `tasksApi.toggleStatus()` with opposite of current status
  - [ ] Update local tasks state on successful toggle
  - [ ] Show loading state during toggle (disable checkbox)
  - [ ] Maintain visual distinction for completed tasks (strikethrough, gray text, green indicator)
  - [ ] Handle 403/404 errors gracefully with error message
  - [ ] Style with Tailwind CSS matching existing design

- [ ] **Task 6: Frontend Testing** (AC: 1, 2, 3, 4)
  - [ ] Update `frontend/src/pages/ProjectDetail.test.tsx`
  - [ ] Test: Clicking checkbox toggles task from incomplete to complete
  - [ ] Test: Clicking checkbox toggles task from complete to incomplete
  - [ ] Test: Completed tasks display with strikethrough styling
  - [ ] Test: Incomplete tasks display without strikethrough styling
  - [ ] Test: Toggle error shows error message

## Dev Notes

### Architecture Compliance

**Backend Structure:**
- Schema: `backend/app/schemas/task.py` (add TaskStatusUpdate)
- Endpoint: `backend/app/routers/tasks.py` (add PATCH endpoint)
- Tests: `backend/tests/api/test_tasks_api.py` (add toggle tests)

**Frontend Structure:**
- Page: `frontend/src/pages/ProjectDetail.tsx` (add toggle functionality)
- API: `frontend/src/api/client.ts` (add toggleStatus method)
- Tests: `frontend/src/pages/ProjectDetail.test.tsx` (add toggle tests)

### Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| Authentication | `get_current_user` dependency |
| Authorization | Verify project ownership via `project.user_id == current_user.id` |
| Nested Routes | `PATCH /api/projects/{project_id}/tasks/{task_id}` |
| HTTP Method | PATCH for partial resource update (only is_complete) |
| Timestamp | Auto-update `updated_at` on save |

### API Endpoint Spec

**PATCH /api/projects/{project_id}/tasks/{task_id}** (Protected)

Request Headers:
```
Authorization: Bearer <access_token>
```

Request Body:
```json
{
  "is_complete": true
}
```

Success Response (200):
```json
{
  "data": {
    "id": 1,
    "title": "My Task",
    "is_complete": true,
    "project_id": 1,
    "created_at": "2026-01-23T00:00:00Z",
    "updated_at": "2026-01-24T12:00:00Z"
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

### Component Specifications

**TaskStatusUpdate Schema:**
```python
class TaskStatusUpdate(BaseModel):
    is_complete: bool
```

**Backend PATCH Endpoint:**
```python
@router.patch("/{task_id}", response_model=TaskDataResponse)
async def toggle_task_status(
    project_id: int,
    task_id: int,
    task_data: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project_or_404(project_id, current_user, db)
    task = await db.scalar(
        select(Task).where(Task.id == task_id, Task.project_id == project.id)
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_complete = task_data.is_complete
    task.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    return TaskDataResponse(data=TaskResponse.model_validate(task))
```

**Frontend tasksApi toggleStatus:**
```typescript
export interface ToggleTaskStatusData {
  is_complete: boolean;
}

export const tasksApi = {
  list: (projectId: number) =>
    api.get<ApiResponse<TaskData[]>>(`/projects/${projectId}/tasks`),
  create: (projectId: number, data: CreateTaskData) =>
    api.post<ApiResponse<TaskData>>(`/projects/${projectId}/tasks`, data),
  update: (projectId: number, taskId: number, data: UpdateTaskData) =>
    api.put<ApiResponse<TaskData>>(
      `/projects/${projectId}/tasks/${taskId}`,
      data
    ),
  toggleStatus: (projectId: number, taskId: number, data: ToggleTaskStatusData) =>
    api.patch<ApiResponse<TaskData>>(
      `/projects/${projectId}/tasks/${taskId}`,
      data
    ),
};
```

**Note:** You will need to add a `patch` method to the `api` object:
```typescript
export const api = {
  // ... existing methods ...
  patch: <T>(endpoint: string, data: unknown) =>
    request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
};
```

**ProjectDetail.tsx Toggle Pattern:**
```tsx
// Add to existing state
const [togglingTaskId, setTogglingTaskId] = useState<number | null>(null);

const handleToggleTask = async (task: TaskData) => {
  setTogglingTaskId(task.id);
  try {
    const response = await tasksApi.toggleStatus(project!.id, task.id, {
      is_complete: !task.is_complete,
    });
    setTasks(tasks.map(t => t.id === task.id ? response.data : t));
  } catch (err) {
    if (err instanceof ApiRequestError) {
      if (err.status === 401) {
        logout();
        return;
      }
      if (err.status === 403) {
        setTaskError('You do not have permission to update this task.');
        return;
      }
      if (err.status === 404) {
        setTaskError('Task not found.');
        return;
      }
    }
    setTaskError(err instanceof Error ? err.message : 'Failed to update task');
  } finally {
    setTogglingTaskId(null);
  }
};

// In render - Task item with clickable checkbox:
{tasks.map((task) => (
  <li key={task.id} className="flex items-center gap-3 rounded-md border border-gray-200 px-4 py-3">
    {editingTaskId === task.id ? (
      // ... existing edit mode UI ...
    ) : (
      <>
        <button
          onClick={() => handleToggleTask(task)}
          disabled={togglingTaskId === task.id}
          className="flex h-5 w-5 items-center justify-center rounded border border-gray-300 hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          aria-label={task.is_complete ? 'Mark as incomplete' : 'Mark as complete'}
        >
          {task.is_complete && (
            <svg className="h-4 w-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          )}
        </button>
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
```

### References

**Planning Documents:**
- [PRD: FR13](../planning-artifacts/prd.md)
- [Architecture: Task Structure](../planning-artifacts/architecture.md)
- [Epics: Story 3.3](../planning-artifacts/epics.md#Story-3.3-Toggle-Task-Status)

**Source: Story 3.1 & 3.2 Implementation (Follow These!)**
- [backend/app/routers/tasks.py](../../backend/app/routers/tasks.py) - Add PATCH endpoint here
- [backend/app/schemas/task.py](../../backend/app/schemas/task.py) - Add TaskStatusUpdate schema here
- [backend/tests/api/test_tasks_api.py](../../backend/tests/api/test_tasks_api.py) - Add toggle tests here
- [frontend/src/api/client.ts](../../frontend/src/api/client.ts) - Add toggleStatus method and patch helper here
- [frontend/src/pages/ProjectDetail.tsx](../../frontend/src/pages/ProjectDetail.tsx) - Add toggle UI here

**Source: Story 2.3 Patterns (Edit Project)**
- Same error handling pattern (401 logout, 403/404 show error)
- Loading state pattern for async operations

### Key Learnings from Previous Stories to Apply

1. **Consistent error handling** - Use `ApiRequestError` pattern for 401/403/404 (from Story 3.1, 3.2)
2. **TDD approach** - Write tests first, then implement (from Story 2.3)
3. **Loading state management** - Track which item is being toggled to disable during request (from Story 3.2 edit pattern)
4. **Reuse `get_project_or_404`** - Already exists in tasks.py router
5. **Timestamp update** - Always update `updated_at` when modifying task (from Story 3.2)

### Epic 2 Retrospective Action Items Applied

1. **Spec-driven + TDD approach** - Continue this methodology
2. **Clear separation of concerns** - PATCH for status toggle vs PUT for title update

## Dev Agent Record

### Agent Model Used

[To be filled by implementing agent]

### Implementation Plan

1. Add TaskStatusUpdate schema with is_complete boolean field.
2. Add PATCH endpoint with auth/ownership checks and status update behavior.
3. Add backend API tests for toggle scenarios (success + error cases).
4. Add patch helper to frontend api object.
5. Add toggleStatus method to tasksApi.
6. Implement task toggle UI with checkbox and loading state.
7. Add frontend tests for toggle flows; run full test suite.

### Completion Notes List

[To be filled by implementing agent]

### File List

**To Modify:**
- backend/app/schemas/task.py (add TaskStatusUpdate)
- backend/app/schemas/__init__.py (export TaskStatusUpdate)
- backend/app/routers/tasks.py (add PATCH endpoint)
- backend/tests/api/test_tasks_api.py (add toggle tests)
- frontend/src/api/client.ts (add patch helper and toggleStatus method)
- frontend/src/pages/ProjectDetail.tsx (add toggle UI)
- frontend/src/pages/ProjectDetail.test.tsx (add toggle tests)

### Change Log

- 2026-01-24: Story created with ready-for-dev status.
